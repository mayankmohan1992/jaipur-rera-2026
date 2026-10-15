# Placing the "unplaceable" RERA projects from their KML

Investigated 2026-10-13. Every RERA project page carries a promoter-supplied
KML in `GetDetailsbyProjectId` → `kmlfile`. We pulled the KML for all **66**
Jaipur 2026 projects that had no RJGIS polygon (our deck's "unplaced" set) and
tested each against `data/mdp_data.js`.

## What the KMLs actually are
Two shapes, not one:
- a real **boundary** (Polygon/LineString, many vertices) — 51 of 66;
- just a marker **Point** (one coordinate) — 12 of 66;
- **no geometry at all** — 3 (`MACHWA COMMERCIAL`, `Dhun Life Phase 1`, `EVOKE`).

19 of the files are KMZ (zipped KML) and must be unzipped.

## Result (script: `rera/kml_place.py`, output: `rera/data/unplaced_kml_placement.csv`)

| outcome | projects |
|---|---|
| **inside the MDP, named zone** | **43** |
| inside the MDP, unlabelled polygon | 2 |
| **outside the MDP** | **18** |
| no geometry in the KML | 3 |

Zones recovered: ZDP-16 15 · ZDP-15 11 · ZDP-10 5 · ZDP-11B 4 · ZDP-08 2 ·
ZDP_02 2 · ZDP-13 2 · ZDP-01 1 · ZDP-05 1.

The 18 "outside" are genuinely outside: 1.3 km from the MDP edge at the nearest
(FINETECH INDUSTRIAL ESTATE) up to **24 km** west (Raj Vihar 3, the Mansukh /
Dudu group around lon 75.18–75.26). They are Jaipur-district registrations
beyond the MDP boundary, not a geometry error.

## Consequence for the RERA deck
The deck says **132 placed / 64 unplaced**. With the KML the Jaipur-MDP set
becomes **175 inside the MDP (173 with a named zone)**, **18 outside** (properly
excluded), and only **3** genuinely undetermined. The "unplaceable 64" headline
should be corrected before this deck is posted.
