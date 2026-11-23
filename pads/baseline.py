"""Weekend 2 (part 2): reproduce the paper's smartwatch-only baseline with nested cross-validation.

Protocol (matches Varghese et al., npj Parkinson's Disease 2024):
  - outer 5-fold stratified CV for testing, inner 5-fold grid search for hyperparameters
  - balanced accuracy as the main metric
  - one row per subject, so no subject can appear in both train and test
Added for rigor: the whole procedure is repeated over several random seeds, and results are
reported as mean +/- SD over all outer folds and over seed-level means.

Published smartwatch-only balanced accuracy to compare against:
  PD vs HC 78.99%   |   PD vs DD 69.18%

Usage:
  python -m pads.baseline --features data/processed/features.parquet --out reports
  python -m pads.baseline --models logreg --seeds 0      # quick smoke test
"""

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, recall_score, roc_auc_score
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .config import COMPARISONS
from .report import md_table

PAPER_SMARTWATCH_BACC = {"pd_vs_hc": 78.99, "pd_vs_dd": 69.18}
META_COLS = ["id", "label", "condition"]


def make_model(name: str, seed: int):
    """Return (estimator, param_grid, n_jobs for the grid search)."""
    if name == "logreg":
        est = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=5000)),
        ])
        return est, {"clf__C": [1e-3, 1e-2, 1e-1]}, -1
    if name == "svm":
        est = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", SVC(kernel="rbf", class_weight="balanced")),
        ])
        return est, {"clf__C": [0.1, 1, 10], "clf__gamma": ["scale", 1e-4]}, -1
    if name == "catboost":
        from catboost import CatBoostClassifier  # imported lazily: optional dependency
        est = CatBoostClassifier(
            iterations=300, auto_class_weights="Balanced", random_seed=seed,
            rsm=0.1,            # sample 10% of features per split: ~15x faster with ~2,000 features
            border_count=64,
            verbose=0, allow_writing_files=False, thread_count=-1,
        )
        return est, {"depth": [4, 6], "learning_rate": [0.03, 0.1]}, 1  # CatBoost is already multithreaded
    raise ValueError(f"Unknown model: {name}")


def scores_for_auc(model, X):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    return model.decision_function(X)


