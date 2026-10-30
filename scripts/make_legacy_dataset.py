"""Turn the clean Contoso CSVs into a realistic 'legacy enterprise' extract.

- Renames tables and columns to cryptic warehouse-style names (cst_full_nm, unt_net_prc, ...).
- Replaces some readable values with codes (gender M/F, store status A/C/R, working-day Y/N).
- Injects a few data-quality issues: duplicate sales lines and missing customer cities.

Outputs:
  data/legacy/*.csv              the dataset Claude and the audience work with
  answer_key/column_mapping.csv  legacy column -> original column, business meaning (hidden from Claude)
  answer_key/data_issues.md      what was injected, so the presenter can check it was found

Usage: python scripts/make_legacy_dataset.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
LEGACY = ROOT / "data" / "legacy"
KEY = ROOT / "answer_key"
SEED = 42
DUPLICATE_SALES_LINES = 40
MISSING_CITY_SHARE = 0.02

# (legacy table, source file, {source column: (legacy column, business meaning)})
TABLES = {
    "fct_sls_ln": ("sales", {
        "OrderKey": ("ord_id", "Order number (one order has several lines)"),
        "LineNumber": ("ln_nbr", "Line number within the order"),
        "OrderDate": ("ord_dt", "Order date"),
        "DeliveryDate": ("dlvr_dt", "Delivery date"),
        "CustomerKey": ("cst_id", "Customer key (FK to dim_cst)"),
        "StoreKey": ("str_id", "Store key (FK to dim_str)"),
        "ProductKey": ("prd_id", "Product key (FK to dim_prd)"),
        "Quantity": ("qty", "Units sold on the line"),
        "UnitPrice": ("unt_lst_prc", "List price per unit, in USD, before discount"),
        "NetPrice": ("unt_net_prc", "Net price per unit, in USD, after discount"),
        "UnitCost": ("unt_cst", "Cost per unit, in USD (note: 'cst' here means cost, not customer)"),
        "CurrencyCode": ("crncy_cd", "Currency the customer paid in"),
        "ExchangeRate": ("fx_rt", "Rate from USD to crncy_cd; multiply USD amounts to get local currency"),
    }),
    "dim_cst": ("customer", {
        "CustomerKey": ("cst_id", "Customer key"),
        "FullName": ("cst_full_nm", "Customer full name"),
        "Gender": ("gndr_cd", "Gender code (M/F)"),
        "Birthday": ("brth_dt", "Date of birth"),
        "City": ("cty_nm", "City"),
        "State": ("st_cd", "State / province code"),
        "Country": ("cntry_cd", "Country code (ISO-2)"),
        "CountryFull": ("cntry_nm", "Country name"),
        "Continent": ("cntnt_nm", "Continent"),
        "Occupation": ("ocptn_txt", "Occupation"),
    }),
    "dim_prd": ("product", {
        "ProductKey": ("prd_id", "Product key"),
        "ProductCode": ("prd_cd", "Product code"),
        "ProductName": ("prd_nm", "Product name"),
        "Manufacturer": ("mfr_nm", "Manufacturer"),
        "Brand": ("brnd_nm", "Brand"),
        "Color": ("clr_nm", "Colour"),
        "Cost": ("std_cst", "Standard cost per unit, USD (catalogue value, not the transactional cost)"),
        "Price": ("lst_prc", "Catalogue list price per unit, USD"),
        "CategoryName": ("cat_nm", "Product category"),
        "SubCategoryName": ("sub_cat_nm", "Product subcategory"),
    }),
    "dim_str": ("store", {
        "StoreKey": ("str_id", "Store key"),
        "StoreCode": ("str_cd", "Store code"),
        "CountryName": ("cntry_nm", "Store country"),
        "State": ("st_nm", "Store state / region"),
        "OpenDate": ("opn_dt", "Store opening date"),
        "CloseDate": ("cls_dt", "Store closing date (empty = still open)"),
        "Description": ("str_desc", "Store name"),
        "SquareMeters": ("flr_sz", "Floor size in square metres"),
        "Status": ("sts_cd", "Store status code: A = active, C = closed, R = restructured"),
    }),
    "dim_cal": ("date", {
        "Date": ("cal_dt", "Calendar date"),
        "Year": ("yr_nbr", "Calendar year"),
        "Quarter": ("qtr_cd", "Quarter (Q1-Q4)"),
        "MonthNumber": ("mth_nbr", "Month number (1-12)"),
        "Month": ("mth_nm", "Month name"),
        "YearMonthShort": ("yr_mth_txt", "Year-month label, e.g. 'Jan 2020'"),
        "YearMonthNumber": ("yr_mth_nbr", "Sortable year-month number (sort key for yr_mth_txt)"),
        "DayofWeek": ("dow_nm", "Day of week"),
        "WorkingDay": ("wrk_day_flg", "Working day flag (Y/N)"),
    }),
}


def prepare(source: str, df: pd.DataFrame) -> pd.DataFrame:
    """Source-specific value changes before renaming."""
    if source == "customer":
        df["FullName"] = df["GivenName"] + " " + df["Surname"]
        df["Gender"] = df["Gender"].map({"male": "M", "female": "F"})
    elif source == "store":
        df["Status"] = df["Status"].map({"Closed": "C", "Restructured": "R"}).fillna("A")
    elif source == "date":
        df["WorkingDay"] = df["WorkingDay"].map({1: "Y", 0: "N"})
    return df


def main() -> None:
    LEGACY.mkdir(parents=True, exist_ok=True)
    KEY.mkdir(parents=True, exist_ok=True)

    sales_customers = set(pd.read_csv(RAW / "sales.csv", usecols=["CustomerKey"])["CustomerKey"])
    mapping_rows = []

    for table, (source, columns) in TABLES.items():
        df = prepare(source, pd.read_csv(RAW / f"{source}.csv", keep_default_na=False, na_values=[""], low_memory=False))
        if source == "customer":
            # Keep only customers that bought something, so the file stays small.
            df = df[df["CustomerKey"].isin(sales_customers)]
        df = df[list(columns)].rename(columns={src: legacy for src, (legacy, _) in columns.items()})

        if table == "fct_sls_ln":
            dupes = df.sample(DUPLICATE_SALES_LINES, random_state=SEED)
            df = pd.concat([df, dupes]).sort_values(["ord_id", "ln_nbr"], kind="stable")
        if table == "dim_cst":
            df.loc[df.sample(frac=MISSING_CITY_SHARE, random_state=SEED).index, "cty_nm"] = None

        df.to_csv(LEGACY / f"{table}.csv", index=False)
        print(f"{table:12} {len(df):>8} rows  <- {source}.csv")
        for src, (legacy, meaning) in columns.items():
            mapping_rows.append({"table": table, "legacy_column": legacy, "source_column": src, "business_meaning": meaning})

    pd.DataFrame(mapping_rows).to_csv(KEY / "column_mapping.csv", index=False)
    (KEY / "data_issues.md").write_text(
        "# Injected data issues\n\n"
        f"- `fct_sls_ln`: {DUPLICATE_SALES_LINES} exact duplicate lines (same ord_id + ln_nbr). "
        "Correct totals must count each line once.\n"
        f"- `dim_cst`: ~{MISSING_CITY_SHARE:.0%} of customers have an empty `cty_nm`.\n"
        "- `dim_cal` covers 2015-2024, but sales stop on 2024-04-20: 2024 is a partial year.\n"
        "- Already in the source: trailing spaces in some text values (e.g. brand 'Contoso ', "
        "category 'Cameras and camcorders '). Trim them in Power Query.\n"
        "- `dim_str` has an 'Online' store (str_cd -1, str_id 999999) that is not a physical location.\n"
        "- `unt_cst` (unit cost) vs `cst_id` (customer): same abbreviation, different meaning.\n"
        "- All amounts are in USD; `fx_rt` converts to the customer's currency (`crncy_cd`).\n"
        "- `dim_prd.std_cst` / `lst_prc` are catalogue values; use the sales-line prices for revenue.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
