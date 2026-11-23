---
name: extracting-pbi-style
description: Extract a reusable Power BI theme and the local formatting conventions from a reference report. Use when someone wants to capture a company's reporting style for reuse.
---

# Extract a Power BI report style

Use the reference report the user names. In the workshop it is `pbi/AlderwakePress.pbip`. Save the style kit outside the source report. Default workshop outputs are `pbi/style-kit/theme.json` and `pbi/style-kit/appearance.md`. Use a separate kit folder for a different source.

1. **Export the active theme.** From the repository root run the command below, substituting the source and output paths. The helper follows the project pointer and the active resource registration. A report can contain several old themes.

   ```powershell
   .venv\Scripts\python.exe scripts\pbi_theme.py extract pbi\AlderwakePress.pbip pbi\style-kit\theme.json
   ```

   For a PBIX, or a project with only a built-in theme, use Desktop's **Export theme** (older versions use **View → Themes → Save current theme**). Inspect the open reference page for the next step. A base-only report can still have a distinctive brand through local formatting.

2. **Read the page as well as the theme.** In PBIR, inspect representative `page.json` and `visual.json` files under `definition/pages`. Compare their `objects`, `visualContainerObjects` and textbox `paragraphs[].textRuns[].textStyle` with the theme defaults. Identify the appearance of the headline, chart and KPI surfaces, and any deliberate use of color for meaning. Record font face, point size, foreground, fill and spacing by role where the source gives a value. If an image carries the brand, identify its registered resource and placement separately.

3. **Write the handoff.** Put the source path and page, palette and font roles, and local treatments worth reproducing into `appearance.md`. Include enough detail to restyle an existing title in its own words. In the sample, the dark masthead and its two text treatments live in one textbox. Cite its visual ID so the applying skill can find it. Keep donor headlines, numbers, model fields and queries out of the kit. Mark one-off analytical highlights as report-specific.

4. **Check the kit.** Parse the theme JSON, compare its palette and text classes with the active source, and check each local treatment against the named page. Return both paths and a short description of what participants should recognize after applying it.
