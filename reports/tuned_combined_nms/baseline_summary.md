# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 85.73 ± 4.68 | 85.73 ± 2.59 | 85.9 | 85.6 | 94.2 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 85.09 ± 4.12 | 85.09 ± 1.37 | 85.9 | 84.3 | 93.0 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 90.02 ± 3.99 | 90.02 ± 1.04 | 90.4 | 89.6 | 96.9 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 70.54 ± 5.48 | 70.54 ± 2.20 | 76.4 | 64.6 | 80.1 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 70.96 ± 4.98 | 70.96 ± 2.49 | 79.5 | 62.4 | 78.7 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 70.47 ± 5.14 | 70.47 ± 0.83 | 75.6 | 65.4 | 78.4 | 69.18 | 5 × 5 |
