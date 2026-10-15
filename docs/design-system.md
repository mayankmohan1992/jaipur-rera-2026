# Jaipur series — design system

The standing rules for every deck under `docs/linkedin-series/`. They are not
preferences; each one exists because breaking it produced a real defect that a
review caught. A new deck follows all of them.

Decks: `property-revenue/`, `land-use/`, `nightlights/`.

---

## 1. No text may ever overlap a chart mark

**No text may overlap a chart mark — bar, line, point, area, axis or gridline —
nor another piece of text.**

This is the single most-violated rule, because the natural place to put a label is
usually where the data already is. The 2026 annotation on the nightlights
like-for-like chart wanted to sit beside the last point; beside the last point is
exactly where the line runs. Every fix is therefore structural, not a nudge:

- **Reserve a margin or gutter and put the label in it.** The nightlights line
  charts give the opening value a left gutter and the closing value a right one,
  and stop their gridlines short of those gutters. A reserved column is also more
  readable than three loose labels.
- **End the gridlines before the value labels**, don't move the labels onto them.
  Horizontal bar charts put their value labels in a column to the right of where
  the gridlines stop.
- **Drop the gridlines entirely when labels surround the marks.** The zone scatter
  needed every dot named, so no arrangement of gridlines would stay clear of the
  text. A ticked L-frame carries the scale instead.
- **Move the text out of a bar rather than on top of it.** A white label inside a
  coloured bar is legible, and it is still text over a mark. Put it beside the bar.
- **Never shrink type to resolve a collision.** Widen the pitch, raise the chart,
  add a gutter, or move the label.

### The one exception, and why it is narrow

A label that is **wholly inside its own proportionate shape, and is the only place
its value appears on the slide** is allowed to stay there. A percentage inside its
own share-bar segment is the clearest example: taking it out deletes the figure.

The exception is deliberately narrow, and the verifier enforces the boundary:

| case | verdict |
|---|---|
| label wholly inside a shape (`rect/inside`) | reported, allowed only under the exception above |
| label **straddling** a shape's edge (`rect/straddles`) | **always a defect** — half the text is off the shape |
| label over a line, gridline, axis or point | **always a defect** |
| text over another text | **always a defect** |

So the exception can never hide a collision: a straddle fails, and a label whose
value is printed elsewhere on the slide fails too (remove it — the number is
already there). Both remaining cases in this series fall inside the exception, and
both are the sole carrier of their figure:

- `land-use` slide 09 — the 51 land-use-mix percentages inside the 100 % zone bars.
- `property-revenue` slide 08 — `69.7%` and `19.3%` inside the revenue share bar.

### Verify it by measurement, never by eye

```
node tools/verify_chart_marks.js <path/to/deck.html> [--tolerance px]
```

It loads the real deck in the vendored Chromium and compares painted geometry:

- **Text** is measured as its painted box (`getBBox()` → the font's ascent/descent
  box, which is what the engine lays out and what the older
  `verify_chart_labels.js` measures with `getBoundingClientRect`). Text boxes are
  filled quads, because a text box is an occupied area.
- **Marks** are measured from the element's own geometry — a `<line>`'s endpoints,
  a `<polyline>`'s segments, a `<circle>`'s disc, a `<rect>`'s corners — converted
  through `getScreenCTM()`, so rotated text and transformed marks are handled by
  the engine's own matrices. A diagonal line's *bounding box* covers half the plot
  and would produce nonsense; the segment never does.
- **A rect is a bar only if it carries `rx`.** Rects without a corner radius are
  era bands and plates. That is the convention every chart in this series follows,
  so the classification needs no tagging. Excluded rects are listed in the output
  with their size and opacity, so a wrongly excluded bar would be visible.
- **Background tints are not marks, deliberately.** Labelling a band is the point
  of a band (the PLATEAU / ACCELERATION era shading). Labelling a bar is not.

The default tolerance is **0.75 px**: a touch closer than that counts as an
overlap. The run **fails** (exit 1) on any overlap, and prints the tightest
text-to-mark clearance per chart so a *nearly* colliding label is visible before it
becomes one. Keep that clearance at 4 px or more; below that a small font-metric
difference can close it. An empty result is a failure too — a deck that failed to
load must not read as a pass.

`deck/verify_chart_labels.js` still runs in the land-use deck for the narrower
rule it was written for (a label belonging to a bar must be *centred* on that bar,
measured). It requires the chart to tag its marks, so it cannot see a chart built
without tags — which is why the geometric verifier above exists and is the one to
run on a new deck.

