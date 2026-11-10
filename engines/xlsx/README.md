# XLSX engine

openpyxl. The plan lists assumptions and rows. The compiler in `compiler.py` turns a short expression into a formula. Nothing in the forecast is a pasted total.

Sheets: cover, assumptions, forecast, dashboard (names follow the language).

Colors come from `profile.model`: blue input, yellow fill, black formula, green cross-sheet. The cover explains the grammar in the plan's language.

`NPV` and `IRR` are written by the engine from `returns`, not by the expression language. Charts are native bar or line charts, one forecast row each, colored from `palette.series`.

Pandas is available for rectangular dumps via `engines.xlsx.bulk.write_dataframe`. Do not use it to paste calculated results over formula cells.

```bash
python -m office_skill render plan.json -o model.xlsx
```

Print setup is A3 landscape, fit to one page wide. After rendering, the gate recalculates in LibreOffice and fails on any error value.
