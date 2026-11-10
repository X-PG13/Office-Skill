# Legal

Audience: a client or a colleague who will rely on the structure and argue with the analysis. Typical files: an opinion letter, a memorandum, a schedule. Serif, black, almost no decoration.

Tokens: `profiles/legal.json`. Body face: Liberation Serif with Noto Serif CJK SC. 12 pt, 1.15 line spacing, A4.

## Structure

Real Word styles: Normal, Heading 1–3, Caption. A TOC field (`TOC \o "1-2"`) when `include_toc` is true. Numbered paragraphs use a multilevel list (`1.` and `(a)`), not typed numbers and not a literal bullet glyph.

Running header: matter on the left, classification on the right. Footer: a page field.

Defined terms are a `definition` block: the term in bold, then the definition in the same paragraph. Quotations are indented with a black left rule, not a colored bar.

## Grammar

Say who asked, what you read, and what you did not read. Separate the client's account from a finding. Cite a statute by article only when you are sure of the proposition; paraphrase rather than invent quotation marks. Do not name a case you have not verified. Do not predict a percentage outcome. End with what the opinion does not decide.

Chinese opinions use fullwidth punctuation and defined terms in 「」. No contractions in English. No emoji. No icons.

## Forbidden

Color blocks. Informal hedging ("basically", "显然没问题"). Placeholder party names left as 甲方某某. Invented docket numbers.

## Data

A date, a price, or a clause is included only if the prompt supplied it, and the text says it comes from the client's account when that is all you have.
