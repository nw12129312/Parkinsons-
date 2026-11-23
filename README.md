# Telling Parkinson's apart from similar disorders with smartwatch data

Can two wrist-worn smartwatches distinguish Parkinson's disease (PD) from healthy controls (HC)
and from disorders that look like it (DD: essential tremor, atypical parkinsonism, multiple
sclerosis and other movement disorders)? This project uses the open **PADS** dataset
(469 participants, 11 movement tasks, an Apple Watch on each wrist) to reproduce the published
smartwatch baseline and test whether clinically motivated features improve on it.

## Results

Balanced accuracy (%), nested 5-fold cross-validation repeated over 5 seeds. Full write-up in
[RESULTS.md](RESULTS.md); fold-level tables in `reports/`.

| | PD vs HC | PD vs DD |
|---|---|---|
| Published, smartwatch only (Varghese et al. 2024) | 78.99 | 69.18 |
| **Reproduced baseline** (generic features, logistic regression) | **82.1** | **70.7** |
| + clinical tremor features | 82.5 | 70.9 |
| + decision-threshold tuning | 82.4 | 71.0 |
| + non-motor symptoms questionnaire | **90.5** | 71.4 |

- **The baseline reproduces** within about 3 points on both comparisons.
- **Clinical tremor features** (rest vs postural tremor, distraction effect, left/right asymmetry,
  frequency stability) match the baseline on PD vs DD with about a sixth as many features, but
  don't beat it.
- **Threshold tuning** fixes SVM and CatBoost collapsing toward the majority class (CatBoost's
  DD specificity rises from 39% to 61–67%).
- **The questionnaire** lifts PD vs HC to 90.5%. Caveat: participants answered it knowing their
  diagnosis, so part of that gain may reflect reporting rather than disease.
- **PD vs DD tops out at about 71%** across every feature set, model and threshold tried.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/download_data.sh
```

Only `data/raw/pads/preprocessed/` is needed (about 230 MB). If physionet.org is unreachable,
the same files are on the public S3 mirror:
`https://physionet-open.s3.amazonaws.com/parkinsons-disease-smartwatch/1.0.0/preprocessed/`

## Usage

```bash
python -m pads.build_tables --data-dir data/raw/pads --out data/interim   # tables + QC report
python -m pads.features --interim data/interim --out data/processed       # generic features
python -m pads.clinical                                                    # clinical features
python -m pads.questionnaire                                               # questionnaire features
python -m pads.baseline --models logreg --seeds 0                          # quick smoke test
python -m pads.baseline                                                    # full run: 3 models × 5 seeds
python -m pads.baseline --tune-threshold --features data/processed/<set>_features.parquet --out reports/tuned_<set>
python -m pads.compare --runs clinical=reports/clinical --out reports      # paired fold-by-fold comparison
```

A full run takes about 25 minutes per feature set on 4 cores, mostly CatBoost. Every metric is
balanced accuracy because the classes are imbalanced (276 PD, 79 HC, 114 DD). Each subject is one
row, so nobody appears in both train and test, and all feature sets use identical CV splits.

To check the pipeline without the real data:

```bash
python tests/make_synthetic.py /tmp/pads_synth
python -m pads.build_tables --data-dir /tmp/pads_synth --out /tmp/pads_out/interim
python -m pads.features --interim /tmp/pads_out/interim --out /tmp/pads_out/processed
python -m pads.baseline --features /tmp/pads_out/processed/features.parquet --out /tmp/pads_out/reports --models logreg --seeds 0
```

## Layout

```
pads/
  config.py         channel/task layout, sampling rate, label map
  io.py             readers for file_list.csv and *_ml.bin
  build_tables.py   Parquet tables + QC report
  features.py       generic per-channel features (baseline)
  baseline.py       nested-CV evaluation (--tune-threshold for inner-CV cut-off)
  clinical.py       clinically motivated tremor features
  questionnaire.py  non-motor symptoms questionnaire features
  compare.py        paired comparison of feature sets on identical splits
  report.py         Markdown table helper
reports/            results of every run
RESULTS.md          full write-up
```

## License and citation

PADS is CC BY-NC-SA 4.0 (non-commercial). Cite the dataset (Varghese et al., PhysioNet,
doi:10.13026/m0w9-zx22) and the paper: Varghese et al., *Machine Learning in the Parkinson's
disease smartwatch (PADS) dataset*, npj Parkinson's Disease 10, 9 (2024).

This is a research and learning project, not a diagnostic tool.
