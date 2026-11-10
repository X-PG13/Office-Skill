# Visual QA

The gate cannot see composition. After `gate.json` says passed, open every PNG and check the page, not your memory of the plan.

## Every page

- The title is a claim, and it is fully visible. No last line clipped, no word cut mid-character.
- Body text does not collide with the source line, the page number, or the edge.
- Contrast is obvious in grayscale: ink on paper, not gray on tint.
- No leftover placeholder, no emoji, no "lorem".
- The same Latin face and the same CJK face throughout, including chart axis labels.
- One accent, used where the profile allows it. No new color introduced on a single page.

## Slides

- Source line is one line and does not run under the page number.
- The chart has no rainbow series, no 3D, no title repeating the slide title.
- Bar labels are readable. The emphasized bar, if any, is the one the sentence is about.
- A 2×2 has four readable cells and a cross, not four filled cards.
- The recommended column is marked by the word and a short rule, not a giant color fill.
- Dark slides are only the ones the profile names (cover, section, close).

## Documents

- Headings are not theme blue.
- 公文: red appears only in the issuing authority and the rule under the doc number. The second page does not repeat the red header. The page number looks like — 1 —. The 版记 is at the end, with horizontal rules only.
- Legal: numbers align; a defined term is bold at the point of definition; the TOC is a field, not a hand-drawn dot leader.

## Sheets

- You can tell an input from a formula without reading this file.
- The printed page is one sheet, landscape, and the type is still readable.
- The chart is the workbook's chart, and the series color matches the profile.

## PDF

- First page carries the title, not a running header.
- A table caption is present and the header row is not repeated as a data row.
- Chinese punctuation is fullwidth and not sprinkled with Latin spaces.
- The answer key, if any, starts on its own page.

Stop when the defects are gone, not after a fixed number of tries. Re-render the whole file; the engines are deterministic.
