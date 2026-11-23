"""Write a small synthetic dataset in the exact PADS 'preprocessed' layout, for testing the pipeline.

The numbers it produces mean nothing clinically; it only proves the code runs end to end.
Injected effects (so a working pipeline should beat chance):
  Parkinson's: ~5 Hz tremor at rest, stronger during the counting task, mostly on one wrist
  Other disorders: ~7 Hz tremor when holding a posture
Usage: python tests/make_synthetic.py /tmp/pads_synth
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pads.config import CHANNELS, FS, N_SAMPLES  # noqa: E402

CONDITIONS = [("Healthy", 0, 60), ("Parkinson's", 1, 120), ("Essential Tremor", 2, 35),
              ("Atypical Parkinsonism", 2, 25)]


def main(out: Path) -> None:
    rng = np.random.default_rng(42)
    t = np.arange(N_SAMPLES) / FS
    (out / "preprocessed" / "movement").mkdir(parents=True, exist_ok=True)
    rows, sid = [], 1
    for condition, label, n in CONDITIONS:
        for _ in range(n):
            x = rng.normal(0, 0.01, size=(len(CHANNELS), N_SAMPLES))
            side = rng.choice(["LeftWrist", "RightWrist"])
            has_effect = rng.random() < 0.6   # not every patient shows tremor in a 10 s window
            for i, ch in enumerate(CHANNELS):
                task, sensor, wrist, _axis = ch.split("_")
                amp = 0.0
                if not has_effect:
                    pass
                elif label == 1 and task.startswith("Relaxed"):
                    amp = rng.uniform(0.0, 0.004) * (1.5 if "Task" in task else 1.0)
                    amp *= 1.0 if wrist == side else 0.3
                    freq = rng.normal(5.0, 0.5)
                elif label == 2 and task in ("StretchHold", "HoldWeight"):
                    amp, freq = rng.uniform(0.0, 0.004), rng.normal(7.0, 0.7)
                if amp:
                    x[i] += amp * np.sin(2 * np.pi * freq * t + rng.uniform(0, 2 * np.pi))
            x.astype(np.float32).tofile(out / "preprocessed" / "movement" / f"{sid:03d}_ml.bin")
            rows.append({"id": sid, "condition": condition, "label": label,
                         "age": int(rng.integers(45, 85)), "gender": rng.choice(["male", "female"])})
            sid += 1
    # One deliberately broken file to exercise the QC path.
    (out / "preprocessed" / "movement" / f"{sid:03d}_ml.bin").write_bytes(b"\x00" * 100)
    rows.append({"id": sid, "condition": "Healthy", "label": 0, "age": 60, "gender": "female"})
    pd.DataFrame(rows).to_csv(out / "preprocessed" / "file_list.csv", index=False)
    print(f"Wrote {len(rows)} synthetic subjects to {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/pads_synth"))
