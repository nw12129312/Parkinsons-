"""Tiny Markdown helpers (avoids an extra dependency on `tabulate`)."""

import pandas as pd


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |")
    return "\n".join(out)
