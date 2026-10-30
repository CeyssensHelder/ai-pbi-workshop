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
All commands are for **PowerShell on Windows**. They use `winget`, which is built into Windows 10/11. Skip any tool you already have (check with the version command under each one).

1. **Install the tools.** Run each command, then close and reopen PowerShell so the new tools are found.

   | Tool | Install | Check |
   |---|---|---|
   | Git | `winget install --id Git.Git -e` | `git --version` |
   | Python 3.12 | `winget install --id Python.Python.3.12 -e` | `python --version` (3.11 or newer) |
   | Node.js LTS (runs the Power BI MCP server) | `winget install --id OpenJS.NodeJS.LTS -e` | `node --version` and `npx --version` |
   | Power BI Desktop (free) | `winget install --id Microsoft.PowerBI -e` | Start menu → *Power BI Desktop* |
   | Claude desktop app (paid account) | `winget install --id Anthropic.Claude -e` | Start menu → *Claude*, then sign in |

   - **Power BI Desktop:** if your company manages software through the Microsoft Store, use `winget install --id 9NTXR16HNW1T --source msstore` instead. Either version works.
   - **Anaconda users:** a `(base)` prompt means conda's Python comes first on your PATH. That's fine: step 4 creates a separate `.venv` anyway.

2. **Get the project:**
   ```powershell
   cd $HOME\Documents
   git clone https://github.com/CeyssensHelder/ai-pbi-workshop.git "AI in Business Reporting"
   cd "AI in Business Reporting"
   ```
3. **Power BI Desktop version:** nothing to enable. Since Microsoft made developer mode generally available (rolled out in September 2026), Power BI Project (.pbip), TMDL and the PBIR report format are standard in Desktop. Just make sure Desktop is up to date (`winget upgrade --id Microsoft.PowerBI -e`, or via the Store).
   - On an older build that has no *Power BI Project (\*.pbip)* type under *File → Save as*: update Desktop, or enable the PBIP, TMDL and PBIR options under *File → Options → Preview features* and restart.
4. **Data** (about 1 minute; downloads ~9 MB from SQLBI):
   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe scripts\download_contoso.py 100k
   .venv\Scripts\python.exe scripts\make_legacy_dataset.py
   .venv\Scripts\python.exe scripts\golden_answers.py
   ```
   Check: `data\legacy\` should contain 5 CSV files.
5. **Starter Power BI project** (manual, about 5 minutes): in Power BI Desktop, *Get data → Text/CSV*, load the 5 files from `data/legacy/` **without changing anything**, then *File → Save as → Power BI Project* to `pbi/ContosoWorkshop.pbip`. Commit it: this is the reset point for every rehearsal.
   ```powershell
   git add pbi
   git commit -m "Starter Power BI project"
   ```
6. **Claude:** open this folder in the Claude desktop app (Code tab) and trust the folder.
   - The Power BI MCP server (`.mcp.json` → `@microsoft/powerbi-modeling-mcp`) starts automatically. On first use you're asked to accept Microsoft's EULA. Read it and accept it yourself.
   - Install the Microsoft `powerbi-authoring` plugin when prompted (configured in `.claude/settings.json`; marketplace `microsoft/skills-for-fabric`). It provides the PBIR report-writing skills.
   - Check: ask Claude "Connect to 'ContosoWorkshop' in Power BI Desktop and list the tables."
7. **Optional, safe exploration:** add `"--readonly"` to the args in `.mcp.json` while you explore. The server can't change the model then.

## Reset between rehearsals
Close Power BI Desktop first, then:
```powershell
git checkout -- pbi semantic
git clean -fd pbi semantic
```
Then reopen `pbi/ContosoWorkshop.pbip`.

## Known limits
- The Microsoft MCP server is in **public preview**. It edits the model, not report pages.
- Report pages are written as PBIR files: Desktop has to be closed and reopened to see them, and layout often needs a manual touch-up.
- Whatever Claude queries is sent to Anthropic. That's fine for this synthetic data, but real data needs IT and compliance approval first.
- Sharing a report with colleagues through the Power BI Service needs Pro licences. This workshop stays in Desktop.

## Data source and licence
Contoso V2 sample data by SQLBI ([Contoso Data Generator](https://github.com/sql-bi/Contoso-Data-Generator-V2), MIT). It's downloaded by the scripts and isn't stored in this repo. All people and companies are fictitious.

This workshop kit is MIT-licensed (see `LICENSE`). Note that `answer_key/` is public: it's presenter material, not a secret.
