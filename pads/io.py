"""Readers for the PADS preprocessed files."""

from pathlib import Path

import numpy as np
import pandas as pd

from .config import CHANNELS, N_CHANNELS, N_SAMPLES


def load_file_list(data_dir: str | Path) -> pd.DataFrame:
    """Subject-level metadata: one row per participant, with `id`, `condition`, `label`."""
    path = Path(data_dir) / "preprocessed" / "file_list.csv"
    df = pd.read_csv(path)
    missing = {"id", "condition", "label"} - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing expected columns: {sorted(missing)}")
    return df


def movement_path(data_dir: str | Path, subject_id: int) -> Path:
    return Path(data_dir) / "preprocessed" / "movement" / f"{int(subject_id):03d}_ml.bin"


def load_movement(data_dir: str | Path, subject_id: int) -> np.ndarray:
    """Return one subject's signals as a float32 array of shape (132, 976)."""
    path = movement_path(data_dir, subject_id)
    x = np.fromfile(path, dtype=np.float32)
    if x.size != N_CHANNELS * N_SAMPLES:
        raise ValueError(
            f"{path.name}: expected {N_CHANNELS * N_SAMPLES} values, got {x.size}"
        )
    return x.reshape(N_CHANNELS, N_SAMPLES)


def channel_frame(signals: np.ndarray) -> pd.DataFrame:
    """Split channel names into task / sensor / wrist / axis columns."""
    parts = [c.split("_") for c in CHANNELS]
    return pd.DataFrame(
        {
            "channel": CHANNELS,
            "task": [p[0] for p in parts],
            "sensor": [p[1] for p in parts],
            "wrist": [p[2] for p in parts],
            "axis": [p[3] for p in parts],
            "signal": list(signals),
        }
    )
