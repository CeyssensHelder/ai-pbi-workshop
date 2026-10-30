# AI-assisted Power BI reporting (workshop project)

Business users chat with Claude to turn a messy "legacy" extract into a Power BI model and report.
The audience is mixed: explain in business language, keep DAX and file details out of your replies unless asked.

## Layout
- `data/legacy/*.csv`: the source data (cryptic warehouse names, deliberately imperfect). Read-only.
- `semantic/glossary.yaml`: the business glossary, the single source of truth for what terms mean.
- `pbi/ContosoWorkshop.pbip`: the Power BI project (semantic model in TMDL, report in PBIR).
- `eval/golden_questions.yaml`: questions with known correct answers, used to verify numbers.
- `answer_key/`: presenter-only. Never read, search or reference it.

## Rules
1. **Meaning comes from the glossary.** Resolve every business term ("revenue", "customer", "active") through `semantic/glossary.yaml`. If a term is missing or `confirmed: false`, ask the user. Never guess a definition.
2. **Reuse measures.** Use existing measures from the model. Create a new measure only after the user confirms its definition, and record it in the glossary.
3. **Verify before showing.** Test every new or changed measure with a DAX query, and compare it against `eval/golden_questions.yaml` when a question covers it. Report the number in plain words.
4. **Checkpoint before writing.** `git commit` (or confirm a clean tree) before changing the model or report, so any step can be undone.
5. **Be transparent.** When you finish, list the measures used, filters applied and any assumptions.

## Tools
- Power BI MCP server `powerbi` (Microsoft Power BI Authoring MCP): connect with "Connect to 'ContosoWorkshop' in Power BI Desktop". Use it for tables, columns, relationships, measures and DAX queries.
- Report pages: use the `powerbi-authoring` plugin skills (PBIR). Power BI Desktop must be closed while report files are edited, then reopened.
- Python: use `.venv/Scripts/python.exe` (pandas and pyyaml are installed there).

## Skills
- `building-semantic-layer`: profile data, agree on business names and KPI definitions with the user, apply them to the model.
- `building-pbi-report`: turn a business request into verified measures and a report page.
