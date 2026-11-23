"""Weekend 1: turn the raw preprocessed files into tidy Parquet tables plus a QC report.

Outputs (under --out, default ./data/interim):
  subjects.parquet  one row per participant (metadata + label + QC flags)
  signals.parquet   one row per participant x channel (132 per subject), signal as a list column
  qc_report.md      class counts, missing/bad files, flat or non-finite channels

Usage:
  python -m pads.build_tables --data-dir /path/to/pads --out data/interim
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import LABELS
from .report import md_table
from .io import channel_frame, load_file_list, load_movement, movement_path

FLAT_STD = 1e-6        # a channel this still is almost certainly a dropout
ACC_LIMIT_G = 16.0     # Apple Watch accelerometer range; beyond this is corrupt
GYRO_LIMIT = 35.0      # rad/s, generous ceiling for wrist rotation


def qc_signals(signals: np.ndarray, channel_meta: pd.DataFrame) -> dict:
    finite = np.isfinite(signals)
    std = np.where(finite, signals, 0).std(axis=1)
    is_acc = (channel_meta["sensor"] == "Acceleration").to_numpy()
    limit = np.where(is_acc, ACC_LIMIT_G, GYRO_LIMIT)
    over = (np.abs(np.nan_to_num(signals)) > limit[:, None]).any(axis=1)
    return {
        "n_nonfinite_values": int((~finite).sum()),
        "n_flat_channels": int((std < FLAT_STD).sum()),
        "n_out_of_range_channels": int(over.sum()),
    }


def build(data_dir: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    subjects = load_file_list(data_dir)
    if subjects["id"].duplicated().any():
        raise ValueError("Duplicate subject ids in file_list.csv")

    signal_tables, qc_rows = [], []
    for sid in subjects["id"]:
        row = {"id": sid, "has_movement": movement_path(data_dir, sid).exists()}
        if row["has_movement"]:
            try:
                x = load_movement(data_dir, sid)
            except ValueError as err:
                row.update(has_movement=False, load_error=str(err))
            else:
                ch = channel_frame(x)
                row.update(qc_signals(x, ch))
                ch.insert(0, "id", sid)
                signal_tables.append(ch)
        qc_rows.append(row)

    qc = pd.DataFrame(qc_rows)
    subjects = subjects.merge(qc, on="id", how="left")
    subjects["label_name"] = subjects["label"].map(LABELS)
    subjects["usable"] = (
        subjects["has_movement"]
        & subjects.get("n_nonfinite_values", 0).fillna(0).eq(0)
        & subjects.get("n_flat_channels", 0).fillna(0).lt(12)   # tolerate a few dead channels
    )

    signals = pd.concat(signal_tables, ignore_index=True)
    signals = signals.merge(subjects[["id", "label", "condition"]], on="id")
    signals["signal"] = signals["signal"].map(lambda a: a.astype(np.float32).tolist())

    subjects.to_parquet(out / "subjects.parquet", index=False)
    signals.to_parquet(out / "signals.parquet", index=False)
    (out / "qc_report.md").write_text(qc_report(subjects))
    print(f"Wrote {len(subjects)} subjects and {len(signals):,} channel rows to {out}")


def qc_report(subjects: pd.DataFrame) -> str:
    lines = ["# PADS data QC report", ""]
    lines += ["## Class counts", "", "| label | label name | subjects | usable |", "|---|---|---|---|"]
    for label, g in subjects.groupby("label"):
        lines.append(f"| {label} | {LABELS.get(label, '?')} | {len(g)} | {int(g['usable'].sum())} |")
    lines += ["", "## Conditions (text field)", "", "| condition | subjects |", "|---|---|"]
    for cond, n in subjects["condition"].value_counts().items():
        lines.append(f"| {cond} | {n} |")

    problems = subjects[~subjects["usable"]]
    lines += ["", f"## Subjects excluded ({len(problems)})", ""]
    if problems.empty:
        lines.append("None.")
    else:
        cols = [c for c in ["id", "condition", "has_movement", "load_error",
                            "n_nonfinite_values", "n_flat_channels"] if c in problems]
        lines.append(md_table(problems[cols]))

    flagged = subjects[subjects.get("n_out_of_range_channels", 0).fillna(0) > 0]
    lines += ["", f"## Subjects with out-of-range channels ({len(flagged)}) — kept, but check", ""]
    lines.append("None." if flagged.empty else
                 md_table(flagged[["id", "condition", "n_out_of_range_channels"]]))
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, required=True,
                   help="Folder containing the PADS 'preprocessed' directory")
    p.add_argument("--out", type=Path, default=Path("data/interim"))
    args = p.parse_args()
    build(args.data_dir, args.out)


if __name__ == "__main__":
    main()
