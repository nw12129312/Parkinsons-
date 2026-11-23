# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 85.79 ± 4.59 | 85.79 ± 1.94 | 87.5 | 84.1 | 94.1 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 84.41 ± 4.77 | 84.41 ± 2.10 | 86.5 | 82.3 | 93.1 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 90.53 ± 4.22 | 90.53 ± 0.68 | 90.7 | 90.4 | 97.0 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 71.36 ± 4.42 | 71.36 ± 1.01 | 80.5 | 62.2 | 79.4 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 68.59 ± 4.74 | 68.59 ± 1.75 | 78.0 | 59.2 | 77.4 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 69.58 ± 5.40 | 69.58 ± 1.29 | 73.6 | 65.5 | 77.7 | 69.18 | 5 × 5 |
