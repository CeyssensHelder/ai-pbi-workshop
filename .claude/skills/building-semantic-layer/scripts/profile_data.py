"""Profile a folder of CSV files and print a Markdown report for the semantic-layer interview.

Per table: row count, duplicate rows, duplicate candidate keys.
Per column: type, null %, distinct count, min/max or sample values, key / foreign-key hints.

Usage: python profile_data.py <folder-with-csvs> [--samples 5]
"""

import argparse
from pathlib import Path

import pandas as pd


def load(folder: Path) -> dict[str, pd.DataFrame]:
    return {
        f.stem: pd.read_csv(f, keep_default_na=False, na_values=[""], low_memory=False)
        for f in sorted(folder.glob("*.csv"))
    }


def kind(s: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(s):
        return "bool"
    if pd.api.types.is_integer_dtype(s):
        return "int"
    if pd.api.types.is_float_dtype(s):
        return "decimal"
    parsed = pd.to_datetime(s.dropna().head(200), errors="coerce", format="ISO8601")
    if len(parsed) and parsed.notna().all():
        return "date"
    return "text"


def column_hints(table: str, col: str, s: pd.Series, tables: dict[str, pd.DataFrame]) -> list[str]:
    hints = []
    if s.notna().all() and s.is_unique:
        hints.append("unique (candidate key)")
    if col.endswith(("_id", "_key", "_cd")) or col.lower().endswith("key"):
        values = set(s.dropna().unique())
        for other, df in tables.items():
            if other == table or col not in df.columns or not df[col].is_unique:
                continue
            missing = len(values - set(df[col].dropna()))
            hints.append(f"FK -> {other}.{col}" + (f" ({missing} values not found)" if missing else ""))
    if 1 < s.nunique() <= 5 and kind(s) == "text":
        hints.append("looks like a code list")
    if kind(s) == "text" and (s.dropna().astype(str) != s.dropna().astype(str).str.strip()).any():
        hints.append("leading/trailing spaces in some values")
    return hints


def grain(df: pd.DataFrame) -> tuple[str, ...] | None:
    """Smallest combination of the 1-2 leading columns that is unique once full duplicates are dropped."""
    deduped = df.drop_duplicates()
    cols = list(df.columns[:3])
    for combo in [(c,) for c in cols] + [(a, b) for i, a in enumerate(cols) for b in cols[i + 1:]]:
        if not deduped.duplicated(list(combo)).any():
            return combo
    return None


def num(x) -> str:
    return f"{x:,}" if abs(x) >= 10_000 else f"{x}"


def describe(s: pd.Series, k: str, samples: int) -> str:
    v = s.dropna()
    if v.empty:
        return "all empty"
    if k in ("int", "decimal"):
        return f"min {num(v.min())} / max {num(v.max())}"
    if k == "date":
        return f"{v.min()} .. {v.max()}"
    top = v.value_counts().head(samples).index.astype(str)
    return ", ".join(top)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("folder", type=Path)
    p.add_argument("--samples", type=int, default=5)
    args = p.parse_args()

    tables = load(args.folder)
    print(f"# Data profile: {args.folder}\n")
    for name, df in tables.items():
        print(f"## {name}  ({len(df):,} rows, {df.shape[1]} columns)\n")
        full_dupes = int(df.duplicated().sum())
        if full_dupes:
            print(f"- WARNING: {full_dupes} fully duplicated rows")
        g = grain(df)
        if g:
            print(f"- Grain: one row per ({', '.join(g)})" + (" once duplicates are removed" if full_dupes else ""))
        else:
            print("- Grain: no unique key among the leading columns")
        print("\n| column | type | null % | distinct | values | hints |\n|---|---|---|---|---|---|")
        for col in df.columns:
            s = df[col]
            k = kind(s)
            hints = "; ".join(column_hints(name, col, s, tables))
            print(f"| {col} | {k} | {s.isna().mean():.1%} | {s.nunique():,} | {describe(s, k, args.samples)} | {hints} |")
        print()


if __name__ == "__main__":
    main()
