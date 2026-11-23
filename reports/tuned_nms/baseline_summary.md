# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 86.87 ± 4.27 | 86.87 ± 1.05 | 83.9 | 89.8 | 94.2 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 86.99 ± 5.42 | 86.99 ± 1.44 | 85.9 | 88.1 | 93.6 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 88.73 ± 4.36 | 88.73 ± 1.01 | 87.6 | 89.9 | 94.3 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 69.27 ± 4.86 | 69.27 ± 1.18 | 70.7 | 67.9 | 75.7 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 69.78 ± 5.12 | 69.78 ± 1.63 | 72.7 | 66.9 | 75.7 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 70.12 ± 5.03 | 70.12 ± 1.38 | 70.1 | 70.2 | 76.2 | 69.18 | 5 × 5 |
