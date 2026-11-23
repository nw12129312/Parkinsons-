# Questionnaire features vs untuned watch-only baseline (paired, identical CV splits)

Balanced accuracy in %, 5 seeds × 5 outer folds. Δ = new minus baseline on the same fold.

| comparison | model | feature set | baseline bAcc | new bAcc | Δ bAcc (95% CI over seeds) | folds improved | Wilcoxon p (folds) | new AUC | Δ AUC | new sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|
| pd_vs_dd | catboost | questionnaire only | 64.73 | 70.12 | +5.39 (+2.69, +8.09) | 19/25 | 0.003 | 76.2 | +2.6 | 70 / 70 |
| pd_vs_dd | catboost | watch + clinical + questionnaire | 64.73 | 70.47 | +5.74 (+4.18, +7.31) | 21/25 | 0.000 | 78.4 | +4.8 | 76 / 65 |
| pd_vs_dd | catboost | watch + questionnaire | 64.73 | 69.58 | +4.85 (+2.75, +6.96) | 19/25 | 0.002 | 77.7 | +4.0 | 74 / 66 |
| pd_vs_dd | logreg | questionnaire only | 70.70 | 69.27 | -1.43 (-2.96, +0.10) | 10/25 | 0.312 | 75.7 | -2.3 | 71 / 68 |
| pd_vs_dd | logreg | watch + clinical + questionnaire | 70.70 | 70.54 | -0.16 (-2.36, +2.04) | 12/25 | 0.932 | 80.1 | +2.1 | 76 / 65 |
| pd_vs_dd | logreg | watch + questionnaire | 70.70 | 71.36 | +0.67 (-1.91, +3.25) | 14/25 | 0.394 | 79.4 | +1.4 | 81 / 62 |
| pd_vs_dd | svm | questionnaire only | 66.34 | 69.78 | +3.44 (+1.73, +5.14) | 15/25 | 0.052 | 75.7 | +0.4 | 73 / 67 |
| pd_vs_dd | svm | watch + clinical + questionnaire | 66.34 | 70.96 | +4.62 (+0.15, +9.10) | 22/25 | 0.000 | 78.7 | +3.4 | 80 / 62 |
| pd_vs_dd | svm | watch + questionnaire | 66.34 | 68.59 | +2.25 (+1.72, +2.78) | 17/25 | 0.004 | 77.4 | +2.1 | 78 / 59 |
| pd_vs_hc | catboost | questionnaire only | 75.95 | 88.73 | +12.78 (+9.98, +15.58) | 24/25 | 0.000 | 94.3 | +3.6 | 88 / 90 |
| pd_vs_hc | catboost | watch + clinical + questionnaire | 75.95 | 90.02 | +14.07 (+12.26, +15.88) | 25/25 | 0.000 | 96.9 | +6.1 | 90 / 90 |
| pd_vs_hc | catboost | watch + questionnaire | 75.95 | 90.53 | +14.59 (+12.13, +17.04) | 24/25 | 0.000 | 97.0 | +6.2 | 91 / 90 |
| pd_vs_hc | logreg | questionnaire only | 82.07 | 86.87 | +4.79 (+3.20, +6.39) | 16/25 | 0.003 | 94.2 | +3.4 | 84 / 90 |
| pd_vs_hc | logreg | watch + clinical + questionnaire | 82.07 | 85.73 | +3.66 (+1.43, +5.88) | 17/25 | 0.001 | 94.2 | +3.4 | 86 / 86 |
| pd_vs_hc | logreg | watch + questionnaire | 82.07 | 85.79 | +3.72 (+2.57, +4.87) | 18/25 | 0.000 | 94.1 | +3.3 | 87 / 84 |
| pd_vs_hc | svm | questionnaire only | 80.81 | 86.99 | +6.19 (+2.45, +9.92) | 20/25 | 0.001 | 93.6 | +3.7 | 86 / 88 |
| pd_vs_hc | svm | watch + clinical + questionnaire | 80.81 | 85.09 | +4.29 (+0.41, +8.17) | 23/25 | 0.000 | 93.0 | +3.1 | 86 / 84 |
| pd_vs_hc | svm | watch + questionnaire | 80.81 | 84.41 | +3.60 (+2.27, +4.94) | 22/25 | 0.000 | 93.1 | +3.2 | 87 / 82 |
