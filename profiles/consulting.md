# Consulting

Audience: a leadership team that has to decide. Typical files: a discussion deck, a board exhibit, a short decision memo. Not a keynote and not a status dump.

Tokens: `profiles/consulting.json`. Cover, section, and close are dark. Content slides are white. The only motif is a small square on those three slides. Do not add a bar, a stripe, an underline, or a footer rule.

## Page

Widescreen 13.333 × 7.5 in, margin 0.58 in. Action title is a sentence at 22 pt, left aligned, at most two lines. Body 15 pt. Source line 10 pt at the foot, no bar behind it.

Latin face: Liberation Sans. East Asian face: Noto Sans CJK SC, on every run. These are the LibreOffice-safe faces. Do not switch to Aptos or 微软雅黑.

## Color

Ink `#1A1F1C` on white. Accent `#0F6A4A` only for the recommended column and, if needed, one emphasized bar. Brass `#C4A46A` is the square on dark slides only. Series stay in the token list. If the palette would also fit a bank, a hospital, and a startup, it is too generic — this one is graphite and one green, and the green is scarce.

## Primitives

`cover`, `section`, `action`, `chart`, `table`, `matrix`, `timeline`, `comparison`, `steps`, `close`.

One message per slide, usually one exhibit. An action title states the finding in a sentence. It does not name only the topic. Every content slide has a source or `illustrative: true`. The renderer prefixes 示意 / Illustrative.

## Grammar

Situation, complication, the question, the answer, the next decision. Pyramid: the title is the answer. Comparison slides mark one column recommended. A timeline is a sequence of decisions, not a chevron process.

## Forbidden

Emoji. Lorem, TODO, 待填写. Titles that could sit on any deck: Overview, Key Takeaways, 关键要点, 谢谢. Three identical icon cards. Accent underlines. Invented market shares. Firm names and their templates are not a style; do not use them.

## Data

Do not invent a precise statistic. If the prompt did not provide a number, drop the chart or set `illustrative: true` and say what the number is a sketch of. Internal, unaudited operating data is labeled that way.

## Chinese

Write the title as a full sentence. Use fullwidth punctuation. No space between a Chinese character and a following fullwidth comma. Keep source lines to one line.