def tune_threshold(best_estimator, X, y, inner) -> float:
    """Pick the score cut-off that maximizes balanced accuracy on out-of-fold predictions from the
    inner CV (training data only, best hyperparameters already fixed). Uses the same score as
    scores_for_auc, so the default cut-off is 0.5 for probabilities and 0 for SVM margins."""
    method = "predict_proba" if hasattr(best_estimator, "predict_proba") else "decision_function"
    oof = cross_val_predict(clone(best_estimator), X, y, cv=inner, method=method)
    oof = oof[:, 1] if oof.ndim == 2 else oof
    cand = np.unique(oof)
    cand = (cand[:-1] + cand[1:]) / 2 if len(cand) > 1 else cand
    baccs = np.array([balanced_accuracy_score(y, (oof >= t).astype(int)) for t in cand])
    best = np.flatnonzero(baccs >= baccs.max() - 1e-9)
    return float(cand[best[len(best) // 2]])   # middle of the tied plateau


def run_comparison(df: pd.DataFrame, comparison: str, model_name: str, seeds: list[int],
                   tune: bool = False) -> pd.DataFrame:
    spec = COMPARISONS[comparison]
    sub = df[df["label"].isin([spec["positive"], spec["negative"]])]
    X = sub.drop(columns=META_COLS).replace([np.inf, -np.inf], np.nan).to_numpy(dtype=np.float64)
    y = (sub["label"] == spec["positive"]).astype(int).to_numpy()

    rows = []
    for seed in seeds:
        outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        for fold, (tr, te) in enumerate(outer.split(X, y)):
            est, grid, n_jobs = make_model(model_name, seed)
            inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
            search = GridSearchCV(est, grid, scoring="balanced_accuracy", cv=inner, n_jobs=n_jobs)
            t0 = time.time()
            search.fit(X[tr], y[tr])
            threshold = np.nan
            if tune:
                threshold = tune_threshold(search.best_estimator_, X[tr], y[tr], inner)
                pred = (scores_for_auc(search.best_estimator_, X[te]) >= threshold).astype(int)
            else:
                pred = search.predict(X[te])
            rows.append({
                "comparison": comparison, "model": model_name, "seed": seed, "fold": fold,
                "n_train": len(tr), "n_test": len(te),
                "balanced_accuracy": 100 * balanced_accuracy_score(y[te], pred),
                "sensitivity": 100 * recall_score(y[te], pred, pos_label=1),
                "specificity": 100 * recall_score(y[te], pred, pos_label=0),
                "roc_auc": 100 * roc_auc_score(y[te], scores_for_auc(search.best_estimator_, X[te])),
                "best_params": str(search.best_params_),
                "threshold": threshold,
                "fit_seconds": round(time.time() - t0, 1),
            })
            print(f"  {comparison} {model_name} seed={seed} fold={fold}: "
                  f"bAcc={rows[-1]['balanced_accuracy']:.1f}%  ({rows[-1]['fit_seconds']}s)")
    return pd.DataFrame(rows)


def summarize(folds: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (comp, model), g in folds.groupby(["comparison", "model"], sort=False):
        seed_means = g.groupby("seed")["balanced_accuracy"].mean()
        out.append({
            "comparison": comp,
            "model": model,
            "bAcc mean ± SD (all folds)": f"{g['balanced_accuracy'].mean():.2f} ± {g['balanced_accuracy'].std():.2f}",
            "bAcc mean ± SD (across seeds)": f"{seed_means.mean():.2f} ± {seed_means.std(ddof=1) if len(seed_means) > 1 else 0:.2f}",
            "sensitivity": f"{g['sensitivity'].mean():.1f}",
            "specificity": f"{g['specificity'].mean():.1f}",
            "ROC AUC": f"{g['roc_auc'].mean():.1f}",
            "paper bAcc (smartwatch only)": PAPER_SMARTWATCH_BACC[comp],
            "seeds × folds": f"{g['seed'].nunique()} × {g['fold'].nunique()}",
        })
    return pd.DataFrame(out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--features", type=Path, default=Path("data/processed/features.parquet"))
    p.add_argument("--out", type=Path, default=Path("reports"))
    p.add_argument("--models", nargs="+", default=["logreg", "svm", "catboost"],
                   choices=["logreg", "svm", "catboost"])
    p.add_argument("--comparisons", nargs="+", default=list(COMPARISONS), choices=list(COMPARISONS))
    p.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    p.add_argument("--tune-threshold", action="store_true",
                   help="Choose the decision cut-off by inner CV (maximizing balanced accuracy)")
    args = p.parse_args()

    df = pd.read_parquet(args.features)
    counts = df["label"].value_counts().sort_index().to_dict()
    print(f"Loaded {len(df)} subjects, {df.shape[1] - len(META_COLS):,} features; label counts {counts}")

    folds = pd.concat(
        [run_comparison(df, c, m, args.seeds, args.tune_threshold) for c in args.comparisons for m in args.models],
        ignore_index=True,
    )
    summary = summarize(folds)

    args.out.mkdir(parents=True, exist_ok=True)
    folds.to_csv(args.out / "baseline_folds.csv", index=False)
    (args.out / "baseline_summary.md").write_text(
        "# Baseline reproduction (smartwatch features only)\n\n"
        f"Subjects per label: {counts}  \n"
        "Nested CV: outer 5-fold (test) × inner 5-fold grid search; metric = balanced accuracy (%).\n\n"
        + md_table(summary) + "\n"
    )
    print("\n" + md_table(summary))
    print(f"\nWrote {args.out / 'baseline_folds.csv'} and {args.out / 'baseline_summary.md'}")


if __name__ == "__main__":
    main()
