# Glossary format (`semantic/glossary.yaml`)

One YAML file, five sections. Every entry Claude proposes starts as `confirmed: false`.
It becomes `true` only after the user explicitly agrees. `semantic/glossary.fallback.yaml` is a complete example.

```yaml
version: 1
model: ContosoWorkshop
updated: 2026-10-27

tables:
  - source: fct_sls_ln            # name in the raw data
    name: Sales                   # business name shown in Power BI
    description: One row per order line. Amounts in USD.
    grain: ord_id + ln_nbr
    columns:
      - source: unt_net_prc
        name: Net Price
        description: Selling price per unit after discount, in USD.
        synonyms: [selling price, discounted price]
        format: "$#,0.00"
        hidden: true              # hide raw inputs that only feed measures
        confidence: high          # Claude's confidence before confirmation: high | medium | low
        confirmed: true

relationships:
  - from: Sales[Customer Key]
    to: Customer[Customer Key]
    cardinality: many-to-one
    confirmed: true

measures:
  - name: Net Sales
    definition: Revenue after discounts, in USD; each order line counted once.
    dax: SUMX(Sales, Sales[Quantity] * Sales[Net Price])
    format: "$#,0"
    synonyms: [revenue, sales, turnover]
    owner: Finance                # who decides the definition
    confirmed: true

terms:                            # business words that are not a single column or measure
  - term: Active customer
    definition: A customer with at least one order in the selected period.
    implemented_by: Active Customers
    confirmed: true

data_quality:
  - issue: 40 duplicate sales lines (same ord_id + ln_nbr)
    decision: Remove duplicates in Power Query on ord_id + ln_nbr
    confirmed: true
```

## Naming rules
- Tables: singular business nouns (`Sales`, `Customer`, `Product`, `Store`, `Date`).
- Columns: Title Case words, no abbreviations (`Customer Name`, not `Cst Nm`).
- Keys: `<Table> Key`, hidden.
- Measures: what they count, unit-free (`Net Sales`, `Gross Margin %`, `Orders`). Kept in a `_Measures` table.
- Codes get a readable column or are decoded (`gndr_cd` M/F -> `Gender` Male/Female).

## Confidence guide
- **high**: the name and values make the meaning unambiguous (`cntry_nm` with values like "Germany").
- **medium**: likely, but a plausible alternative exists (`flr_sz`: square metres or square feet?).
- **low**: several meanings possible, or the abbreviation clashes (`cst` = customer or cost?), or currency/units are unclear.
Medium and low items always go to the user.
