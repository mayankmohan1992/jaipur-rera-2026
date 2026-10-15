# Data sources — every endpoint used

Four public endpoints, on two hosts, plus the RERA GIS layers. No login, no API
account — but the register API does require a static key header, and the GIS layers
require a token (see [`rjgis-layers.md`](rjgis-layers.md)).

| Host | What it serves |
|---|---|
| `reraapi.rajasthan.gov.in` | the JSON API: the project register |
| `reraapp.rajasthan.gov.in` | the project detail pages (status, extensions, units, KML) |
| `gisprod.rajasthan.gov.in` | the RERA GIS layers (area polygons, location points) |

---

## 1. The register — `GetProjects`

**This is the master list.** Every script joins to it.

```http
POST https://reraapi.rajasthan.gov.in/api/web/Home/GetProjects
Content-Type: application/json
X-API-KEY: <static key carried in the portal's own JS bundle>

{ }
```

Returns **all** projects in the state — **5,408** at the time the deck was built
(5,414 the following day).

### Filtering by status

The same endpoint takes a status filter, and this is exactly how the portal's own
**Lapsed / Suspended / Revoked** pages are built:

| Body | Projects (statewide) | Meaning |
|---|---:|---|
| `{}` | 5,408 | everything |
| `{"ApplicationStatus": 5}` | 106 | **revoked** |
| `{"ApplicationStatus": 6}` | 21 | **suspended** |
| `{"ApplicationStatus": 7}` | **1,208** | **lapsed** |

Any other value returns the full set, i.e. the filter is ignored — so a wrong
guess silently looks like "all projects". Verify the count, not just the response.

### Fields on every row

| Field | What it is |
|---|---|
| `Id` | numeric project id — **the join key** to the detail endpoints and the GIS layers |
| `EncryptedProjectId` | opaque id used by the detail endpoints |
| `REGISTRATIONNO`, `ApplicationNo` | e.g. `RAJ/P/2026/5473`, `RAJ-RERA-APP-P-2026-12269` |
| `APPROVEDON` | **registration date** — the basis of the by-year series |
| `ProjectName`, `PromoterName`, `ORGNAME`, `ContactPersonName` | project and promoter |
| `ProjectTypeName`, `ProjectType` | `PLOTTED`, `GROUP HOUSING`, `Commercial`, `Mixed (…)` |
| `DistrictName`, `Taluka` | geography available *in the register* — Taluka is a **numeric code**, not a name |
| `ProjectStatus`, `AppStatus` | `3` = approved (5,281), `5` = revoked (106), `6` = suspended (21) |
| `CertificateNo` | registration certificate number and date |
| `RevisedDateOfComplation` | the completion date currently on record |
| `RevisedCertiRC` | flag: a revised registration certificate exists (`1` on 482 projects) |
| `IsCCUploaded` | completion certificate uploaded (`True` on 92 projects) |
| `UpdatedOn`, `SendToAdminOn`, `DayCount` | workflow timestamps |

**The register carries no coordinates, no pincode and no tehsil name.** Those must be
fetched per project (below).

## 2. Per-project status and extension history — `ProjectDtlsWebsite`

```http
GET https://reraapp.rajasthan.gov.in/HomeWebsite/ProjectDtlsWebsite/<EncryptedProjectId>
```

This is the page the portal itself renders. It carries the two fields the deck needs
that the register lacks:

| Field | What it is |
|---|---|
| **`StatusOfProject`** | `INPROGRESS` · `COMPLETED` · `COMPLETED & OC ISSUED ` · `LAPSED` · `REVOKED` · `SUSPENDED` · `EXEMPTED` — **note the trailing space** on `COMPLETED & OC ISSUED ` |
| **`GetPreviousExtsList`** | **the extension history** — one object per extension, each with `ExtensionFromDt` and `ExtensionToDt` (ASP.NET `/Date(ms)/` strings) |
| `DateofRegistration`, `RevisedDateOfComplation` | dates as `dd-mm-yyyy` strings here (the register uses ISO) |
| `PhaseArea`, `TotalBuildingCount`, `SanctionedbuildingCount` | scale |
| `ProjectLocation` | the free-text address (khasra / plot numbers, village) |

Also returned but not used: `GetQPRList`, `GetEncumbranceList`, `GetAPRList`,
`GetMapRevision*`, `GetSpecialModProjectList`, document lists.

## 3. Units, coordinates and the KML — `GetDetailsbyProjectId`

```http
GET https://reraapp.rajasthan.gov.in/Home/GetDetailsbyProjectId?REFID_id=<Id>
```

Note this one takes the **numeric `Id`**, not the encrypted one.

| Field | What it is |
|---|---|
| **`total_units`** | units declared by the promoter — the source of the 328,469 figure |
| `Latitude`, `Longitude` | present for a minority of projects (`None` on most) |
| **`kmlfile`** | a URL — but see the caveat: it often serves a **PDF**, not a KML |
| `is_kml_file`, `IsKMLUpdated` | flags that do **not** reliably indicate the file type |
| `StateName`, `DistrictName`, `CityTownVillage`, `PinCode`, `PlotKhasraNo` | the address block — **the source of the pincode the deck groups on** |
| `category_name`, `project_subtype`, `total_no_of_floors`, `phase_area` | attributes |

One request per project. **This is the slow step** (~90 minutes for ~5,400 projects).

## 4. The RERA GIS layers

Two independently-built layers, explained in [`rjgis-layers.md`](rjgis-layers.md):

| Layer | URL | Geometry | Rows |
|---|---|---|---|
| Rera Project Areas | `…/dynamicquery/rest/services/Rera/Rera/FeatureServer/**1**` | polygon | 1,076 |
| Rera Project Locations | `…/dynamicquery/rest/services/Rera/Rera/FeatureServer/**0**` | point | 1,385 |

Token-gated — `POST https://rajdharaa.rajasthan.gov.in/RajdharaaCommonWebAPI/api/GenerateGISToken`
returns one token per service, and these layers need the **`dynamicquery`** token.
An empty POST needs `Content-Length: 0` or you get **HTTP 411**.

---

## Retrieval log

| Date | What | Rows |
|---|---|---:|
| 2026-10-13 | register (statewide) | 5,408 |
| 2026-10-13 | register, `ApplicationStatus: 7` (lapsed) | 1,208 |
| 2026-10-13 | per-project detail (status + extensions + units) | 5,408 |
| 2026-10-13 | pincode + city/town/village | 2,389 (Jaipur) |
| 2026-10-14 | pincode → place names | 2,389 (Jaipur) |
| **2026-10-15** | **register re-fetched while verifying this repository** | **5,414** |

**The register grows.** Six new registrations appeared in the two days between the
deck's pull and this repository's verification. Every figure in `data/` is an
as-of snapshot of **2026-10-13**; re-running the pipeline will return slightly
different totals, and that is the correct behaviour, not a bug.
