# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 75.52 ± 5.61 | 75.52 ± 1.11 | 79.8 | 71.2 | 86.6 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 77.33 ± 6.57 | 77.33 ± 1.16 | 79.5 | 75.2 | 87.5 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 78.37 ± 5.57 | 78.37 ± 2.02 | 80.8 | 75.9 | 87.7 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 68.61 ± 4.20 | 68.61 ± 1.47 | 74.1 | 63.2 | 75.7 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 70.95 ± 4.93 | 70.95 ± 0.67 | 76.3 | 65.6 | 78.3 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 68.36 ± 5.51 | 68.36 ± 2.89 | 69.7 | 67.1 | 76.9 | 69.18 | 5 × 5 |
