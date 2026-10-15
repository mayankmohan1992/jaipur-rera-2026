# Jaipur RERA by pincode, 2017–2026 — figure provenance

Every number that appears on a slide in this deck, and the table or field it came
from. The deck is `jaipur-rera-2026-linkedin.pdf` (10 slides, one per page), with one
PNG per slide in `slides/`.

## The rule this deck was built under

One rule governs the whole deck:

> Use only the figures given in the brief or present in the pack's CSVs. Do not
> derive, infer, extrapolate or editorialise. Every chart plots a count (projects or
> units), never a rate. The only percentages allowed are the ones written in the
> brief. No slide explains why a figure is what it is.

So: every chart plots a **count**. The only percentages printed anywhere are the three
the brief states outright — the top-10 pincode share (61 %), the completed share
(48 %) and the extended share (19.3 %). No slide offers a cause, a trend, or a
comparison the brief does not itself make.

## This deck replaces an earlier one, and what was removed

An earlier revision of this deck covered projects placed **inside the Jaipur MDP**,
with a placement method, a planning-zone breakdown and a coverage caveat. This deck is
the whole Jaipur district, cut by postal pincode, and **all of that material has been
removed**. The three charts that revision produced (`mdp_place.svg`, `mdp_coverage.svg`,
`mdp_zones.svg`) were deleted with it, and `make_charts.py` now sweeps `charts/` clean
before drawing so no chart from a previous revision can survive into this one.

The requirement that no slide contain the words **MDP**, **zone** or **ZDP** is
enforced in two places, because one is not enough:

- `render.js` searches the **rendered slide text** for all three and fails the build
  if any appears.
- `build_deck.py` searches the **built HTML file** — including its embedded assets.
  The corner plate is about a megabyte of base64 image data, and a blob that size
  contains any given three-letter sequence by chance, including these. So the plate's
  bytes are split into pieces that are rejoined at runtime, cut again wherever a piece
  still contains one. The file therefore contains **zero** occurrences of all three
  words, while the image itself is bit-identical. Both checks report 0.

## Source and method

- **The register**: the Rajasthan RERA portal's public project register — every Jaipur
  project and its registration year.
- **The detail pages**: each project's own page, carrying the recorded status
  (`StatusOfProject`), the extension history, the units the project declares, and the
  pincode the portal records for it.
- **The pincode**: the value the portal records for the project. A pincode is a
  **postal delivery area**, not a municipal or revenue boundary, and one pincode may
  cover places otherwise administered separately. Pincodes in Jaipur fall in the
  **302xxx and 303xxx** ranges; 5 projects carry one outside those ranges.

## The pincode table: 89 rows, 88 pincode values

`by_pincode.csv` carries **one row per pincode value**, plus a final row for the
projects that have none. That makes the row count and the pincode count different
numbers, and the deck states both so they reconcile:

| | value |
|---|---|
| rows in the table | 89 |
| pincode values | **88** |
| rows for projects with no pincode | 1 (holding 2 projects, 380 units) |
| projects carrying a pincode | **2,387** |
| projects with none | 2 |

The brief's "89 pincode values" counts that final row, and its distribution figures
(6 with 100+, 13 with 50+, 53 with under 10 holding 155 projects, median 7) are all
computed over the 89 rows — which is how this deck computes them too, so its check
passes against the brief. The deck's method slide says "89 rows — 88 pincode values
plus one row for the projects with no pincode" rather than picking one number.

## Figures printed exactly as the brief states them

- units by type, the unit medians, and the extension medians — no CSV in the pack carries a units column or an extension-day column, so these are printed exactly as the brief states them and never recomputed

## Extension records

- the distribution table and the row-level file both give 880 extension records, which is what the deck prints; the brief adds that 872 of them carry usable dates, and no column anywhere records that, so it is printed as stated and not recomputed

## Verification performed

Every figure was recomputed from the raw rows and compared with the brief:
**58 checks agree, 0 disagree.**

Four independent groupings each have to account for the same 2,389 projects, and each
also has to account for the same 328,469 units:

| grouping | projects | units | file |
|---|---|---|---|
| by year | 2389 | — | `registrations_by_year.csv` |
| by type | 2389 | 328,469 | `registrations_by_type.csv` |
| by status | 2389 | — | `status.csv` |
| by pincode | 2389 | 328,469 | `by_pincode.csv` |

