# Weekend 3: clinical features vs baseline (paired, identical CV splits)

Balanced accuracy in %, 5 seeds × 5 outer folds. Δ = new minus baseline on the same fold.

| comparison | model | feature set | baseline bAcc | new bAcc | Δ bAcc (95% CI over seeds) | folds improved | Wilcoxon p (folds) | new AUC | Δ AUC | new sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|
| pd_vs_dd | catboost | clinical | 64.73 | 67.07 | +2.34 (+1.02, +3.67) | 17/25 | 0.009 | 76.9 | +3.3 | 89 / 45 |
| pd_vs_dd | catboost | combined | 64.73 | 66.68 | +1.95 (-0.67, +4.58) | 17/25 | 0.024 | 75.9 | +2.2 | 91 / 43 |
| pd_vs_dd | logreg | clinical | 70.70 | 69.00 | -1.70 (-4.69, +1.29) | 11/25 | 0.101 | 75.7 | -2.3 | 78 / 60 |
| pd_vs_dd | logreg | combined | 70.70 | 70.92 | +0.23 (-2.86, +3.31) | 10/25 | 0.726 | 78.7 | +0.7 | 84 / 58 |
| pd_vs_dd | svm | clinical | 66.34 | 70.27 | +3.93 (+1.77, +6.09) | 19/25 | 0.000 | 78.3 | +3.0 | 83 / 58 |
| pd_vs_dd | svm | combined | 66.34 | 67.39 | +1.05 (-0.74, +2.84) | 15/25 | 0.060 | 77.0 | +1.7 | 87 / 48 |
| pd_vs_hc | catboost | clinical | 75.95 | 75.95 | +0.00 (-2.89, +2.90) | 9/25 | 0.966 | 87.7 | -3.1 | 94 / 58 |
| pd_vs_hc | catboost | combined | 75.95 | 76.30 | +0.35 (-0.87, +1.57) | 11/25 | 0.773 | 91.0 | +0.2 | 95 / 57 |
| pd_vs_hc | logreg | clinical | 82.07 | 75.68 | -6.39 (-8.00, -4.79) | 3/25 | 0.000 | 86.6 | -4.2 | 82 / 69 |
| pd_vs_hc | logreg | combined | 82.07 | 82.49 | +0.41 (-1.01, +1.84) | 12/25 | 0.286 | 91.6 | +0.8 | 89 / 76 |
| pd_vs_hc | svm | clinical | 80.81 | 76.83 | -3.97 (-6.88, -1.06) | 7/25 | 0.012 | 87.5 | -2.4 | 88 / 66 |
| pd_vs_hc | svm | combined | 80.81 | 80.52 | -0.29 (-2.30, +1.73) | 14/25 | 0.637 | 90.7 | +0.8 | 82 / 80 |
