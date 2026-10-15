# Jaipur RERA, 2017–2026

How the *“2,389 projects on Jaipur's RERA register”* deck was built: the official
Rajasthan RERA register, every endpoint used to reach it, the arithmetic behind each
figure, and the caveats — including the two different definitions of *“lapsed”* that
the portal itself publishes.

**What it covers:** every real-estate project registered with the **Rajasthan Real
Estate Regulatory Authority** in **Jaipur district**, from the authority's first
registration in **2017** to the retrieval date. Geography is the **pincode the
portal records** for each project and the **project type** — no map, no spatial
inference.

| | |
|---|---|
| [`deck/jaipur-rera-2026-linkedin.pdf`](deck/) | the 10-slide deck (PDF; one PNG per slide in `deck/slides/`) |
| [`data/`](data/) | every table behind every figure |
| [`scripts/`](scripts/) | the six-step pipeline that fetches and rebuilds everything |
| [`docs/method.md`](docs/method.md) | every calculation, step by step |
| [`docs/data-sources.md`](docs/data-sources.md) | every endpoint, parameter and field |
| [`docs/caveats.md`](docs/caveats.md) | status definitions, pincode limits, and what we tried and dropped |
| [`docs/verification.md`](docs/verification.md) | the 2026-10-15 re-run, and every row that changed |
| [`docs/figures.md`](docs/figures.md) | every figure traced to its table, slide by slide |
| [`docs/rjgis-layers.md`](docs/rjgis-layers.md) | why the RERA GIS portal shows *two* RERA checkboxes |

---

## Headline figures — Jaipur district

**2,389 projects · 328,469 units declared.**

| Registrations by year | | | |
|---|---:|---:|---:|---:|
| 2017 | **280** | 2018 | 108 |
| 2019 | 107 | 2020 | 112 |
| 2021 | 187 | 2022 | 306 |
| 2023 | 308 | 2024 | 274 |
| 2025 | **456** | 2026 (to date) | 251 |

| Status, as the portal records it | Projects |
|---|---:|
| Completed (incl. completion certificate issued) | **1,155** |
| In progress | 747 |
| Lapsed | **400** *(the portal's own Lapsed list: 421)* |
| Revoked | 55 |
| Suspended | 11 |
| Exempted | 21 |

| Type | Projects | Units declared |
|---|---:|---:|
| Group Housing | **1,248** | 164,955 |
| Plotted | **1,037** | 141,064 |
| Mixed (Residential And Commercial) | 42 | 11,462 |
| Commercial | 62 | 10,988 |

**Extensions:** 460 of 2,389 projects (**19.3 %**) hold at least one; **880
extension records** (872 with usable dates); the median extension is **364 days**
and the median extended project gains **474 days**.

**Pincodes:** 2,387 of 2,389 projects carry one, across **88 pincode values**. The
**top 10 pincodes hold 61 %** of the projects. 6 pincodes hold ≥100 projects; **53
hold fewer than 10**. The type mix differs sharply by pincode — **302017 is 113
Group Housing against 13 Plotted**, while **303904 is 4 Group Housing against 68
Plotted**.

## Reproduce it

```bash
python3 scripts/01_fetch_register.py      # -> work/register.json, work/register_lapsed.json
python3 scripts/02_harvest_status.py      # -> work/details.json      (per-project status + extensions + units)
python3 scripts/03_fetch_pincodes.py      # -> work/pincodes.json     (pincode + city/town/village)
python3 scripts/04_pincode_names.py       # -> data/projects_pincode_city.csv, pincode_names.csv
python3 scripts/05_build_pack.py          # -> data/registrations_*, status, lapsed_*, extensions_*, findings.md
python3 scripts/06_pincode_pack.py        # -> data/by_pincode.csv, by_pincode_top.csv, pincode_summary.md
```

Or `./run_all.sh` for the lot. Steps 02–04 make one request per project (**~5,400
projects ≈ 90 minutes** at the portal's pace); the tables in `data/` are committed,
so every figure can be checked without running anything.

**The pipeline was re-run end to end on 2026-10-15 and all six steps passed** — the
tables moved slightly because the register had grown by six projects in the meantime.
Every difference is listed in [`docs/verification.md`](docs/verification.md), which is
worth reading before you re-run it yourself.

## The two things a reader should know first

1. **“Lapsed” has two definitions on the portal, and they disagree.** The portal's
   own **Lapsed list** returns 421 Jaipur projects; the per-project **status field**
   says 400. The deck leads with 421 and says so. See
   [`docs/caveats.md`](docs/caveats.md#1-two-definitions-of-lapsed).
2. **The register is alive.** It returned **5,408** projects statewide when the deck
   was built and **5,414** a day later. Every figure here is an as-of snapshot; the
   retrieval date is recorded in [`docs/data-sources.md`](docs/data-sources.md).

## Attribution

The data is published by the **Rajasthan Real Estate Regulatory Authority** through
its public portal (`rera.rajasthan.gov.in` / `reraapp.rajasthan.gov.in`) and its GIS
services. This repository redistributes the **derived tables** and the **deck**;
re-run step 01 to obtain the register itself. Not affiliated with or endorsed by the
authority.

Code in `scripts/` is MIT — see [`LICENSE`](LICENSE).
