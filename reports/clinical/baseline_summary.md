# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 75.68 ± 5.84 | 75.68 ± 0.85 | 82.2 | 69.2 | 86.6 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 76.83 ± 5.66 | 76.83 ± 1.60 | 87.6 | 66.1 | 87.5 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 75.95 ± 4.55 | 75.95 ± 2.09 | 93.6 | 58.3 | 87.7 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 69.00 ± 4.16 | 69.00 ± 1.63 | 78.3 | 59.7 | 75.7 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 70.27 ± 5.13 | 70.27 ± 0.41 | 82.9 | 57.7 | 78.3 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 67.07 ± 4.45 | 67.07 ± 0.51 | 89.4 | 44.7 | 76.9 | 69.18 | 5 × 5 |
