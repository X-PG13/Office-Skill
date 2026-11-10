# Finance

Audience: someone who will change an input and check that the outputs move. Typical files: a returns model, an assumption log, a one-page result sheet. A deck, if requested, uses the same restraint as the model: black, white, one steel blue.

Tokens: `profiles/finance.json`.

## The model grammar

This is the public modeling convention, not a firm's template.

- Inputs: blue font `#0000FF`, yellow fill `#FFFF99`.
- Formulas: black.
- Cross-sheet links: green `#008000`.
- External links, if any: red. v1 does not create them.
- Years are text, not dates.
- Currency format with negatives in parentheses when the unit is dollars.
- Every assumption has its own cell, a unit, a note, and a source.
- NPV, IRR, totals, and growth builds are formulas. The expression language is in `engines/xlsx/README.md`. Allowed functions: `+ - * / ^`, `MAX`, `MIN`, `ROUND`, `ROUNDUP`, `ABS`, `IF`, plus engine-written `NPV` and `IRR`. No `XLOOKUP`, `FILTER`, `UNIQUE`, `SORT`, `SEQUENCE`.

## Page and type

Slides, if used: Liberation Sans, 20 pt action titles, dense but aligned. Workbooks print landscape A3, fit to one page wide. Font is Liberation Sans in English and Noto Sans CJK SC in Chinese, because Liberation Sans has no CJK glyphs.

## Grammar

State the question the model answers, the simplifications, and what would change the decision. A thin case that does not clear the hurdle is a valid result. Do not add a terminal value you cannot defend. Label illustrative cases on the cover and in the footer.

## Forbidden

Hardcoded totals. Neon dashboards. 3D charts. A chart pasted as a picture. Invented "street" multiples presented as fact.

## Data

If the prompt did not supply historicals, the plan is `illustrative: true` and the banner says so. Do not describe scenario inputs as reported results.
