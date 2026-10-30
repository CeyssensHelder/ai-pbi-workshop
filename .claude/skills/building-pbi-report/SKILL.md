---
name: building-pbi-report
description: Turns a business request into a Power BI report page. Clarifies the request, maps every business term to the glossary, reuses or creates verified DAX measures, checks numbers against the golden questions, then writes the page into the PBIP project. Use when a user asks for a report, dashboard, page, chart, KPI overview or "show me ..." view in Power BI.
---

# Building a Power BI report from a business request

The user describes what they want to know. You deliver a page whose numbers are verified and whose terms match the glossary.
**Clarify, verify, then build.** A good-looking page with a wrong number is worse than no page.

## Workflow

Copy this checklist and keep it updated:
```
- [ ] 1. Understand the request
- [ ] 2. Map terms to the glossary
- [ ] 3. Measures: reuse, or define and confirm
- [ ] 4. Verify the numbers
- [ ] 5. Design the page (agree on it)
- [ ] 6. Build the page
- [ ] 7. Hand over
```

**1. Understand.** Fill [references/request-checklist.md](references/request-checklist.md) from the request. Ask only for what's missing or ambiguous, in one batch of multiple-choice questions (AskUserQuestion, best guess first). Typical gaps: which period, which comparison, who reads it, which level of detail.

**2. Map terms.** Look up every business word in `semantic/glossary.yaml` (names, synonyms, `terms`).
- Found and `confirmed: true`: use it, and say which definition you used ("revenue = Net Sales, after discounts").
- Missing or unconfirmed: ask the user, then add it to the glossary in the format of `.claude/skills/building-semantic-layer/references/glossary-schema.md`. For bigger gaps, switch to the building-semantic-layer skill.

**3. Measures.** List the measures in the model (MCP `powerbi`, measure list) and reuse them. For a new measure (e.g. "Net Sales YoY %"): explain it in one plain sentence, get a yes, commit to git, create it in `_Measures` with a description and format, and add it to the glossary.

**4. Verify.** Run a DAX query for every measure on the page, at the grain the page shows (e.g. by year and category). Check the matching entries in `eval/golden_questions.yaml`. Sanity-check the result too: no blanks where data should exist, shares add up to 100%, the partial year is flagged. Fix any mismatch before building.

**5. Design.** Propose the layout in words (or a small ASCII sketch) using [references/visual-guidelines.md](references/visual-guidelines.md). Get a quick OK. One page answers one question.

**6. Build.**
- Ask the user to save and close Power BI Desktop, and commit to git.
- Create the page in `pbi/ContosoWorkshop.Report/` using the `powerbi-authoring` plugin's report skills (PBIR format). Bind visuals to measures and business-named columns only.
- Add a page title, a subtitle stating the period and filters, and a small "Definitions" text box listing the measures used.
- Ask the user to reopen `pbi/ContosoWorkshop.pbip` and confirm that the page renders.

**7. Hand over.** Summarise in plain language: what the page shows, the key numbers you verified, which definitions you used, and any assumptions or open questions.

## Rules
- Never put a number in your reply that you didn't get from a DAX query or a golden answer.
- Never use hidden raw columns (prices, keys) directly in visuals. Use measures.
- Never read `answer_key/`.
- If a visual fails to render after reopening, read the error, fix the PBIR JSON, and ask the user to reopen again. After two failed attempts, propose a simpler visual.
