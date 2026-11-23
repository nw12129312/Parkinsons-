# Telling Parkinson's apart from similar disorders with smartwatch data

Can two wrist-worn smartwatches distinguish Parkinson's disease (PD) from disorders that look like it,
such as essential tremor, atypical parkinsonism and multiple sclerosis? This project uses the open
**PADS** dataset (469 participants, 11 neurologist-designed movement tasks, an Apple Watch on each
wrist) and tries to beat the published smartwatch-only baseline with clinically motivated features.

| Comparison | Published balanced accuracy (smartwatch only) |
|---|---|
| PD vs healthy controls (HC) | 78.99% |
| PD vs differential diagnoses (DD) | **69.18%** ← main target |

**Results so far:** see [RESULTS.md](RESULTS.md). The baseline reproduces (82.1% / 70.7%).
Clinical features, threshold tuning and the non-motor questionnaire lift PD vs HC to about 90%,
but PD vs DD stays at about 71%.

Source: Varghese et al., *Machine Learning in the Parkinson's disease smartwatch (PADS) dataset*,
npj Parkinson's Disease 10, 9 (2024).

---

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/download_data.sh            # ~1.4 GB into data/raw/pads
```

Only `data/raw/pads/preprocessed/` is needed (movement and questionnaire files, about 230 MB).
If physionet.org is unreachable, the same files are on the public S3 mirror over plain HTTPS:
`https://physionet-open.s3.amazonaws.com/parkinsons-disease-smartwatch/1.0.0/preprocessed/...`

## Weekend 1: data pipeline and QC

```bash
python -m pads.build_tables --data-dir data/raw/pads --out data/interim
```

Produces:
- `data/interim/subjects.parquet`: one row per participant (metadata, label, QC flags, `usable`)
- `data/interim/signals.parquet`: one row per participant × channel (132 channels, 976 samples each)
- `data/interim/qc_report.md`: class counts, conditions, excluded subjects, out-of-range channels

**Read the QC report before doing anything else.** Write down the class counts. PD vs DD is
imbalanced, which is why every metric here is *balanced* accuracy.

How the files are laid out (taken from the dataset's own scripts):
- `preprocessed/movement/{id:03d}_ml.bin`: float32, shape (132, 976). That's 11 tasks × 2 wrists ×
  2 sensors (accelerometer, gyroscope) × 3 axes. Gravity is already removed from the accelerometer,
  and the first 48 samples are trimmed.
- `preprocessed/file_list.csv`: `label` 0 = healthy, 1 = Parkinson's, 2 = other movement disorders.
- The channel order and names live in `pads/config.py`.

## Weekend 2: reproduce the baseline

```bash
python -m pads.features --interim data/interim --out data/processed
python -m pads.baseline --models logreg --seeds 0          # 1-minute smoke test
python -m pads.baseline                                    # full run: 3 models × 5 seeds
```

- **Features** (`pads/features.py`): 17 generic statistics per channel (amplitude, band powers,
  peak frequency, spectral entropy, ...), about 2,200 features per subject. This stands in for the
  paper's "spectral and amplitude statistics". It's deliberately *not* clinically tuned, so that
  weekend 3's features can be measured as an improvement.
- **Evaluation** (`pads/baseline.py`): the paper's protocol, an outer 5-fold CV for testing and an
  inner 5-fold grid search for hyperparameters, scored by balanced accuracy. Each subject is one row,
  so nobody appears in both train and test. The whole procedure is repeated over 5 seeds, because
  the paper reported fold-to-fold SDs of up to ~12 points.
- **Outputs**: `reports/baseline_folds.csv` (every fold) and `reports/baseline_summary.md` (table).

**What "reproduced" looks like:** within a few points of 79% (PD vs HC) and 69% (PD vs DD) for
the best model. If you're far above, suspect leakage. If you're far below, check the QC report and
class counts. Either way, note it in the write-up; an honest mismatch is fine.

**Runtime:** logistic regression and SVM take seconds. CatBoost takes the longest, since it's
nested CV × grid × seeds. It uses feature subsampling (`rsm=0.1`) to stay practical. Expect tens of
minutes for the full run on a laptop. Start with `--seeds 0` to check timing.

## Testing without the real data

```bash
python tests/make_synthetic.py /tmp/pads_synth
python -m pads.build_tables --data-dir /tmp/pads_synth --out /tmp/pads_out/interim
python -m pads.features --interim /tmp/pads_out/interim --out /tmp/pads_out/processed
python -m pads.baseline --features /tmp/pads_out/processed/features.parquet --out /tmp/pads_out/reports --models logreg --seeds 0
```

The synthetic data mimics the file layout and injects fake tremor effects. Its scores mean nothing
clinically; it only proves the pipeline runs.

## Project layout

```
pads/
  config.py        channel/task layout, sampling rate, label map
  io.py            readers for file_list.csv and *_ml.bin
  build_tables.py  weekend 1: Parquet tables + QC report
  features.py      weekend 2: generic per-channel features
  baseline.py      weekend 2: nested-CV baseline reproduction (--tune-threshold for inner-CV cut-off)
  clinical.py      weekend 3: clinically motivated tremor features
  questionnaire.py non-motor symptoms questionnaire features
  compare.py       paired fold-by-fold comparison of feature sets on identical splits
  report.py        Markdown table helper
reports/           results of every run (fold-level CSVs + summaries)
RESULTS.md         write-up
scripts/download_data.sh
tests/make_synthetic.py
```

## Weekend 3: clinical features (done, see RESULTS.md)

Implemented in `pads/clinical.py`, compared on the same CV splits with `pads/compare.py`:
- **Rest vs. postural tremor:** tremor-band power in `Relaxed*` vs. `StretchHold` / `HoldWeight`
- **Distraction effect:** `RelaxedTask*` (counting) vs. `Relaxed*`
- **Left/right asymmetry:** PD usually starts on one side
- **Tremor frequency stability**, and orientation-free vector-magnitude channels

## Data license and citation

PADS is CC BY-NC-SA 4.0 (non-commercial). Cite both the dataset
(Varghese et al., PhysioNet, doi:10.13026/m0w9-zx22) and the npj Parkinson's Disease paper above.
This project is for research and learning. It is not a diagnostic tool.
