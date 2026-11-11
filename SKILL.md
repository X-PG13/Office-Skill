---
name: office-skill
description: >
  Generate a professional PPTX, DOCX, XLSX, or PDF from three inputs: file type,
  professional domain, and a prompt, plus optional source files. Use when the user
  wants a slide deck, memo, opinion, official notice, spreadsheet model, or PDF
  that should look like a domain expert made it. Chinese and English are both
  first-class. Do not use for editing an arbitrary existing Office file in place.
---

# Office-Skill

The user supplies `file_type`, `domain`, and a prompt. Optional source files may
come with the prompt. Do not ask them to pick a library, a theme, or a template.

Output language follows the prompt. Simplified Chinese and English are both
first-class. Do not mix them unless the prompt does.

## Input contract

| Input | Values |
| --- | --- |
| `file_type` | `pptx`, `docx`, `xlsx`, `pdf` |
| `domain` | `consulting`, `finance`, `legal`, `academic`, `product`, `brand` (also `marketing`), `government` (公文), `education` |
| prompt | What the document must decide, explain, or teach |
| sources | Optional. Figures in the file must come from these, or be marked illustrative |

If the domain is not in the list, pick the closest profile, say so in the delivery note, and do not invent a mood palette.

## What to load

Load exactly one profile and one engine. Do not read the other profiles.

1. `profiles/<domain>.md` and `profiles/<domain>.json`
2. `engines/<file_type>/README.md`
3. `references/plan-schema.md` for the primitive you will use
4. `references/anti-ai-traces.md`
5. If the output is Chinese, also `references/cjk-typography.md`
6. `references/library-gotchas.md` only when a render or a gate fails

## Pipeline

1. **Interpret.** Audience, decision, language, length, and whether each number is sourced or must be labeled illustrative. Do not invent precise statistics, cases, citations, or 文号.
2. **Plan before drawing.** Write a JSON plan (see `references/plan-schema.md`). Storyline, claims, exhibits, sources. No coordinates.
3. **Render** with the engine. From the repo root:

```bash
python -m office_skill render plan.json -o deliverable.pptx
```

4. **Gate.** The script grades what you must not grade yourself:

```bash
python -m office_skill gate deliverable.pptx --plan plan.json --preview-dir /tmp/preview --result gate.json
```

The command writes `gate.json`. `passed: false` means fix the plan or the content and render again. Do not flip the flag by hand.

5. **Look at every page.** Open every PNG in the preview directory. This step is required even when the JSON says passed. Check the list in `references/visual-qa.md`. A fresh pass is better than the pass that just wrote the file: you will see the sentence you meant instead of the one on the page.
6. **Deliver** the file and a short note: profile used, what is illustrative, residual risks (font substitution, fields Word will refresh). The renderer writes `*.delivery.md` beside the file.

## Domain route

| Domain | Default file when the prompt does not specify | Read |
| --- | --- | --- |
| consulting | pptx | action titles, one exhibit, source line |
| finance | xlsx | formulas, assumption sheet, blue / yellow / green |
| legal | docx | numbered paragraphs, defined terms, no invented cases |
| academic | pdf | Typst article, real citations, limitations |
| product | pptx | problem, constraint, decision |
| brand | pdf or pptx | one idea, the product's own words |
| government | docx | 公文 profile, GB/T 9704 measurements |
| education | pdf or xlsx | a calculation shown in full |

## Hard rules

- Named primitives only. Do not hand-write OOXML or raw coordinates.
- Charts, tables, and formulas are native objects. Do not paste a picture of a chart.
- Placeholder text, emoji, and generic titles (`Overview`, `关键要点`) fail the gate.
- v1 creates a new file. It does not round-trip an arbitrary existing deck or contract.