---

## 2. Background plate — the series watermark

Every deck carries the same faint Hawa Mahal mark in the bottom-right corner. It
is a standing element of the series, like the palette, not a per-deck choice.

| setting | value |
|---|---|
| asset | **`docs/linkedin-series/assets/hawa_mahal.png`** — one shared file, not a per-deck copy |
| position | bottom-right; the image's top-left at **(560, 780)** on a 1080×1350 slide |
| size | drawn at **900 px** wide, aspect preserved (so only the image's north-west corner is on the slide and the rest bleeds off the right and bottom edges) |
| opacity | **0.15**, behind all content |
| stacking | plate `z-index: 0`, `.inner` content `1`, `.topbar` rule `2` — explicit, never left to DOM order |
| embedding | as a `data:` URI, so the deck stays one self-contained file |

Implementation: it is **one constant** — `BG` in each deck's `build_deck.py`. Set
`BG = None` and the plate is gone with no other edit anywhere.

- **Feather only what has an edge.** This asset is a palette PNG whose background
  index carries alpha 0, so only the building paints: there is no rectangular plate
  and no seam to blend away. Feathering it would only thin out the building's own
  edge. A JPEG always needs one.
- **Check legibility over it**, not just presence. The plate check sits in each
  deck's render audit beside the overflow and overlap checks.

---

## 3. Palette

Pink City. Rose `#C1446A`, gold `#E0A34E`, deep indigo `#1F2A44`, ivory `#F5EDE4`,
with `--rose-dk #9E3156`, `--gold-lt #F6E3C6`, `--muted #707481`, `--grey #C9BFB4`
as the supporting set. Extra categories take tints and shades of those four, never
new hues. Any chart that uses colour to encode also labels it directly or keys a
legend, so colour is never the only channel.

## 4. Typography

Noto Serif for display, Inter for everything else. Neither is downloaded; both come
from the system. Both carry the ₹ glyph (U+20B9) — verified by a render check,
because a missing glyph is silent.

## 5. Page

1080 × 1350 px (LinkedIn's 4:5 portrait carousel ratio), rendered to a PDF at
810 × 1013.04 pt so each page is exactly one slide. One PNG per slide in `slides/`,
each verified 1080×1350 straight from the PNG header.

## 6. Charts

Hand-rolled SVG from the Python standard library. No chart library, no plotting
package, no network. The output stays vector and the deck rebuilds anywhere Python 3
runs. Chart text is laid out against **measured** font widths
(`textfit.py` + `measure_text.js` + `build_charts.sh`'s fixed-point loop), never a
per-character model — averaged over the alphabet that model is off by tens of
percent on individual words, so it reports clipped labels as clean.

Guards before a chart ships:

| tool | what it proves |
|---|---|
| `bash build_charts.sh` | the charts are a fixed point and every label has a measured width |
| `python3 check_charts.py` | no text runs off a chart's canvas and no two text elements collide (measured from the source) |
| `node tools/verify_chart_marks.js deck.html` | **§1** — no text touches a mark or other text, measured from a real render |

## 7. Copy

Audience-facing only: no file, script or repository name ever reaches a slide. No
logo and no reserved logo slot. Plain text — no markdown syntax, since none of it
would render. The source line goes on the first and last slide only; other slides
carry the page number alone.

## 8. Numbers

Indian digit grouping (`1,09,995`, not `109,995`). Every figure on every slide is
re-derived from the source by a `facts.py` that also cross-checks it, and every one
is traceable through that deck's `sources.md`. **Round outputs, never inputs** — a
figure rounded before it is used in a percentage shifts the percentage.

---

## 9. Where each deck stands against §1

Measured with `node tools/verify_chart_marks.js <deck>`, tolerance 0.75 px:

| deck | charts | text-over-mark | text-over-text | note |
|---|---|---|---|---|
| `nightlights` | 7 | **0** | **0** | clean |
| `property-revenue` | 11 | 2 | 0 | both inside their own share-bar segment (the §1 exception; sole carrier) |
| `land-use` | 10 | 51 | 0 | all inside their own 100 %-bar segment (the §1 exception; sole carrier) |

No straddles, no text over a line, gridline, axis or point, and no text over text
in any of the three. The land-use share **strip** (slide 03) had four labels inside
it that duplicated the figures in the ranked rows directly below; those were
removed rather than exempted, which is why it no longer appears above.
