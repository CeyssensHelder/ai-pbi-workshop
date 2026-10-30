---
name: building-semantic-layer
description: Builds or extends the business glossary and semantic layer of a Power BI model. Profiles raw tables, proposes business names, descriptions, synonyms, relationships, data-quality fixes and base measures, confirms the uncertain ones with the user, writes semantic/glossary.yaml and applies it to the model through the Power BI MCP server. Use when the user wants raw or cryptic data made understandable, wants business terms mapped to columns, wants KPIs defined, or when a business term is missing from the glossary.
---

# Building the semantic layer

The goal is a model a business user can read, where every name and number means what the business thinks it means.
**Propose, confirm, then apply.** Never write a business definition the user hasn't agreed to.
The user is usually not technical: ask about meaning ("Is this price before or after discount?"), not about DAX.

## Workflow

Copy this checklist and keep it updated:
```
- [ ] 1. Profile the data
- [ ] 2. Draft the mapping
- [ ] 3. Confirm uncertain items with the user
- [ ] 4. Agree on KPI definitions
- [ ] 5. Write semantic/glossary.yaml
- [ ] 6. Apply to the model
- [ ] 7. Validate and report back
```

**1. Profile.** Run `.venv/Scripts/python.exe .claude/skills/building-semantic-layer/scripts/profile_data.py data/legacy`.
Note the grain, keys and foreign keys, code lists, duplicates, nulls, trailing spaces, sentinel values (-1, 999999, "Online") and the date coverage (is the last year complete?).
If `semantic/glossary.yaml` already exists, extend it. Don't redo confirmed entries.

**2. Draft.** For every table and column, propose a business name, a one-line description, synonyms, a format, whether it should be hidden, and a confidence level (see [references/glossary-schema.md](references/glossary-schema.md)). Also draft the relationships (star schema: facts many-to-one to dimensions, single direction) and the data-quality decisions.

**3. Confirm.** Show the user a short table of the **high-confidence** items to approve in bulk. Then ask about each **medium/low** item separately, as multiple-choice questions (AskUserQuestion, 3–4 per batch, your best guess first). Always ask about:
- abbreviations with two possible meanings (e.g. `cst` = customer or cost),
- currency and units of amounts,
- before/after discount, tax or returns,
- what each code value means,
- how to handle data-quality issues (remove duplicates? exclude the partial year?).

**4. KPIs.** Ask which KPIs the audience uses and how they define them, offering the common definitions as options: Net Sales, Gross Sales, Cost, Gross Margin %, Discount %, Orders, Average Order Value, Active Customers. Record the owner (who decides the definition).

**5. Write** `semantic/glossary.yaml` in the schema format. Mark only user-approved items `confirmed: true`. Show the user a plain-language summary (not the YAML).

**6. Apply** after the user says go, and after a git commit of the current state:
- Connect: "Connect to 'ContosoWorkshop' in Power BI Desktop" (MCP server `powerbi`).
- Use one transaction per batch of changes. Rename tables and columns, set descriptions, hide keys and raw inputs, set formats and sort-by columns (month name by month number).
- Apply data-quality fixes in the table's Power Query (partition): remove duplicates on the grain, trim text, decode codes.
- Create the relationships, and mark the Date table as a date table.
- Create a `_Measures` table, then each confirmed measure with its description and format.
- Refresh the changed tables.

**7. Validate.** For each measure, run a DAX query (all-time total plus the last full year). Compare against `eval/golden_questions.yaml` where an entry covers it. Report to the user in a small table of measure, value and status. If a number doesn't match, stop and investigate (duplicates? trimming? the wrong price column?) before going further.

## Rules
- Never read `answer_key/`.
- If the user is unsure about a definition, record it as `confirmed: false` with an `open_question` and move on. Don't invent one.
- Keep raw-data names out of user-facing text after step 5. Talk in business names.
- If the MCP server is unavailable, finish steps 1–5 and give the user the remaining steps.
