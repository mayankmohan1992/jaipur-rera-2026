# Why the RERAGIS portal has two checkboxes: "Project Point" and "Project Polygon"

Investigated 2026-10-13 against the live portal
(https://rajdharaa.rajasthan.gov.in/RERAGIS/index.html). The app registers a
public GIS token via `POST /RajdharaaCommonWebAPI/api/GenerateGISToken` and then
loads two **independent** FeatureLayers from the same service:

| app layer / checkbox | service | geometry | `PROJECT_ID` | rows |
|---|---|---|---|---|
| **Rera** ("Project Point") | `dynamicquery/…/Rera/Rera/FeatureServer/**0**` | Point | **24 – 13,714** | 1,385 |
| **Rera Polygon** ("Project Polygon") | `…/Rera/Rera/FeatureServer/**1**` | Polygon | **11,990 – 16,092** | 1,076 |

Defined in `js/Config.js` (`Rera`, `ReraPolygon`) and built in `js/layerConfig.js`.

## They are two different datasets, not one layer's point + polygon

- **Different id spaces.** Point ids run 24–13,714; polygon ids 11,990–16,092.
  Only **7 ids statewide** overlap (2 in Jaipur).
- **Different eras.**
  - The **point** layer's `REGISTRATION_NO` years are **2017–2025** (333 in
    2017 … 108 in 2025; only **2** from 2026). It was bulk-created on a single
    day (**2026-04-17**) and never edited — a one-off location backlog for the
    historic registry.
  - The **polygon** layer was created **2026-03-18 → 2026-10-13** and is still
    being edited — an actively-growing area layer. Its ids are in the same id
    space as the current register: **182 of the 246** Jaipur projects
    registered 2026+ have a polygon there.
- **Different attributes.**
  - Point-only: `APPLICATION_NO`, `REGISTRATION_NO`, `TOTAL_BUILDING_COUNT`,
    `PINCODE`, `IMAGE_AREA`.
  - Polygon-only: `TOTAL_UNITS`, computed `Shape__Area` / `Shape__Length`.
- **Different geometry purpose & category mix.** Points skew **Group Housing**
  (695 vs 593 Plotted statewide) — a tower needs a marker, not a boundary.
  Polygons skew **Plotted** (827 vs 205) — a layout needs its outline drawn.
- **Different popups.** The point popup calls
  `reraapp.rajasthan.gov.in/Home/GetDetailsbyProjectId?REFID_id=<PROJECT_ID>`
  for live detail (state, district, city, pincode, khasra, lat/lon, project
  image) — it's the "click a project, see everything" layer. The polygon popup
  shows the area layer's own attributes.

So the two checkboxes toggle **a historical location dataset** and **a current
boundary dataset** — different coverage, keys, fields and vintage — not two
representations of one layer.

## The point layer is genuinely geocoded

Jaipur: 560 points, 557 distinct coordinates (only ~1 % share a coordinate with
another point), spread across tehsils (Sanganer 286, Jaipur 218, …). So they are
per-project locations, not tehsil/pincode centroids.

## Impact on the LinkedIn series

- Our pipeline (`source-data/rera_portal/extract_rera_portal.py`,
  `tools/pull_layers.py`, `verify_counts.py`) uses **only FeatureServer/1**, the
  polygon layer. We never used the point layer.
- This explains the deck's "no polygon" projects: they are **recent (2026+)
  registrations whose site boundary has not been digitised yet**, not projects
  placed somewhere else. The point layer cannot rescue them — it covers the
  2017–2025 registry, not 2026.
- The earlier statement "the register carries no coordinates" holds for the
  portal register/detail APIs we pull; coordinates *do* exist for the older
  registry in this GIS point layer.
