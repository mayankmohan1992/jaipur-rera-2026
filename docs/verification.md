# Verification — re-running the pipeline

The whole pipeline was re-run end to end on **2026-10-15**, two days after the deck
was built, to confirm that the scripts in [`../scripts/`](../scripts/) actually
reproduce the tables in [`../data/`](../data/).

**All six steps completed without error.** The tables did not come back
byte-identical — and that is the correct result, because **the register is a live
dataset that grew by six projects in the intervening two days.** Every difference
below is explained by that, and every difference is small.

This document records the full comparison so nothing is hidden behind a claim of
"reproduces".

## What moved

| | at deck build (2026-10-13) | at verification (2026-10-15) |
|---|---:|---:|
| Register, statewide | 5,408 | **5,414** |
| Register, Jaipur district | 2,389 | **2,390** |
| Lapsed list, Jaipur | 421 | 420 |
| Units declared | 328,469 | 328,677 |
| Extension records | 880 | 881 |
| Registrations, 2026 | 251 | 252 |
| Plotted projects | 1,037 | 1,038 |
| Completed | 1,006 + 149 OC = 1,155 | 1,008 + 149 OC = 1,157 |
| `StatusOfProject = LAPSED` | 400 | 399 |

## Row-by-row differences

| file | change |
|---|---|
| `registrations_by_year.csv` | 2026: 251 → **252** |
| `registrations_by_type.csv` | PLOTTED: 1,037 → **1,038** |
| `status.csv` | COMPLETED 1,006 → 1,008 · LAPSED 400 → **399** |
| `lapsed_by_year.csv` | 2024: 45/31 → **44/30** |
| `lapsed_by_type.csv` | Commercial: 14 → **13** |
| `extensions_distribution.csv` | 1 extension: 193 → 192 · 2 extensions: 167 → **168** |
| `completed_by_year.csv` | 2024: 145 → **147** |
| `by_pincode.csv` | 89 → **88 rows** (see below) |
| `projects_pincode_city.csv` | `Gulmohar Plaza Sarthi Shops` **gained a pincode** (302017, Manpur Bhatawala) — it had none at deck build |
| `extended_projects.csv` | `Palmera Garden Phase - 1` **INPROGRESS → COMPLETED**; `Commercial Scheme of Khasra No.74,73(Part) & 66(part)` gained a second extension (1 → **2**) |
| `lapsed_projects.csv` | 421 → **420 rows** |

Two of these are worth calling out because they show the data is being *maintained*,
not just appended to:

- **A project's status advanced** — `Palmera Garden Phase - 1` moved from
  `INPROGRESS` to `COMPLETED` between the two runs.
- **A project gained a pincode** — `Gulmohar Plaza Sarthi Shops` had an empty
  pincode at deck build and now reports `302017`. So the "2 projects with no pincode"
  in the deck is a snapshot, not a permanent defect.

## The one structural difference

`by_pincode.csv` has **89 rows at deck build and 88 at verification**, and the
*composition* of the top 15 changed:

- **`303007` (44 projects) entered the top 15**, displacing **`302001` (43)**.
- The two counts differ by one project — the table is simply cut at 15, and the
  15th/16th boundary is that tight.

So the deck's pincode ranking is a **snapshot of a moving ordering**, not a fixed
fact. Re-running will reshuffle the bottom of the top-15 whenever two pincodes are
within a project or two of each other.

## What this means for the committed tables

`data/` holds the **deck's own tables** (as of **2026-10-13**) so that every figure
in the deck can be checked against them — that is the point of this repository.

If you re-run the pipeline you will get the newer numbers above, and your tables
will differ from the deck's. **That is expected.** Pin the date when you quote a
figure, or re-date the deck.

## Script bugs found and fixed while setting this up

Recorded because they are the kind of thing that silently produces a wrong table:

1. An undefined variable in a fetch script's output path — it failed loudly.
2. The register was being saved as a bare list while the downstream scripts expected
   the API's `{"Data": [...]}` envelope — also a loud failure.
3. A path that only resolved when the script was run from one particular directory.

The re-run above is the check that all three are fixed.
