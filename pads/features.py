"""Weekend 2 (part 1): generic per-channel features, approximating the paper's baseline.

The original study used "hand-defined spectral and amplitude statistics" per channel. The exact
list isn't published in a reusable form, so this is a close, standard stand-in. Clinically
motivated features (rest/postural ratio, asymmetry, ...) come in weekend 3, so they can be
measured as an improvement over this baseline.

Output: features.parquet with one row per usable subject (id, label, condition + ~2,200 features).

Usage:
  python -m pads.features --interim data/interim --out data/processed
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal as sps
from scipy import stats

from .config import FS

BANDS = {          # Hz
    "low": (0.5, 3.0),      # voluntary movement / drift
    "tremor": (3.0, 7.0),   # typical parkinsonian rest-tremor range
    "fast": (7.0, 12.0),    # essential / physiological tremor range
    "high": (12.0, 20.0),
}
WELCH_NPERSEG = 256


def _channel_features(x: np.ndarray) -> dict:
    x = x.astype(np.float64)
    diff = np.diff(x)
    f, pxx = sps.welch(x, fs=FS, nperseg=WELCH_NPERSEG, detrend="constant")
    band_mask = (f >= 0.5) & (f <= 20.0)
    total = np.trapezoid(pxx[band_mask], f[band_mask]) + 1e-12

    feats = {
        "mean": x.mean(),
        "std": x.std(),
        "rms": np.sqrt(np.mean(x**2)),
        "range": np.ptp(x),
        "skew": stats.skew(x),
        "kurtosis": stats.kurtosis(x),
        "mean_abs_diff": np.abs(diff).mean(),
        "zero_cross_rate": np.mean(np.signbit(x[1:] - x.mean()) != np.signbit(x[:-1] - x.mean())),
        "log_total_power": np.log(total),
    }
    for name, (lo, hi) in BANDS.items():
        m = (f >= lo) & (f < hi)
        feats[f"rel_power_{name}"] = np.trapezoid(pxx[m], f[m]) / total

    tm = (f >= 3.0) & (f <= 12.0)
    peak = np.argmax(pxx[tm])
    feats["peak_freq_3_12"] = f[tm][peak]
    feats["peak_rel_power_3_12"] = pxx[tm][peak] / (pxx[tm].sum() + 1e-12)

    p = pxx[band_mask] / (pxx[band_mask].sum() + 1e-12)
    feats["spectral_entropy"] = -(p * np.log(p + 1e-12)).sum() / np.log(len(p))
    feats["spectral_centroid"] = (f[band_mask] * p).sum()
    return feats


def build_features(signals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in signals.groupby("id", sort=True):
        row = {"id": sid, "label": g["label"].iat[0], "condition": g["condition"].iat[0]}
        for ch, sig in zip(g["channel"], g["signal"]):
            for k, v in _channel_features(np.asarray(sig)).items():
                row[f"{ch}__{k}"] = v
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--interim", type=Path, default=Path("data/interim"))
    p.add_argument("--out", type=Path, default=Path("data/processed"))
    args = p.parse_args()

    subjects = pd.read_parquet(args.interim / "subjects.parquet")
    usable = set(subjects.loc[subjects["usable"], "id"])
    signals = pd.read_parquet(args.interim / "signals.parquet")
    signals = signals[signals["id"].isin(usable)]

    feats = build_features(signals)
    args.out.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(args.out / "features.parquet", index=False)
    n_feat = feats.shape[1] - 3
    print(f"Wrote {len(feats)} subjects x {n_feat:,} features to {args.out / 'features.parquet'}")


if __name__ == "__main__":
    main()
