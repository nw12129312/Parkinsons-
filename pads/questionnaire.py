"""Non-movement features: the 30-item Non-Motor Symptoms questionnaire (NMSQuest) in PADS.

preprocessed/questionnaire/{id:03d}_ml.bin holds 30 float32 values (0 = no, 1 = yes), in the
order of the raw questionnaire_response_*.json items (01 = dribbling of saliva, 02 = loss of
taste/smell, 05 = constipation, ... 30). Many of these (smell loss, constipation, REM sleep
behaviour signs, urinary urgency) are known prodromal / non-motor PD signs, which watch signals
can't see.

Demographics (age, age at diagnosis, sex) are deliberately NOT added: age at diagnosis is
filled in for healthy controls too, and age differs by group, so they'd blur what the
questionnaire itself contributes.

Outputs, all sorted by id so CV splits are identical to earlier runs:
  nms_features.parquet               questionnaire only (30 items + total score)
  baseline_nms_features.parquet      generic watch features + questionnaire
  combined_nms_features.parquet      generic + clinical watch features + questionnaire

Usage:
  python -m pads.questionnaire --data-dir data/raw/pads --processed data/processed
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

N_ITEMS = 30


def load_nms(data_dir: Path, ids) -> pd.DataFrame:
    rows = []
    for sid in ids:
        path = data_dir / "preprocessed" / "questionnaire" / f"{int(sid):03d}_ml.bin"
        x = np.fromfile(path, dtype=np.float32)
        if x.size != N_ITEMS:
            raise ValueError(f"{path.name}: expected {N_ITEMS} values, got {x.size}")
        row = {"id": sid, **{f"nms_{i + 1:02d}": float(v) for i, v in enumerate(x)}}
        row["nms_total"] = float(x.sum())
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, default=Path("data/raw/pads"))
    p.add_argument("--processed", type=Path, default=Path("data/processed"))
    args = p.parse_args()

    base = pd.read_parquet(args.processed / "features.parquet").sort_values("id").reset_index(drop=True)
    combined = pd.read_parquet(args.processed / "combined_features.parquet")
    assert (combined["id"].to_numpy() == base["id"].to_numpy()).all()
    nms = load_nms(args.data_dir, base["id"])
    nms_cols = nms.drop(columns="id")

    meta = base[["id", "label", "condition"]]
    pd.concat([meta, nms_cols], axis=1).to_parquet(args.processed / "nms_features.parquet", index=False)
    pd.concat([base, nms_cols], axis=1).to_parquet(args.processed / "baseline_nms_features.parquet", index=False)
    pd.concat([combined, nms_cols], axis=1).to_parquet(args.processed / "combined_nms_features.parquet", index=False)

    prev = pd.concat([meta, nms_cols], axis=1).groupby("label")[["nms_total"]].mean().round(1)
    print(f"Wrote questionnaire features for {len(nms)} subjects. Mean NMS total by label:\n{prev}")


if __name__ == "__main__":
    main()
