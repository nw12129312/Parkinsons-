# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 82.49 ± 5.27 | 82.49 ± 0.97 | 88.8 | 76.2 | 91.6 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 80.52 ± 5.75 | 80.52 ± 2.10 | 81.5 | 79.5 | 90.7 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 76.30 ± 6.96 | 76.30 ± 1.41 | 95.3 | 57.3 | 91.0 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 70.92 ± 5.70 | 70.92 ± 1.18 | 84.0 | 57.9 | 78.7 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 67.39 ± 4.62 | 67.39 ± 1.12 | 86.7 | 48.0 | 77.0 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 66.68 ± 4.95 | 66.68 ± 2.20 | 90.6 | 42.8 | 75.9 | 69.18 | 5 × 5 |
