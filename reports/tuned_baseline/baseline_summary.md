# Baseline reproduction (smartwatch features only)

Subjects per label: {0: 79, 1: 276, 2: 114}  
Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).

| comparison | model | bAcc mean ± SD (all folds) | bAcc mean ± SD (across seeds) | sensitivity | specificity | ROC AUC | paper bAcc (smartwatch only) | seeds × folds |
|---|---|---|---|---|---|---|---|---|
| pd_vs_hc | logreg | 81.70 ± 4.91 | 81.70 ± 0.68 | 83.9 | 79.5 | 90.8 | 78.99 | 5 × 5 |
| pd_vs_hc | svm | 81.07 ± 4.77 | 81.07 ± 0.78 | 81.1 | 81.0 | 89.9 | 78.99 | 5 × 5 |
| pd_vs_hc | catboost | 81.68 ± 4.47 | 81.68 ± 1.62 | 81.6 | 81.8 | 90.8 | 78.99 | 5 × 5 |
| pd_vs_dd | logreg | 69.34 ± 5.32 | 69.34 ± 1.32 | 77.5 | 61.2 | 78.0 | 69.18 | 5 × 5 |
| pd_vs_dd | svm | 67.75 ± 4.91 | 67.75 ± 0.65 | 78.7 | 56.8 | 75.3 | 69.18 | 5 × 5 |
| pd_vs_dd | catboost | 67.20 ± 5.01 | 67.20 ± 2.14 | 73.5 | 60.9 | 73.6 | 69.18 | 5 × 5 |