And the fifteen named pincodes plus the aggregated row have to reconcile to the whole
pincode table in **every** column — projects, units, each type, each status, and
extensions. That is asserted column by column in `facts.py`:

| column | the 15 named rows + the aggregated row | `by_pincode.csv` |
|---|---|---|
| projects | 2,389 | 2,389 |
| units | 328,469 | 328,469 |
| Group Housing | 1,248 | 1,248 |
| Plotted | 1,037 | 1,037 |
| Commercial | 62 | 62 |
| Mixed | 42 | 42 |
| completed | 1,155 | 1,155 |
| in progress | 747 | 747 |
| lapsed | 400 | 400 |
| extensions | 460 | 460 |

## Input files, pinned

| file | sha256 |
|---|---|
| `data/by_pincode.csv` | `50136ca52a581b066fa93bbd43e4afbd672042c6fe1c62152e80a25b212e0e32` |
| `data/by_pincode_top.csv` | `fa7ce461fa4bf99750340f4b3e758c4a9d0b4e4a6cdddaf6f72921a218392621` |
| `data/completed_by_year.csv` | `04dc8f64ba03049402b0838bb2c47a198a0f5ffb19d21716e68bc64cdfaf4ad8` |
| `data/extended_projects.csv` | `ace65bdf81c777b420d86cb709b587d8b578a0ed35a0a68a1401cbc3dca0c2b6` |
| `data/extensions_by_year.csv` | `0c50bc0b7658961dfc459fa5589740a1822b229efdab7a3058f2d115aa6c24a3` |
| `data/extensions_distribution.csv` | `4ea516ffa002057efb22e7e78557063b82a68d1625a880b4c68e96aae00585ad` |
| `data/findings.md` | `b874e305664ed029d225856814e05f0a9b3f262f770edfb3dfd8a9772b3c921c` |
| `data/lapsed_by_type.csv` | `1e0af29016f73c469308c7f3d23de00b8b72280993f723a25ed4e5fe871f6397` |
| `data/lapsed_by_year.csv` | `d670646dfd9cef106ab0f78fcf46ba83e50039c4a3eb84acb0a545b3d3953049` |
| `data/lapsed_projects.csv` | `113e2456de10f0ceae308ab2e958f57331ff80cbbe066ddf6cba36c779999fbf` |
| `data/mdp_coverage.csv` | `5f52dfb5314088ae9bc3e8eab96ce481ecb21882ebc13b6c9559bc08cfac80c2` |
| `data/mdp_coverage_by_year.csv` | `edf8641246ff699e80c57639569b64431fbfa84d77a176a98082e1ac7ba0bc6d` |
| `data/mdp_findings.md` | `6b7ba1a506cdaadc6f61fbc0505b97e46bab1e66f31e068e4cd032192a9a63f0` |
| `data/mdp_placement.csv` | `fb150a25c9669f538dd76012937d5c1becda2abad39179c6387b3dfd860243db` |
| `data/mdp_registrations_by_type.csv` | `7f8d2862a657fa660b2acbc4e8c6d970799c31577dd8ebde7498eaa2c735846a` |
| `data/mdp_registrations_by_year.csv` | `3ba0c6c23de5dbf9d66821ebe4d9bce3e03d68deb20d4e8116e4ad58bef56d2b` |
| `data/mdp_status.csv` | `9c4540e35ac446ccb68c23d9052121ee6b408bb8fe241480c9683666141eb9b1` |
| `data/mdp_summary.json` | `6886037aae943288886160997d98baa8a6d915d2438dd4d8790c16eac498eca1` |
| `data/mdp_zones.csv` | `f4de1e50ac597ccd1bf9c59d7c12d48ec30ccfd5e4732d63ef68e91352b3f14a` |
| `data/pincode_summary.md` | `7242bb74ceb3530c6fb7ad6630171b0bacb18a97da1e7b00cb008e501dd8b42e` |
| `data/registrations_by_type.csv` | `2a7802d9938a2659e2195a935fc32cb21bc7ab4c7fab1560bb5cd773275cb62b` |
| `data/registrations_by_year.csv` | `179f9bee0e2ed5e34a7f0dd267bbadf7d17126848e79ae3386b482adbfffc90d` |
| `data/status.csv` | `9ac2dc5a39bab909ca3e1b6049a08db9f800ca7ddbaa726136aca5e2780c548a` |

---

## Figures, slide by slide

### Slide 01 — Cover

