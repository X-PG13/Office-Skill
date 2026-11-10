# CJK typography

Chinese output is not Latin output with a font fallback. Set the East Asian face on every run.

## Faces the engines name

| Role | Name the file stores | Why |
| --- | --- | --- |
| Sans, including PPTX body and Chinese workbooks | Noto Sans CJK SC | Covers simplified Chinese and basic Latin |
| Serif, including 公文 body and academic Chinese | Noto Serif CJK SC | Covers simplified Chinese |
| Latin sans | Liberation Sans | Metric stand-in for Arial, present in LibreOffice |
| Latin serif | Liberation Serif | Metric stand-in for Times |
| Mono | Liberation Mono | Step numbers and identifiers |

Install them before QA (`scripts/install_tools.sh`). If the desktop that opens the file does not have the same faces, line breaks will move. Say that in the delivery note. Do not embed the full CJK fonts; they are large, and the license of the file stays MIT without a font bundle.

公文的小标宋、仿宋、黑体、楷体没有可嵌入的免费全套。剖面里写了替代关系。不要把衬线斜体当作楷体。

## Setting the face

- PPTX: every `a:rPr` gets `a:latin` and `a:ea`. Theme major/minor and Hans/Hant script slots are patched to the same pair. A run that only sets Calibri will render Chinese in a substitute and the gate will fail.
- DOCX: every run sets `w:ascii`, `w:hAnsi`, and `w:eastAsia`. Document defaults do the same. Numbering definitions carry the face so the "1." is not Calibri.
- XLSX: one font name per cell. English models use Liberation Sans. Chinese models use Noto Sans CJK SC for the whole sheet, because that family also draws the digits.
- PDF: Typst font list is `(primary, fallback)`.

## Composition

- Simplified Chinese uses fullwidth punctuation ：，。；「」. No space between a Han character and a fullwidth mark.
- Dates in 公文: `2026年11月10日`, Arabic digits, no leading zero on the month or day, no space.
- Body indent for 公文 and for a Chinese lesson sheet is 2 em. Do not justify a one-line sentence; the last line, and any short line, will stretch.
- Slide titles are left aligned. Centered CJK titles with a decorative underline are a template habit, not a consulting habit.
- Do not letter-space a line to force 28 characters. With Noto that looks worse than a ragged edge.
- Latin product names inside a Chinese sentence can sit tight against the characters. Do not insert a full space on both sides by habit.
- Line breaks: keep an opening quote with the words that follow. The plan can put a hard break with `\n` in a slide title when the phrase has a natural pause.
