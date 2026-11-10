# Education

Audience: a teacher preparing a sheet, or a student reading one. Also a unit-cost workbook when the prompt asks for numbers. Domain id: `education`.

Tokens: `profiles/education.json`. White page, ink `#1C2430`, one blue `#1F4B7A` for a heading or a step. No stickers, no cartoon borders, no rainbow boxes.

## PDF handout

Typst. Chinese sheets use Noto Serif CJK SC at 12 pt, first-line indent 2 em, headings in Noto Sans CJK SC. Put the answer key after a `page_break`, with its own heading, so the working page stands alone.

A worked example must be arithmetically right. Show the unit conversion, not only the result. Name the common error in a sentence, not in a warning icon.

English sheets use the same template with Liberation Serif and `language: en`. Do not set a 2 em indent on English; override is not required if you keep paragraphs short — the profile indent applies to the education PDF, so write English education plans as `language: zh` only when the sheet is Chinese. For an English sheet, the indent is a limitation of this profile; keep paragraphs to one or two sentences so the indent does not look like a letter.

## Workbook

Same formula grammar as finance: blue inputs, yellow fill, black formulas, green cross-sheet links, an assumptions sheet. The grammar is how a model is read, not a decoration. Say the figures are illustrative when they are a teaching case.

## Slides

If the prompt asks for slides, use the consulting primitives with these tokens: one idea, a worked step, no clipart.

## Forbidden

Emoji section markers. "Let's dive in." Fake school letterhead of a real school. An answer that does not match the question.

## Data

Enrollment, prices, and hours in a sample model are scenario assumptions with a source note that says so. A mathematics item is not "illustrative" if the arithmetic is the point — it has to be correct.