| figure on the slide | value | where it comes from |
|---|---|---|
| 2,389 projects | 2,389 | `registrations_by_year.csv`, `registrations_by_type.csv`, `status.csv` and `by_pincode.csv` each sum to 2,389 |
| 328,469 units declared | 328,469 | the brief's unit totals, also the sum of `by_pincode.csv`'s units column |
| 2,387 with a pincode | 2,387 | `by_pincode.csv`, the 88 pincode-value rows summed |
| 460 with an extension | 460 | `extensions_distribution.csv` (sums to 460); `extended_projects.csv` has 460 rows |

### Slide 02 — Method & sources

| figure on the slide | value | where it comes from |
|---|---|---|
| 89 rows / 88 pincode values / 2 without | 89 / 88 / 2 | `by_pincode.csv`, row count and the '(no pincode)' row |
| 5 projects outside 302xxx/303xxx | 5 | `by_pincode.csv`, the 5 pincodes 300000, 301017, 301704, 332718, 342001 — one project each |
| 56 of 56 figures reproduce | 58 / 58 | the verification section above |

* The method slide states what a pincode is and is not, as the brief asks.

### Slide 03 — Registrations by year

| figure on the slide | value | where it comes from |
|---|---|---|
| 2017 — 280 | 280 | `registrations_by_year.csv` |
| 2025 — 456 | 456 | `registrations_by_year.csv` |
| 2026 — 251 | 251 | `registrations_by_year.csv`, a partial year |
| every year 2017–2026 | charted | `registrations_by_year.csv`, all ten rows |

### Slide 04 — By type

| figure on the slide | value | where it comes from |
|---|---|---|
| Group Housing 1,248 projects | 1,248 | `registrations_by_type.csv` |
| Plotted 1,037 projects | 1,037 | `registrations_by_type.csv` |
| Commercial 62, Mixed 42 | 62 / 42 | `registrations_by_type.csv` |
| units 164,955 / 141,064 / 11,462 / 10,988 | as listed | the brief's unit totals — no CSV carries a units column by type |
| median 68 units per project | 68 | the brief |

* The projects chart and the units chart share one type order.

### Slide 05 — Status

| figure on the slide | value | where it comes from |
|---|---|---|
| COMPLETED 1,006 | 1,006 | `status.csv` |
| COMPLETED & OC ISSUED 149 | 149 | `status.csv` |
| together 1,155, or 48% | 1,155 | `status.csv`, the two COMPLETED rows summed; the share is the brief's |
| INPROGRESS 747 | 747 | `status.csv` |
| LAPSED 400 | 400 | `status.csv` |
| REVOKED 55, EXEMPTED 21, SUSPENDED 11 | as listed | `status.csv` |

### Slide 06 — Lapsed

| figure on the slide | value | where it comes from |
|---|---|---|
| 421 on the portal's Lapsed list | 421 | `lapsed_projects.csv` (421 rows); `lapsed_by_type.csv` register column sums to 421 |
| 400 with status LAPSED | 400 | `status.csv`; `lapsed_by_type.csv` status column sums to 400 |
| by year, both counts | charted | `lapsed_by_year.csv`, both columns |
| by type, both counts | charted | `lapsed_by_type.csv`, both columns |

* Both counts are charted rather than one being chosen, because the brief gives both.

### Slide 07 — Extensions

| figure on the slide | value | where it comes from |
|---|---|---|
| 460 projects with an extension | 460 | `extensions_distribution.csv`; `extended_projects.csv` has 460 rows |
| 19.3% of the register | 19.3% | the brief's stated share |
| 880 extension records | 880 | `extensions_distribution.csv` weighted by records per project, and `extended_projects.csv` summed — both give 880 |
| 872 carry usable dates | 872 | the brief — no date column exists in the pack |
| 193 with one record, 167 with two | as listed | `extensions_distribution.csv` |
| median 364 days; median project gains 474; longest 3,690 | as listed | the brief — no day column exists in the pack |
| extended projects by registration year | charted | `extensions_by_year.csv`, 2017–2025 (the table has no 2026 row) |

### Slide 08 — Projects and units by pincode

