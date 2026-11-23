# Results: Parkinson's vs similar disorders from smartwatch data (PADS)

All runs: 469 PADS participants, nested cross-validation (outer 5-fold for testing, inner 5-fold
grid search), repeated over 5 seeds, scored by **balanced accuracy (%)**. Every feature set was
run on the *same* subject order and seeds, so outer fold *k* of seed *s* holds the same test
subjects in every run. That allows paired, fold-by-fold comparisons (25 folds per comparison).
Full tables are in `reports/`.

This is a research and learning project, not a diagnostic tool.

## TL;DR

| | PD vs HC | PD vs DD |
|---|---|---|
| Published, smartwatch only (Varghese et al. 2024) | 78.99 | 69.18 |
| **Reproduced baseline**, generic watch features, logistic regression | **82.1** | **70.7** |
| + clinical tremor features | 82.5 | 70.9 |
| + decision-threshold tuning (best model) | 82.4 | 71.0 |
| + non-motor symptoms questionnaire (best model) | **90.5** | 71.4 |

- The published baseline reproduces within about 3 points on both comparisons.
- **PD vs DD tops out at about 71%** across every feature set, model and threshold tried here.
  None of the additions changed it by a statistically meaningful amount.
- **PD vs HC** goes up to about 90% once the 30-item non-motor symptoms questionnaire is added.

## 1. Data and QC (`pads/build_tables.py`)

| Group | Subjects | Usable |
|---|---|---|
| Healthy controls (HC) | 79 | 79 |
| Parkinson's disease (PD) | 276 | 276 |
| Differential diagnoses (DD) | 114 | 114 |

The DD group breaks down into 60 other movement disorders, 28 essential tremor, 15 atypical
parkinsonism and 11 multiple sclerosis. No files are broken, no channels are flat and none are
out of range. The counts match the paper. Only the `preprocessed/` folder is used (about 230 MB).

## 2. Baseline reproduction (`pads/features.py`, `pads/baseline.py`)

The baseline uses 2,244 generic per-channel statistics (17 per channel × 132 channels).
Results are mean ± SD across the 5 seed-level means.

| | Logistic regression | SVM | CatBoost | Paper |
|---|---|---|---|---|
| PD vs HC | **82.1 ± 1.3** | 80.8 ± 3.0 | 76.0 ± 1.7 | 78.99 |
| PD vs DD | **70.7 ± 1.5** | 66.3 ± 1.6 | 64.7 ± 1.1 | 69.18 |

Fold-to-fold SD is about 5 points, consistent with the paper's reported spread. SVM and CatBoost
label nearly everyone as PD: CatBoost's PD vs DD specificity is 39%, although its AUC is similar
to the other models. That points to the decision threshold, which section 4 addresses.

## 3. Clinical tremor features (`pads/clinical.py`)

This adds 400 features computed on orientation-free spectra (the sum of the X, Y and Z spectra
for each task × wrist × sensor):

- **Rest vs postural tremor:** tremor-band power at rest minus during posture (`StretchHold`, `HoldWeight`).
- **Distraction effect:** rest tremor while counting (`RelaxedTask`) minus plain rest.
- **Left/right asymmetry:** |log power left − log power right| per task.
- **Frequency stability:** SD of the dominant 3–12 Hz frequency across 2 s windows, plus how sharp the spectral peak is.
- **Features from the more affected wrist**, so the side of onset doesn't need to be known.

The features were defined once and not tuned against these results.

| PD vs DD | Baseline | Clinical only | Baseline + clinical |
|---|---|---|---|
| Logistic regression | **70.7** | 69.0 | **70.9** |
| SVM | 66.3 | 70.3 (+3.9, better on 19/25 folds) | 67.4 |
| CatBoost | 64.7 | 67.1 (+2.3) | 66.7 |

The 400 clinical features alone match the best 2,244-feature baseline on PD vs DD, and they lift
the weaker models. They don't beat the best baseline. On PD vs HC, clinical features alone are
worse (logistic regression drops from 82.1 to 75.7), and adding them to the baseline changes nothing.

## 4. Decision-threshold tuning (`pads/baseline.py --tune-threshold`)

After the inner grid search, the cut-off is chosen to maximize balanced accuracy on inner-CV
out-of-fold predictions. Only training folds are used, so the test folds stay untouched.

