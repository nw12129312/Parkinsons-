"""Dataset constants for the PADS (Parkinson's Disease Smartwatch) preprocessed files.

Layout taken from the dataset's own scripts (PhysioNet, v1.0.0):
  preprocessed/movement/{id:03d}_ml.bin  -> float32, shape (132, 976)
  132 channels = 11 tasks x 2 wrists x 2 sensors x 3 axes, ordered task -> wrist -> sensor -> axis
  Accelerometer channels have gravity removed (L1 trend filter); first 48 samples trimmed.
  preprocessed/file_list.csv -> one row per subject; `label`: 0 = healthy, 1 = Parkinson's, 2 = other disorders
"""

from itertools import product

# 20 s recordings were split into two halves ("...1", "...2"); steps LiftHold, PointFinger
# and TouchIndex were dropped by the dataset's preprocessing script.
TASKS = [
    "Relaxed1", "Relaxed2",            # step 1a: rest, eyes closed
    "RelaxedTask1", "RelaxedTask2",    # step 1b: rest while doing serial sevens
    "StretchHold",                     # step 3: arms held out (postural)
    "HoldWeight",                      # step 4: 1 kg weight in each hand (postural, loaded)
    "DrinkGlas",                       # step 6: mime drinking (kinetic)
    "CrossArms",                       # step 7: cross and extend arms (kinetic)
    "TouchNose",                       # step 9: finger-to-nose (kinetic)
    "Entrainment1", "Entrainment2",    # step 10: stamp feet to examiner's pace
]
WRISTS = ["LeftWrist", "RightWrist"]
SENSORS = ["Acceleration", "Rotation"]
AXES = ["X", "Y", "Z"]

# Order matches the loop in the dataset's plot_example_*_processed.py scripts.
CHANNELS = [
    f"{task}_{sensor}_{wrist}_{axis}"
    for task, wrist, sensor, axis in product(TASKS, WRISTS, SENSORS, AXES)
]
N_CHANNELS = len(CHANNELS)   # 132
N_SAMPLES = 976

# The dataset page documents 100 Hz. (A code comment in run_preprocessing.py calls the
# 48-sample trim "half a second", which would imply ~96 Hz; the difference barely moves
# band edges, but keep it in mind when reporting exact tremor frequencies.)
FS = 100.0

LABELS = {0: "Healthy", 1: "Parkinson's", 2: "Other movement disorder"}

# Binary comparisons from the original paper (Varghese et al., npj Parkinson's Disease 2024).
COMPARISONS = {
    "pd_vs_hc": {"positive": 1, "negative": 0},
    "pd_vs_dd": {"positive": 1, "negative": 2},
}
