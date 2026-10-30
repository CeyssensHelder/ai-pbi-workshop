# AI-assisted Power BI reporting: workshop kit

A 1-hour internal workshop showing how business users (finance, compliance, sales) can chat with Claude to turn messy data into a trustworthy Power BI report.

**Story:** a cryptic "legacy" extract (`cst_full_nm`, `unt_net_prc`, duplicates, trailing spaces)
→ Claude interviews the user to agree on what things mean (**semantic layer**)
→ Claude builds the model and measures and checks the numbers
→ Claude builds a report page from a plain-language request.

## What's in here
| Path | What |
|---|---|
| `workshop/runbook.md` | Agenda, exact prompts, fallbacks and talking points for the presenters |
| `.claude/skills/building-semantic-layer/` | Skill 1: profile the data → interview the user → glossary → apply to the model |
| `.claude/skills/building-pbi-report/` | Skill 2: business request → verified measures → report page |
| `semantic/glossary.fallback.yaml` | Complete, confirmed glossary (demo fallback, and an example of the target result) |
| `eval/golden_questions.yaml` | 12 business questions with independently computed answers |
| `scripts/` | Download Contoso, build the legacy extract, compute the golden answers |
| `answer_key/` | Presenter-only: the true column meanings and injected issues. Claude is blocked from reading it |
| `CLAUDE.md` | Project rules Claude follows (glossary first, verify numbers, commit before writing) |

## One-time setup (per presenter laptop)
1. **Install:** [Power BI Desktop](https://aka.ms/pbidesktop) (free), [Node.js](https://nodejs.org) LTS, Python 3.11+, Git, and the Claude desktop app (paid account).
2. **Power BI Desktop preview features:** File → Options → Preview features → enable *Power BI Project (.pbip) save option*, *Store semantic model using TMDL format* and *Store reports using enhanced metadata format (PBIR)*. Restart Desktop.
3. **Data:**
   ```bash
   python -m venv .venv
   .venv/Scripts/python.exe -m pip install -r requirements.txt
   .venv/Scripts/python.exe scripts/download_contoso.py 100k
   .venv/Scripts/python.exe scripts/make_legacy_dataset.py
   .venv/Scripts/python.exe scripts/golden_answers.py
   ```
4. **Starter Power BI project** (manual, about 5 minutes): in Power BI Desktop, *Get data → Text/CSV*, load the 5 files from `data/legacy/` **without changing anything**, then *File → Save as → Power BI Project* to `pbi/ContosoWorkshop.pbip`. Commit it: this is the reset point for every rehearsal.
5. **Claude:** open this folder in the Claude desktop app (Code tab) and trust the folder.
   - The Power BI MCP server (`.mcp.json` → `@microsoft/powerbi-modeling-mcp`) starts automatically. On first use you're asked to accept Microsoft's EULA. Read it and accept it yourself.
   - Install the Microsoft `powerbi-authoring` plugin when prompted (configured in `.claude/settings.json`; marketplace `microsoft/skills-for-fabric`). It provides the PBIR report-writing skills.
   - Check: ask Claude "Connect to 'ContosoWorkshop' in Power BI Desktop and list the tables."
6. **Optional, safe exploration:** add `"--readonly"` to the args in `.mcp.json` while you explore. The server can't change the model then.

## Reset between rehearsals
```bash
git checkout -- pbi semantic && git clean -fd pbi semantic
```
Then reopen `pbi/ContosoWorkshop.pbip`.

## Known limits (say these out loud in the workshop)
- The Microsoft MCP server is in **public preview**. It edits the model, not report pages.
- Report pages are written as PBIR files: Desktop has to be closed and reopened to see them, and layout often needs a manual touch-up.
- Whatever Claude queries is sent to Anthropic. That's fine for this synthetic data, but real data needs IT and compliance approval first.
- Sharing a report with colleagues through the Power BI Service needs Pro licences. This workshop stays in Desktop.

## Data source and licence
Contoso V2 sample data by SQLBI ([Contoso Data Generator](https://github.com/sql-bi/Contoso-Data-Generator-V2), MIT). It's downloaded by the scripts and isn't stored in this repo. All people and companies are fictitious.

This workshop kit is MIT-licensed (see `LICENSE`). Note that `answer_key/` is public: it's presenter material, not a secret.