| PD vs DD, untuned → tuned | Baseline | Clinical only | Baseline + clinical |
|---|---|---|---|
| Logistic regression | 70.7 → 69.3 | 69.0 → 68.6 | 70.9 → 70.1 |
| SVM | 66.3 → 67.8 | 70.3 → **71.0** | 67.4 → 69.3 |
| CatBoost | 64.7 → 67.2 | 67.1 → 68.4 | 66.7 → 68.7 |

- DD specificity rises for every model. CatBoost goes from 39% to 61–67%, and SVM from 46% to 57–66%.
- Tuned CatBoost on PD vs HC rises from 76.0 to 81.7 with baseline features, and to 82.4 with baseline + clinical.
- Logistic regression was already near its best cut-off, so tuning costs it 1–2 points of estimation noise.

## 5. Non-motor symptoms questionnaire (`pads/questionnaire.py`)

PADS includes the 30-item yes/no NMSQuest (loss of smell, constipation, sleep, mood, and more).
On average, people with PD answer yes to 9.9 items, people with DD to 7.4, and HC to 2.5. Age
and sex are deliberately excluded, because age at diagnosis is filled in for HC too. All runs
here use threshold tuning.

| Best model | PD vs HC | PD vs DD |
|---|---|---|
| Questionnaire only (30 answers) | 88.7 (CatBoost) | 70.1 (CatBoost) |
| Watch + questionnaire | **90.5** (CatBoost, better on 24/25 folds vs baseline) | **71.4** (logistic regression, +0.7, not significant) |
| Watch + clinical + questionnaire | 90.0 | 71.0 |

**Caveat:** participants answered the questionnaire knowing their diagnosis, so some of the
PD vs HC gain may come from how they report symptoms rather than from the disease itself.

## Conclusions

1. The published smartwatch baseline is reproducible with simple generic features and logistic regression.
2. Telling PD apart from similar disorders appears capped at about 71% balanced accuracy with this
   data and sample size (276 vs 114). Clinical tremor features, threshold tuning and questionnaire
   answers each fall within noise of that number. The watch and the questionnaire seem to carry
   overlapping information about the PD vs DD difference.
3. Clinically motivated features offer the same PD vs DD performance with about a sixth as many,
   far more interpretable features. That's useful for explaining a model, even though it doesn't
   improve accuracy.
4. Threshold tuning is worth using for tree and kernel models under class imbalance: it fixes
   their collapse toward the majority class.

## Methods notes and limitations

- p-values in the comparison reports come from Wilcoxon tests over 25 folds. The folds share
  training data, so treat these p-values as a guide, not a strict test.
- The DD group mixes four different conditions (ET, atypical parkinsonism, MS and others). A
  per-condition analysis, such as PD vs ET alone, would be more clinically meaningful, but the
  subgroups are small (11–60 subjects).
- The sampling rate is assumed to be 100 Hz, as documented. A comment in the dataset's
  preprocessing script implies about 96 Hz, which would shift reported tremor frequencies by about 4%.

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
bash scripts/download_data.sh          # or download preprocessed/ from the PhysioNet S3 mirror (see README)
python -m pads.build_tables --data-dir data/raw/pads --out data/interim
python -m pads.features --interim data/interim --out data/processed
python -m pads.clinical
python -m pads.questionnaire
python -m pads.baseline --out reports                                     # untuned baseline
python -m pads.baseline --features data/processed/clinical_features.parquet --out reports/clinical
python -m pads.baseline --features data/processed/combined_features.parquet --out reports/combined
python -m pads.baseline --tune-threshold --features data/processed/<set>_features.parquet --out reports/tuned_<set>
python -m pads.compare --runs clinical=reports/clinical combined=reports/combined --out reports
```

A full run (3 models × 5 seeds) takes about 25 minutes per feature set on 4 CPU cores. Nearly all
of that is CatBoost.

## Citation and license

PADS: Varghese et al., PhysioNet, doi:10.13026/m0w9-zx22 (CC BY-NC-SA 4.0). Paper: Varghese et
al., *Machine Learning in the Parkinson's disease smartwatch (PADS) dataset*, npj Parkinson's
Disease 10, 9 (2024).
