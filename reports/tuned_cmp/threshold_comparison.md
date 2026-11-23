# Threshold tuning vs untuned baseline (paired, identical CV splits)

Balanced accuracy in %, 5 seeds × 5 outer folds. Δ = new minus baseline on the same fold.

| comparison | model | feature set | baseline bAcc | new bAcc | Δ bAcc (95% CI over seeds) | folds improved | Wilcoxon p (folds) | new AUC | Δ AUC | new sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|
| pd_vs_dd | catboost | tuned baseline | 64.73 | 67.20 | +2.47 (+0.71, +4.24) | 19/25 | 0.016 | 73.6 | +0.0 | 74 / 61 |
| pd_vs_dd | catboost | tuned clinical | 64.73 | 68.36 | +3.63 (+0.69, +6.58) | 19/25 | 0.003 | 76.9 | +3.3 | 70 / 67 |
| pd_vs_dd | catboost | tuned combined | 64.73 | 68.70 | +3.97 (+3.02, +4.93) | 22/25 | 0.000 | 75.9 | +2.2 | 74 / 64 |
| pd_vs_dd | logreg | tuned baseline | 70.70 | 69.34 | -1.36 (-3.17, +0.45) | 5/25 | 0.032 | 78.0 | +0.0 | 78 / 61 |
| pd_vs_dd | logreg | tuned clinical | 70.70 | 68.61 | -2.09 (-4.29, +0.11) | 10/25 | 0.056 | 75.7 | -2.3 | 74 / 63 |
| pd_vs_dd | logreg | tuned combined | 70.70 | 70.07 | -0.63 (-3.32, +2.06) | 11/25 | 0.459 | 78.7 | +0.7 | 79 / 61 |
| pd_vs_dd | svm | tuned baseline | 66.34 | 67.75 | +1.41 (-0.56, +3.37) | 13/25 | 0.108 | 75.3 | +0.0 | 79 / 57 |
| pd_vs_dd | svm | tuned clinical | 66.34 | 70.95 | +4.61 (+1.84, +7.38) | 19/25 | 0.000 | 78.3 | +3.0 | 76 / 66 |
| pd_vs_dd | svm | tuned combined | 66.34 | 69.33 | +2.98 (-1.16, +7.13) | 13/25 | 0.059 | 77.0 | +1.7 | 77 / 62 |
| pd_vs_hc | catboost | tuned baseline | 75.95 | 81.68 | +5.74 (+5.26, +6.21) | 22/25 | 0.000 | 90.8 | +0.0 | 82 / 82 |
| pd_vs_hc | catboost | tuned clinical | 75.95 | 78.37 | +2.42 (-0.39, +5.23) | 16/25 | 0.080 | 87.7 | -3.1 | 81 / 76 |
| pd_vs_hc | catboost | tuned combined | 75.95 | 82.38 | +6.44 (+3.65, +9.23) | 20/25 | 0.000 | 91.0 | +0.2 | 81 / 83 |
| pd_vs_hc | logreg | tuned baseline | 82.07 | 81.70 | -0.37 (-1.56, +0.81) | 7/25 | 0.259 | 90.8 | +0.0 | 84 / 79 |
| pd_vs_hc | logreg | tuned clinical | 82.07 | 75.52 | -6.56 (-9.13, -3.98) | 0/25 | 0.000 | 86.6 | -4.2 | 80 / 71 |
| pd_vs_hc | logreg | tuned combined | 82.07 | 81.69 | -0.38 (-1.32, +0.56) | 9/25 | 0.520 | 91.6 | +0.8 | 85 / 78 |
| pd_vs_hc | svm | tuned baseline | 80.81 | 81.07 | +0.26 (-3.49, +4.02) | 10/25 | 0.841 | 89.9 | +0.0 | 81 / 81 |
| pd_vs_hc | svm | tuned clinical | 80.81 | 77.33 | -3.47 (-7.58, +0.63) | 10/25 | 0.034 | 87.5 | -2.4 | 79 / 75 |
| pd_vs_hc | svm | tuned combined | 80.81 | 81.53 | +0.73 (-3.09, +4.54) | 14/25 | 0.689 | 90.7 | +0.8 | 86 / 77 |
