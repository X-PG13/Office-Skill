# Plan schema

The renderer accepts one JSON object. Validate it with `python -m office_skill render`. Unknown keys on a primitive are ignored; missing required keys fail.

Common fields: `file_type`, `domain` (canonical id, not an alias), `language` (`zh` or `en`), `title`, optional `author`, `subtitle`.

## pptx

`slides`: a list. Each slide has `primitive` and, except the cover, `title`.

| Primitive | Fields |
| --- | --- |
| `cover` | `kicker`, `title`, `subtitle`, `meta` (string or list) |
| `section` | `kicker`, `title`, `subtitle` |
| `action` | `title`, `paragraphs` (list of strings), optional `pull` |
| `chart` | `title`, `categories`, `series` (`name`, `values`), `chart_type` (`column`, `bar`, `line`), `unit`, `insight_lead`, `insight`, `emphasis_index`, `number_format`, `illustrative`, `source` |
| `table` | `title`, `columns`, `rows` (list of lists), optional `aligns`, `widths`, `note` |
| `matrix` | `title`, `x_axis`, `y_axis`, `quadrants` (4 items with `pos` of `tl`/`tr`/`bl`/`br`, `title`, `body`) |
| `timeline` | `title`, `items` (`label`, `title`, `detail`), 3–6 items |
| `comparison` | `title`, `columns` (`title`, `points`, optional `recommended`), 2–3 columns |
| `steps` | `title`, `steps` (`title`, `detail`), 3–4 steps |
| `close` | `kicker`, `title`, `decisions` (`label`, `text`) |

Content slides in a consulting deck need `source` or `illustrative: true`. A chart always does. `\n` in a title is a hard line break.

## docx

`blocks`: `heading` (`level` 1–3, `text`), `paragraph` (`text`, optional `numbered`, `level`), `definition` (`term`, `text`), `quote` (`text`, `cite`), `table` (`caption`, `columns`, `rows`), `signature` (`lines`), `page_break`.

Also `header_left`, `header_right`, `meta`, `include_toc` (default true), `numbering` (`legal` or omit).

公文: `doc_kind` = `gongwen` and a `gongwen` object: `org`, `doc_number`, `recipients`, `signoff`, `date`, optional `copy_to`, `print_org`, `print_date`. Body blocks are paragraphs with `level` 0 (indent), 1 (一、), 2, or 3. Put the enumeration in the text.

## xlsx

`years` (2–8 labels), `assumptions` (`id`, `label`, `value`, `format`, `unit`, `note`, `source`), `rows`, optional `highlights`, `returns`, `charts`, `paragraphs`, `caveat`, `illustrative`.

A row is either an input (`values`, one per year) or a formula (`expr`, optional `prev_base`). Names in `expr` are assumption ids, row ids, or `year_index`. `prev(row_id)` is the previous year. Functions: `MAX MIN ROUND ROUNDUP ABS IF`. Arithmetic and comparisons use Python spellings (`**`, `==`); the compiler emits Excel.

`returns`: `cashflow_row`, `discount_rate` (an assumption id). The engine writes NPV and IRR.

`charts`: `type` (`col` or `line`), `title`, `row`. One row per chart.

Set `illustrative: true` unless every figure is from the named sources (`data_status: "sourced"`).

## pdf

`pdf_engine` defaults to `typst`. `sections`: `heading`, `level`, optional `unnumbered`, `blocks`.

Blocks: `paragraph`, `list` (`items`), `quote`, `math` (`tex` is Typst math, not LaTeX), `table` (`caption`, `columns`, `rows`), `page_break`.

Optional: `authors` (`name`, `affiliation`), `date`, `abstract`, `keywords`, `running_head`, `classification`, `references` (`id`, `label`, `text`). Cite with `[@id]` inside paragraph text. Academic plans need a limitations section. Do not include a `doi` key.

`pdf_engine: weasyprint` renders a plain HTML letter. It is optional and not used by the samples.
