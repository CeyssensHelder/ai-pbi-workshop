# Injected data issues

- `fct_sls_ln`: 40 exact duplicate lines (same ord_id + ln_nbr). Correct totals must count each line once.
- `dim_cst`: ~2% of customers have an empty `cty_nm`.
- `dim_cal` covers 2015-2024, but sales stop on 2024-04-20: 2024 is a partial year.
- Already in the source: trailing spaces in some text values (e.g. brand 'Contoso ', category 'Cameras and camcorders '). Trim them in Power Query.
- `dim_str` has an 'Online' store (str_cd -1, str_id 999999) that is not a physical location.
- `unt_cst` (unit cost) vs `cst_id` (customer): same abbreviation, different meaning.
- All amounts are in USD; `fx_rt` converts to the customer's currency (`crncy_cd`).
- `dim_prd.std_cst` / `lst_prc` are catalogue values; use the sales-line prices for revenue.
