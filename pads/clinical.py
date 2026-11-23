"""Weekend 3: clinically motivated features, built to be compared against the generic baseline.

Everything is computed on orientation-free spectra: for each task x wrist x sensor, the Welch
power spectra of the X, Y and Z axes are summed (equal to the spectrum of the 3-D vector, so it
doesn't depend on how the watch sits on the wrist). The two halves of 20 s recordings
(Relaxed1/2, RelaxedTask1/2, Entrainment1/2) are averaged into one spectrum.

Feature families (README "Next" list):
  1. Rest vs postural tremor: tremor-band power at rest (Relaxed) minus posture (StretchHold,
     HoldWeight), in log units. PD tremor is classically strongest at rest; essential tremor
     is postural/kinetic.
  2. Distraction effect: RelaxedTask (serial sevens) minus Relaxed. PD rest tremor typically
     increases with mental load.
  3. Left/right asymmetry: |log power left - log power right| per task. PD usually starts on one side.
  4. Tremor frequency stability: SD of the dominant 3-12 Hz frequency across 2 s windows, plus
     how sharp the spectral peak is (peak / median power).
  5. Orientation-free summary per task x wrist x sensor (log band powers, peak frequency).

"Max" features take the more affected wrist (higher tremor-band power in that task), which
avoids needing to know the side of onset.

Output: clinical_features.parquet (id, label, condition + features), and
combined_features.parquet (baseline features + clinical features), both sorted by id so that
StratifiedKFold produces exactly the same splits as the baseline run.

Usage:
  python -m pads.clinical --interim data/interim --baseline data/processed/features.parquet --out data/processed
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal as sps

from .config import FS, SENSORS, WRISTS

TASK_GROUPS = {
    "Relaxed": ["Relaxed1", "Relaxed2"],
    "RelaxedTask": ["RelaxedTask1", "RelaxedTask2"],
    "StretchHold": ["StretchHold"],
    "HoldWeight": ["HoldWeight"],
    "DrinkGlas": ["DrinkGlas"],
    "CrossArms": ["CrossArms"],
    "TouchNose": ["TouchNose"],
    "Entrainment": ["Entrainment1", "Entrainment2"],
}
POSTURAL = ["StretchHold", "HoldWeight"]
BANDS = {"rest": (3.0, 7.0), "broad": (3.0, 12.0), "fast": (7.0, 12.0), "total": (0.5, 20.0)}
NPERSEG = 256
WIN, STEP, NFFT = 200, 100, 1024     # 2 s windows, 1 s step, zero-padded for finer peak frequency
EPS = 1e-12


def _band(f, p, lo, hi):
    m = (f >= lo) & (f < hi)
    return np.trapezoid(p[m], f[m])


def _vm_psd(xyz: np.ndarray):
    """Sum of per-axis Welch spectra = spectrum of the 3-D signal (orientation-free)."""
    f, p = sps.welch(xyz, fs=FS, nperseg=NPERSEG, detrend="constant", axis=-1)
    return f, p.sum(axis=0)


def _freq_stability(xyz_list: list[np.ndarray]) -> tuple[float, float]:
    """SD (Hz) of the dominant 3-12 Hz frequency across 2 s windows, and the share of windows
    whose dominant frequency is within 1 Hz of the median (higher = steadier oscillation)."""
    peaks = []
    for xyz in xyz_list:
        for start in range(0, xyz.shape[1] - WIN + 1, STEP):
            seg = xyz[:, start:start + WIN]
            f, p = sps.periodogram(seg, fs=FS, nfft=NFFT, window="hann", detrend="constant", axis=-1)
            p = p.sum(axis=0)
            m = (f >= 3.0) & (f <= 12.0)
            peaks.append(f[m][np.argmax(p[m])])
    peaks = np.asarray(peaks)
    return float(peaks.std()), float(np.mean(np.abs(peaks - np.median(peaks)) <= 1.0))


def subject_features(g: pd.DataFrame) -> dict:
    sig = {ch: np.asarray(s, dtype=np.float64) for ch, s in zip(g["channel"], g["signal"])}
    feats: dict[str, float] = {}
    logp: dict[tuple, float] = {}   # (group, wrist, sensor, band) -> log power

    for group, tasks in TASK_GROUPS.items():
        for wrist in WRISTS:
            for sensor in SENSORS:
                xyz_list = [np.stack([sig[f"{t}_{sensor}_{wrist}_{a}"] for a in "XYZ"]) for t in tasks]
                spectra = [_vm_psd(xyz) for xyz in xyz_list]
                f = spectra[0][0]
                p = np.mean([s[1] for s in spectra], axis=0)
                key = f"{group}_{sensor}_{wrist}"
                for band, (lo, hi) in BANDS.items():
                    lp = np.log(_band(f, p, lo, hi) + EPS)
                    logp[(group, wrist, sensor, band)] = lp
                    feats[f"vm_{key}__logpow_{band}"] = lp
                feats[f"vm_{key}__relpow_rest"] = np.exp(logp[(group, wrist, sensor, "rest")]
                                                         - logp[(group, wrist, sensor, "total")])
                m = (f >= 3.0) & (f <= 12.0)
                feats[f"vm_{key}__peak_freq"] = f[m][np.argmax(p[m])]
                feats[f"vm_{key}__peak_sharpness"] = np.log(p[m].max() / (np.median(p[m]) + EPS) + EPS)
                sd, steady = _freq_stability(xyz_list)
                feats[f"vm_{key}__freq_sd"] = sd
                feats[f"vm_{key}__freq_steady_share"] = steady

    for sensor in SENSORS:
        # More affected wrist = higher rest-band power at rest.
        rest_lp = {w: logp[("Relaxed", w, sensor, "rest")] for w in WRISTS}
        worst = max(rest_lp, key=rest_lp.get)

        for band in ("rest", "broad"):
            for wrist in WRISTS + ["max"]:
                w = worst if wrist == "max" else wrist
                rest = logp[("Relaxed", w, sensor, band)]
                post = np.mean([logp[(t, w, sensor, band)] for t in POSTURAL])
                task = logp[("RelaxedTask", w, sensor, band)]
                feats[f"clin_{sensor}_{wrist}__rest_minus_postural_{band}"] = rest - post
                feats[f"clin_{sensor}_{wrist}__distraction_{band}"] = task - rest
            # Max-over-wrists tremor power per task group (strongest side).
            for group in TASK_GROUPS:
                feats[f"clin_{sensor}_max__{group}_logpow_{band}"] = max(
                    logp[(group, w, sensor, band)] for w in WRISTS)

        for group in TASK_GROUPS:
            for band in ("rest", "fast", "total"):
                feats[f"clin_{sensor}__asym_{group}_{band}"] = abs(
                    logp[(group, "LeftWrist", sensor, band)] - logp[(group, "RightWrist", sensor, band)])
        # Does the same side dominate at rest and in posture? (1 = consistent side)
        post_lp = {w: np.mean([logp[(t, w, sensor, "broad")] for t in POSTURAL]) for w in WRISTS}
        feats[f"clin_{sensor}__same_side_rest_postural"] = float(max(post_lp, key=post_lp.get) == worst)
        feats[f"clin_{sensor}_max__rest_freq_sd"] = feats[f"vm_Relaxed_{sensor}_{worst}__freq_sd"]
        feats[f"clin_{sensor}_max__rest_peak_freq"] = feats[f"vm_Relaxed_{sensor}_{worst}__peak_freq"]
        feats[f"clin_{sensor}_max__rest_peak_sharpness"] = feats[f"vm_Relaxed_{sensor}_{worst}__peak_sharpness"]
    return feats


def build(signals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in signals.groupby("id", sort=True):
        row = {"id": sid, "label": g["label"].iat[0], "condition": g["condition"].iat[0]}
        row.update(subject_features(g))
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--interim", type=Path, default=Path("data/interim"))
    p.add_argument("--baseline", type=Path, default=Path("data/processed/features.parquet"))
    p.add_argument("--out", type=Path, default=Path("data/processed"))
    args = p.parse_args()

    subjects = pd.read_parquet(args.interim / "subjects.parquet")
    usable = set(subjects.loc[subjects["usable"], "id"])
    signals = pd.read_parquet(args.interim / "signals.parquet")
    clin = build(signals[signals["id"].isin(usable)])

    base = pd.read_parquet(args.baseline).sort_values("id").reset_index(drop=True)
    clin = clin.set_index("id").loc[base["id"]].reset_index()   # identical row order => identical CV splits
    assert (clin["label"].to_numpy() == base["label"].to_numpy()).all()
    combined = pd.concat([base, clin.drop(columns=["id", "label", "condition"])], axis=1)

    args.out.mkdir(parents=True, exist_ok=True)
    clin.to_parquet(args.out / "clinical_features.parquet", index=False)
    combined.to_parquet(args.out / "combined_features.parquet", index=False)
    print(f"Wrote {len(clin)} subjects: {clin.shape[1] - 3} clinical features, "
          f"{combined.shape[1] - 3:,} combined features")


if __name__ == "__main__":
    main()
