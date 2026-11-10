# Academic

Audience: a reader of a discussion note or a short working paper. The PDF engine is Typst. A Word file uses the same serif and real heading styles. Do not produce a bullet "paper".

Tokens: `profiles/academic.json`. A4, Liberation Serif and Noto Serif CJK SC, 11 pt, numbered headings, captions on every table and figure.

## Structure

Title, authors, a one-paragraph abstract, keywords if useful, numbered sections, then references. The plan must include a limitations section (the heading contains "limitation", "does not", "局限", or "不说明"). The renderer will refuse an academic PDF without it.

Mathematics is a Typst math block, not a picture and not Unicode superscripts pretending to be an equation.

## Citations

Every reference needs an `id`, a human `label` for the in-text citation, and a `text` bibliographic line. In paragraphs, cite as `[@id]`. Do not add a `doi` field unless you have checked that DOI. Do not invent a journal article, a sample size, a p-value, or a quotation.

Safe pattern: make an argument, cite a work you know exists, and say what this note did not test.

## Forbidden

Decorative covers. Emoji section markers. Fake DOIs. "Key takeaways" as a section title. A bibliography of plausible-looking names.

## Chinese

If the prompt is Chinese, set `language` to `zh`. The same template uses Noto Serif CJK SC as the first face. Punctuation is fullwidth. A translated citation keeps the original bibliographic facts.