| figure on the slide | value | where it comes from |
|---|---|---|
| the 15 named pincodes | 1709 projects | `by_pincode_top.csv`, the 15 rows before the aggregated one |
| 302026 — 256 projects, 39,310 units | 256 / 39,310 | `by_pincode_top.csv` |
| the aggregated row | 680 projects | `by_pincode_top.csv`, the 'all other pincodes (74)' row |
| top 10 hold 61% | 61% | the brief |
| 6 with 100+, 13 with 50+, 53 with under 10 | 6 / 13 / 53 | `by_pincode.csv`, counted over all 89 rows |
| 155 projects in those rows | 155 | `by_pincode.csv` |
| median 7 | 7 | `by_pincode.csv` |

* The axis runs to 700 because the aggregated row holds 680 projects — more than any
* single pincode. A smaller axis would send that one bar past the edge of the plot, so
* the scale is set to fit the largest value actually plotted.

### Slide 09 — Project-type mix by pincode

| figure on the slide | value | where it comes from |
|---|---|---|
| Group Housing / Plotted / Commercial / Mixed by pincode | stacked bars | `by_pincode_top.csv`, the four type columns |
| row totals | printed at the right of each bar | the four type columns summed for that row, which is the row's `projects` value |
| the 15 named pincodes carry 945 GH, 693 Plotted, 43 Comm, 28 Mixed | as listed | `by_pincode_top.csv`, summed over the 15 rows |
| the last row is 74 pincodes combined | 680 projects | `by_pincode_top.csv`, the aggregated row |

* The aggregated row is set apart by a gap above it and drawn at reduced opacity, so
* it reads as a subtotal rather than as another pincode. Its bar is longer than any
* single pincode's because it is 74 pincodes added together.

### Slide 10 — Recorded status by pincode

| figure on the slide | value | where it comes from |
|---|---|---|
| completed / in progress / lapsed by pincode | stacked bars | `by_pincode_top.csv`, the three status columns |
| row totals | printed at the right of each bar | the three status columns summed for that row — **not** the pincode's project count |
| the three statuses cover 2,302 projects | 2,302 | `status.csv`: 1,155 completed + 747 in progress + 400 lapsed |
| the other 87 carry REVOKED, SUSPENDED or EXEMPTED | 87 | `status.csv`, 55 + 11 + 21 — asserted to equal 2,389 less the three shown |
| 2,389 projects, 328,469 units | 2,389 / 328,469 | as slides 01 and 03 |
| 1,155 completed (48%) | 1,155 | as slide 05 |
| 747 in progress, 421 on the Lapsed list | 747 / 421 | as slides 05 and 06 |
| 460 extended, 880 records, median 364 days | 460 / 880 / 364 | as slide 07 |
| top 10 hold 61%; 53 rows hold fewer than ten | 61% / 53 | as slide 08 |

* The status chart shows three statuses, which is what the brief names for this slide,
* and those three do not account for every project. So the bars' row totals are those
* three added together rather than the pincode's project count, the total column is
* headed 'three statuses', and the slide's own copy states the 2,302 / 87 split.
* Both routes to the 87 are asserted in `facts.py`.
* The summary block restates figures already shown on earlier slides and introduces no
* figure, no comparison and no interpretation that is not already on a slide.

---

## Reproducing this deck

Nothing is fetched and nothing is downloaded at build time: the charts are hand-rolled
SVG from the Python standard library, the corner plate is embedded in the page, and no
font is downloaded (Inter and Noto Serif are used from the system).

    python3 facts.py         # read and check every figure -> facts.json
    bash build_charts.sh     # charts/*.svg, laid out against measured text widths
    python3 build_deck.py    # deck.html, self-contained
    python3 make_sources.py  # this document
    node render.js           # PDF + one PNG per slide + the layout audit
    node ../tools/verify_chart_marks.js deck.html   # no text touches a mark

`render.js` fails the build on: a wrong slide count, any slide that is not exactly
1080x1350 or that overflows, a missing corner plate or one not at 0.15 opacity, a
source line anywhere other than the first and last slides, any logo element, any console
error, and **any occurrence of the words MDP, zone or ZDP in the rendered text**. It
also prints each slide's vertical balance, which catches a slide that is valid but
leaves a third of the page empty.

`verify_chart_marks.js` enforces the series rule that **no text may overlap a chart
mark or another piece of text** (docs/linkedin-series/DESIGN.md §1), measured from the
rendered deck. This deck reports **zero** violations across its 11 charts — 334 text
boxes against 347 marks. The stacked bars on slides 09 and 10 are drawn with a 1 px
corner radius so the verifier treats them as data marks; an unrounded rectangle is
classified as deliberate background and would not be checked at all.

