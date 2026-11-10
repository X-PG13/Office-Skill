# PPTX engine

python-pptx, widescreen, blank layout. You choose a primitive from `references/plan-schema.md`. The engine places it on the grid in `profiles/<domain>.json`.

```bash
python -m office_skill render plan.json -o deck.pptx
```

What the engine always does:

- Paints the slide from the profile tone (light or dark).
- Sets Liberation (or the profile Latin face) and Noto CJK on every run, including chart axes, then patches the theme.
- Draws a source line and a page number. Illustrative slides are prefixed.
- Uses one native chart, not a picture. Single-series charts are one color; `emphasis_index` recolors one point with the accent.
- Strips shadows and 3D.
- Refuses to save if a text box overflows or a shape leaves the slide.

Do not import this module and then add free-positioned shapes. If a layout is missing, add a primitive here rather than emitting coordinates from the model.
