# Workshop runbook (60 min)

**Roles:** the *Driver* (technical) types and runs the laptop. The *Business user* (non-technical colleague) says what they want and answers Claude's questions. That split *is* the message: the business person decides what things mean, and the AI does the technical work.

**Before you start:** the repo is at its reset point, `pbi/ContosoWorkshop.pbip` is open in Desktop, the Claude desktop app is open in this folder, the MCP connection has been tested, and the screen is zoomed to 125%.

During rehearsal, also open `pbi/AlderwakePress.pbip` and choose **Home → Refresh**. Its model contains eight fictional records. With no selections the reference shows 48,000 copies and a 58.3% print share. Keep the two report names visible when switching windows.

---

## 0:00–0:08 · Why this matters (slides or talk)
- Today: a business question → a ticket to the BI team → days or weeks.
- With AI: the business user describes what they need, and the AI builds it. **But AI is only as good as the meaning you give it.**
- Three ingredients: **access to data**, **a semantic layer** (what things mean), **building the report**.
- Show the costs honestly: paid Claude seats; Power BI Desktop is free; sharing needs Pro licences.

## 0:08–0:18 · The problem: cryptic data
Show `data/legacy/fct_sls_ln.csv` in Excel or a text editor, then the field list in Power BI Desktop.
> "Which column is revenue? Is `unt_cst` unit cost or customer? Which currency?"

Prompt (Business user):
```
Look at the data in data/legacy and tell me in plain language what's in it and what looks wrong.
```
Expected: Claude profiles it and finds the order-line grain, the 40 duplicate lines, the trailing spaces, missing cities, 2024 as a partial year, and the cost/customer abbreviation clash.
**Talking point:** this is the data reality in every enterprise.

## 0:18–0:32 · Building the semantic layer together (Skill 1)
Prompt:
```
Help me make this data understandable for the business. Propose business names and definitions, and ask me about anything you're unsure of.
```
- Claude shows high-confidence names for bulk approval, then asks multiple-choice questions. The *Business user* answers them out loud. Suggested answers: amounts are USD after discount, `cst` in the sales table is cost, remove duplicates, revenue = Net Sales.
- Claude writes `semantic/glossary.yaml`, then applies it. **The audience watches the Desktop field list rename itself live.**
- Claude validates: Net Sales 2023 = **$31,871,231** (golden answer).

**Fallback** (over time or stuck): `copy semantic\glossary.fallback.yaml semantic\glossary.yaml`, then prompt `Apply semantic/glossary.yaml to the model and validate the measures.`

**Talking point:** without the de-duplication, Net Sales would be $31,881,546. It's small, but it's wrong, and finance would notice.

## 0:32–0:47 · Building the report from a business request (Skill 2)
Prompt (Business user, deliberately conversational):
```
I'm presenting to the sales leadership. I need a one-page overview of how we did last year: revenue, margin, how many customers bought, which product categories and countries drive it, and the monthly trend compared to the year before.
```
- Claude asks 1–3 clarifying questions (e.g. "Region: by store country or by customer continent?").
- Claude verifies the numbers, then proposes a layout and builds the page.
- *Driver*: when asked, close Desktop, wait for Claude, then reopen `pbi/ContosoWorkshop.pbip`.
- Show the page. Point out the Definitions box.

**Fallback:** if the page fails to render, show the numbers Claude verified (the DAX query results) and build one visual by hand, describing it as "AI did the model, I did the layout". That's also the honest picture of today's tools.

## 0:47–0:55 · The story works. Now give it our company style (Skills 3 and 4)

*Business user:* “This tells the right story. It still doesn't look like one of our reports.” Show the finished Contoso page and capture a screenshot with its current slicers and KPI values. Switch to the Alderwake Press circulation review. Point out the light-blue canvas, navy masthead with its bright-blue label line, rounded white cards, geometric headline font and the blue-and-navy chart.

**Retrieve the style.** Prompt:

```
Use pbi/AlderwakePress.pbip as our company style reference. Save its reusable theme and appearance notes in pbi/style-kit/. What makes this look like an Alderwake report?
```

Show the theme and the masthead entry in the notes. The masthead has its own formatting inside a textbox.

**Apply it.** Save and close the Contoso report, checkpoint the generated page, and prompt:

```
Apply the style in pbi/style-kit/ to pbi/ContosoWorkshop.pbip. Keep the sales story and the Definitions box. Match the headline treatment to our existing headline and preserve the meaning of our chart colors.
```

Reopen Contoso beside its before screenshot. Ask the audience to identify two visible brand changes, then read the same KPI with the same filters. For the 2023 sales overview, Net Sales should still be **$31,871,231**.

**Fallback:** in Contoso, use Desktop's theme import command and select `pbi/AlderwakePress.Report/StaticResources/RegisteredResources/AlderwakePress.json`. This demonstrates the palette, type and surfaces. Show the donor masthead alongside it to illustrate why local formatting also needs a pass.

## 0:55–0:57 · Deliberate failure: ambiguity
Prompt:
```
Add a card with our revenue in euros.
```
Expected: Claude points out that amounts are USD and asks whether to convert at the order-date rate or filter to EUR orders. **Talking point:** a good agent asks instead of guessing, and the answer goes into the glossary so it never has to ask again.

(Optional) Ask a golden question it can answer instantly from the model: `How many active customers did we have in 2023?` → **13,746**.

## 0:57–1:00 · Reality check and Q&A
- **Works well:** model cleanup, naming, descriptions, measures, checking numbers, first drafts of pages.
- **Still needs a human:** business definitions, visual polish, sign-off on numbers.
- **Governance:** data sent to the AI, licences, the preview status of the tools, version control (git) as the undo button.
- **Next steps for us:** a pilot on one real (approved) dataset, with a business owner per glossary term.

---

## Golden answers cheat sheet (2023 unless stated)
| Question | Answer |
|---|---|
| Net Sales, all time | $203,723,866 |
| Net Sales | $31,871,231 |
| Gross Margin % | 56.1% |
| Discount % | 6.0% |
| Orders | 15,503 |
| Average Order Value | $2,055.81 |
| Active Customers | 13,746 |
| Top category | Computers ($11,222,620) |
| Top store country | Online |
| Top customer continent | North America |
| Contoso-brand units | 33,566 |

Source: `eval/golden_questions.yaml` (regenerate with `scripts/golden_answers.py`).
