# Library gotchas

Original notes for the stack this skill actually runs. They are not a copy of any other skill's text.

## python-pptx

- Set slide width and height before adding slides. The blank layout is 13.333 × 7.5 in here (12,192,000 × 6,858,000 EMU), not the 10 × 5.625 in default.
- `text_frame.text = ...` replaces runs. Add a run and set latin and ea on that run.
- A chart with one series still paints each category a different color until `plot.vary_by_categories = False`.
- Horizontal bar charts draw the first category at the bottom. Reverse the category axis and set the value axis to cross at maximum so the first category is on top and the axis stays at the bottom of the plot.
- Do not round-trip the package through a pretty-printer. Font patching is done on the live element tree before `save`.
- Shadows and 3D are stripped. They are a common reason PowerPoint offers to repair a file, and they are not part of any profile.

## python-docx

- Heading styles must have their color set explicitly or the theme blue comes back.
- A TOC is a field (`TOC \o "1-2" \h \z \u`), not a row of tabs and dots. The cached result lists the headings so the file is readable before Word refreshes it. `w:updateFields` asks Word to refresh on open. LibreOffice often refreshes during PDF export.
- Numbering is a numbering part plus `numPr` on the paragraph. Typed "1." plus a tab will drift.
- Table widths are in twips (dxa), not a percentage string.
- East Asian text needs `w:eastAsia`. Setting `font.name` alone stores the Latin face.

## openpyxl

- A formula cell's value is the string `=...`. Writing the computed number "so the sheet looks finished" fails the gate.
- `data_only=True` reads the cached value, which is empty until LibreOffice recalculates. The gate converts the file with `soffice` and then checks for `#REF!`, `#NAME?`, `#VALUE!`, `#DIV/0!`, `#NUM!`, `#NULL!`, `#N/A`.
- LibreOffice does not implement `XLOOKUP`, `XMATCH`, `FILTER`, `UNIQUE`, `SORT`, or `SEQUENCE`. Stay with the functions listed in the finance profile.
- `NPV` discounts the first argument by one period. The engine writes `NPV(rate, year1:yearN)+year0`.
- Defined years are text (`number_format` `@`) so they do not become dates.

## Typst

- The compiler is the `typst` Python package (pinned). A failed compile is a failed gate.
- Escape `# $ < > * _ \` @ [ ]` in prose. Math is a separate block and cannot contain `import`, `include`, or `read`.
- System fonts must be visible to fontconfig. Liberation and Noto CJK are installed by `scripts/install_tools.sh`.
- WeasyPrint is optional and is not in the default install. Use it only when the plan sets `pdf_engine` to `weasyprint`.

## QA tools

- Call LibreOffice with a fresh `-env:UserInstallation` and `SAL_USE_VCLPLUGIN=svp`. A bare `soffice` left over from another process will hang or no-op.
- Rasterize with `pdftoppm -png`. Do not use PyMuPDF; it is AGPL and this repository is MIT.
- The same overflow estimator runs inside the renderer and inside the gate. If they ever diverge, the gate copy in `office_skill/geometry.py` is the one to fix, and the renderer should keep calling it.
