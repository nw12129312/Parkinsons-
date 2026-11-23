# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 81.69 ± 5.63 | 81.69 ± 1.50 | 85.4 | 78.0 | 91.6 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 81.53 ± 6.21 | 81.53 ± 1.13 | 85.6 | 77.5 | 90.7 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 82.38 ± 5.16 | 82.38 ± 2.33 | 81.5 | 83.3 | 91.0 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 70.07 ± 4.93 | 70.07 ± 1.15 | 78.9 | 61.2 | 78.7 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 69.33 ± 4.73 | 69.33 ± 1.82 | 77.1 | 61.6 | 77.0 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 68.70 ± 3.61 | 68.70 ± 1.05 | 73.6 | 63.8 | 75.9 | 69.18 | 5 × 5 |
