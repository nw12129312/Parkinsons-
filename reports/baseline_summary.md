# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 82.07 ± 5.42 | 82.07 ± 1.29 | 87.2 | 77.0 | 90.8 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 80.81 ± 5.75 | 80.81 ± 3.03 | 76.5 | 85.1 | 89.9 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 75.95 ± 5.74 | 75.95 ± 1.73 | 95.1 | 56.8 | 90.8 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 70.70 ± 5.47 | 70.70 ± 1.45 | 83.2 | 58.2 | 78.0 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 66.34 ± 4.47 | 66.34 ± 1.63 | 86.2 | 46.4 | 75.3 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 64.73 ± 5.03 | 64.73 ± 1.05 | 90.0 | 39.4 | 73.6 | 69.18 | 5 × 5 |
