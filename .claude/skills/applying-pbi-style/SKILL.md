---
name: applying-pbi-style
description: Restyle an existing Power BI report using an extracted company theme and appearance notes. Use when the report already tells the intended story and needs to match a reference report or brand.
---

# Apply a Power BI report style

Identify the target report and style kit from the request. For the workshop, the target is `pbi/ContosoWorkshop.pbip` and the kit is in `pbi/style-kit/`. If the user supplies a reference report, use the extracting-pbi-style skill to obtain the kit. Keep the reference read-only.

1. **Capture the baseline.** Read the kit. Record the target page titles, KPI values at the current filters, chart bindings, and any meaningful color rules (for example, margin below 50%). Use the existing report checkpoint rule before editing. For PBIR edits, have the driver save and close the target in Desktop. Work on the selected target only.

2. **Apply the theme.** A theme applies to the entire report. For a report-wide request, run this command from the repository root with the actual target and theme paths.

   ```powershell
   .venv\Scripts\python.exe scripts\pbi_theme.py apply pbi\ContosoWorkshop.pbip pbi\style-kit\theme.json
   ```

   For a PBIX, use **Import theme** in Desktop (older versions use **View → Themes → Browse for themes**) and save the styled report. If the user requests only one page, apply the appearance locally on that page.

3. **Apply local treatments by role.** Match the kit's headline treatment to the target's existing headline, charts to charts and KPI cards to KPI cards. In PBIR use the report-authoring plugin to adjust individual formatting properties. For a masthead, set the target textbox fill and its existing text runs' font, color and size. Preserve its words, dynamic values, links and emphasis. Fit the treatment into the available space alongside slicers. Where a literal fill or font masks a theme default, change just that property. Preserve conditional rules, series colors with business meaning, filter state, bookmarks, navigation, positions and field bindings. Avoid bulk format resets.

4. **Verify in context.** Review the diff for theme registration, theme resource and intended formatting changes. Check that page and visual IDs, queries, filters, model files and report text match the baseline. Reopen the target and compare the KPI values at the same filters. Inspect each affected page for legibility, clipped titles and series contrast. Report which treatments were applied, any deliberate exceptions, and which checks were actually performed.
