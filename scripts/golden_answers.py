"""Compute the expected answers to the workshop's golden questions, independently of Power BI.

Answers use the agreed business definitions (see semantic/glossary.fallback.yaml):
  Net Sales      = SUM(qty * unt_net_prc), USD, each sales line counted once (duplicates removed)
  Gross Sales    = SUM(qty * unt_lst_prc)
  Total Cost     = SUM(qty * unt_cst)
  Gross Margin % = (Net Sales - Total Cost) / Net Sales
  Discount %     = 1 - Net Sales / Gross Sales
  Orders         = DISTINCTCOUNT(ord_id)
  Active Customers (period) = customers with at least one order in the period

Each answer also records the 'naive' value (duplicates kept), which is what a model that skipped
the data-quality step would show.

Usage: python scripts/golden_answers.py   ->  eval/golden_questions.yaml
"""

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "data" / "legacy"
OUT = ROOT / "eval" / "golden_questions.yaml"
LAST_FULL_YEAR = 2023


def load(dedupe: bool) -> pd.DataFrame:
    sales = pd.read_csv(LEGACY / "fct_sls_ln.csv", parse_dates=["ord_dt"])
    if dedupe:
        sales = sales.drop_duplicates(["ord_id", "ln_nbr"])
    products = pd.read_csv(LEGACY / "dim_prd.csv")
    customers = pd.read_csv(LEGACY / "dim_cst.csv", keep_default_na=False, na_values=[""])
    stores = pd.read_csv(LEGACY / "dim_str.csv")
    # Some brand/category values carry trailing spaces ("Contoso "); a clean model trims them.
    for col in ("cat_nm", "brnd_nm"):
        products[col] = products[col].str.strip()
    sales = sales.merge(products[["prd_id", "cat_nm", "brnd_nm"]], on="prd_id")
    sales = sales.merge(customers[["cst_id", "cntnt_nm"]], on="cst_id")
    sales = sales.merge(stores[["str_id", "cntry_nm"]].rename(columns={"cntry_nm": "str_cntry_nm"}), on="str_id")
    sales["net"] = sales["qty"] * sales["unt_net_prc"]
    sales["gross"] = sales["qty"] * sales["unt_lst_prc"]
    sales["cost"] = sales["qty"] * sales["unt_cst"]
    sales["yr"] = sales["ord_dt"].dt.year
    return sales


def answers(s: pd.DataFrame) -> dict:
    y = s[s["yr"] == LAST_FULL_YEAR]
    by_cat = y.groupby("cat_nm")["net"].sum().sort_values(ascending=False)
    by_country = y.groupby("str_cntry_nm")["net"].sum().sort_values(ascending=False)
    by_continent = y.groupby("cntnt_nm")["net"].sum().sort_values(ascending=False)
    return {
        "net_sales_all_time": round(s["net"].sum(), 2),
        "net_sales_last_full_year": round(y["net"].sum(), 2),
        "gross_margin_pct_last_full_year": round((y["net"].sum() - y["cost"].sum()) / y["net"].sum(), 4),
        "discount_pct_last_full_year": round(1 - y["net"].sum() / y["gross"].sum(), 4),
        "orders_last_full_year": int(y["ord_id"].nunique()),
        "avg_order_value_last_full_year": round(y["net"].sum() / y["ord_id"].nunique(), 2),
        "active_customers_last_full_year": int(y["cst_id"].nunique()),
        "top_category_last_full_year": by_cat.index[0],
        "top_category_net_sales_last_full_year": round(by_cat.iloc[0], 2),
        "top_store_country_last_full_year": by_country.index[0],
        "top_customer_continent_last_full_year": by_continent.index[0],
        "units_sold_contoso_brand_last_full_year": int(y.loc[y["brnd_nm"] == "Contoso", "qty"].sum()),
    }


QUESTIONS = {
    "net_sales_all_time": "What are our total net sales (USD) across all years?",
    "net_sales_last_full_year": f"What were net sales in {LAST_FULL_YEAR}?",
    "gross_margin_pct_last_full_year": f"What was our gross margin % in {LAST_FULL_YEAR}?",
    "discount_pct_last_full_year": f"What was the average discount % in {LAST_FULL_YEAR}?",
    "orders_last_full_year": f"How many orders did we receive in {LAST_FULL_YEAR}?",
    "avg_order_value_last_full_year": f"What was the average order value in {LAST_FULL_YEAR}?",
    "active_customers_last_full_year": f"How many active customers did we have in {LAST_FULL_YEAR}?",
    "top_category_last_full_year": f"Which product category sold the most (net sales) in {LAST_FULL_YEAR}?",
    "top_category_net_sales_last_full_year": f"What were the net sales of that top category in {LAST_FULL_YEAR}?",
    "top_store_country_last_full_year": f"Which store country had the highest net sales in {LAST_FULL_YEAR}?",
    "top_customer_continent_last_full_year": f"Which customer continent bought the most in {LAST_FULL_YEAR}?",
    "units_sold_contoso_brand_last_full_year": f"How many Contoso-brand units did we sell in {LAST_FULL_YEAR}?",
}


def to_python(values: dict) -> dict:
    """numpy scalars -> plain Python, so yaml can write them."""
    return {k: v.item() if hasattr(v, "item") else v for k, v in values.items()}


def main() -> None:
    correct, naive = to_python(answers(load(dedupe=True))), to_python(answers(load(dedupe=False)))
    items = []
    for key, question in QUESTIONS.items():
        item = {"id": key, "question": question, "expected": correct[key]}
        if isinstance(correct[key], float):
            item["tolerance"] = 0.0005 if abs(correct[key]) < 1 else 0.01
        if naive[key] != correct[key]:
            item["naive_if_duplicates_kept"] = naive[key]
        items.append(item)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump({"last_full_year": LAST_FULL_YEAR, "questions": items}, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
