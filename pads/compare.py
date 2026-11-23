"""Weekend 3: paired comparison of feature sets against the baseline on identical CV splits.

Every feature set is run through pads.baseline with the same seeds and the same subject order,
so outer fold k of seed s holds exactly the same test subjects in every run. That lets us compare
fold by fold (paired), which is far more sensitive than comparing two means with ~5-point SDs.

Reported per comparison x model:
  - mean balanced accuracy of each feature set
  - mean paired difference vs baseline, with a 95% interval over the 5 seed-level means
  - how many of the 25 folds improved
  - a Wilcoxon signed-rank test over all 25 folds. Folds share training data, so the folds
    aren't independent: treat the p-value as a guide, not a strict test.

Usage:
  python -m pads.compare --baseline reports --runs clinical=reports/clinical combined=reports/combined --out reports
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .report import md_table

KEYS = ["comparison", "model", "seed", "fold"]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path / "baseline_folds.csv")


def compare(base: pd.DataFrame, runs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    out = []
    for name, run in runs.items():
        m = base.merge(run, on=KEYS, suffixes=("_base", "_new"))
        assert (m["n_test_base"] == m["n_test_new"]).all(), "fold sizes differ: splits not identical"
        for (comp, model), g in m.groupby(["comparison", "model"], sort=False):
            d = g["balanced_accuracy_new"] - g["balanced_accuracy_base"]
            seed_d = d.groupby(g["seed"]).mean()
            half = stats.t.ppf(0.975, len(seed_d) - 1) * seed_d.std(ddof=1) / np.sqrt(len(seed_d))
            p = stats.wilcoxon(d).pvalue if (d != 0).any() else 1.0
            out.append({
                "comparison": comp, "model": model, "feature set": name,
                "baseline bAcc": f"{g['balanced_accuracy_base'].mean():.2f}",
                "new bAcc": f"{g['balanced_accuracy_new'].mean():.2f}",
                "Δ bAcc (95% CI over seeds)": f"{seed_d.mean():+.2f} ({seed_d.mean() - half:+.2f}, {seed_d.mean() + half:+.2f})",
                "folds improved": f"{int((d > 0).sum())}/{len(d)}",
                "Wilcoxon p (folds)": f"{p:.3f}",
                "new AUC": f"{g['roc_auc_new'].mean():.1f}",
                "Δ AUC": f"{(g['roc_auc_new'] - g['roc_auc_base']).mean():+.1f}",
                "new sens / spec": f"{g['sensitivity_new'].mean():.0f} / {g['specificity_new'].mean():.0f}",
            })
    return pd.DataFrame(out).sort_values(["comparison", "model", "feature set"], kind="stable")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baseline", type=Path, default=Path("reports"))
    p.add_argument("--runs", nargs="+", required=True, help="name=path pairs")
    p.add_argument("--out", type=Path, default=Path("reports"))
    args = p.parse_args()

    runs = {kv.split("=", 1)[0]: load(Path(kv.split("=", 1)[1])) for kv in args.runs}
    table = compare(load(args.baseline), runs)
    text = ("# Weekend 3: clinical features vs baseline (paired, identical CV splits)\n\n"
            "Balanced accuracy in %, 5 seeds × 5 outer folds. Δ = new minus baseline on the same fold.\n\n"
            + md_table(table) + "\n")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "clinical_comparison.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
