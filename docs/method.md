# Method — how every figure is calculated

Six steps, in order. Everything downstream of step 1 is a grouping or an
arithmetic operation on server fields; nothing is modelled or inferred.

```
01_fetch_register.py   POST GetProjects {}            -> work/register.json, register_lapsed.json
02_harvest_status.py   1 request per project          -> work/details.json
03_fetch_pincodes.py   1 request per project          -> work/pincodes.json
04_pincode_names.py    1 request per project          -> data/projects_pincode_city.csv, pincode_names.csv
05_build_pack.py       grouping + arithmetic          -> data/registrations_*, status, lapsed_*, extensions_*
06_pincode_pack.py     grouping by pincode            -> data/by_pincode*.csv
```

Steps 02–04 are one request per project (~5,400 ⇒ ~90 minutes). Every script is
idempotent: re-running resumes or overwrites cleanly.

---

## 1. Scope — Jaipur district

```
jaipur = [r for r in register if r["DistrictName"] == "Jaipur"]
```

**2,389 of the 5,408** registered projects. `DistrictName` is the register's own
field — the string `Jaipur`, exactly.

## 2. Registrations by year

```
year(project) = r["APPROVEDON"][:4]          # e.g. "2026-10-13T10:44:03.647" -> "2026"
```

→ [`../data/registrations_by_year.csv`](../data/registrations_by_year.csv)

`APPROVEDON` is the **registration date**, the date the authority approved the
project. It is not the application date, the start of construction or the
completion date. 2026 is **partial** — eight and a half months of the year at the
retrieval date — and the deck labels it as such.

## 3. Status — and why "lapsed" has two answers

The register and the detail page disagree, and both are official:

| Source | Field | Jaipur count |
|---|---|---:|
| The portal's own **Lapsed list** (`ApplicationStatus: 7`) | — | **421** |
| The per-project detail page | `StatusOfProject == "LAPSED"` | **400** |

The first is a register-level list the authority maintains; the second is a status
field the authority sets. They are close but not identical, so the deck quotes
**421** (the Lapsed list) on the lapse slide and states the 400 alongside it.

The rest of the taxonomy, from `StatusOfProject`:

```
status(project) = r["status"].strip()          # note: the server pads one value
COMPLETED = status contains "COMPLETED"        # matches both:
                                               #   "COMPLETED"
                                               #   "COMPLETED & OC ISSUED "   <- trailing space
```

- **Completed = 1,155** — `COMPLETED` (1,006) + `COMPLETED & OC ISSUED` (149).
  These are counted together because both mean the project is recorded as finished;
  the second additionally has an occupancy certificate on file.
- The remaining values are used verbatim: `INPROGRESS` 747, `LAPSED` 400,
  `REVOKED` 55, `SUSPENDED` 11, `EXEMPTED` 21.

`.strip()` matters: the server's `COMPLETED & OC ISSUED ` carries a trailing space,
which would otherwise split the category in two.

## 4. Extensions

`GetPreviousExtsList` returns one object per extension, each with an
`ExtensionFromDt` and `ExtensionToDt` as ASP.NET `/Date(<epoch ms>)/` strings.

```
extension_records = Σ len(project.GetPreviousExtsList)              -> 880
dated_periods     = records where both dates parse and to > from    -> 872

period_days   = (to_ms - from_ms) / 86_400_000
project_total = Σ period_days over that project's extensions
```

| Figure | Value |
|---|---:|
| Projects with ≥1 extension | **460** (19.3 % of 2,389) |
| Extension records | **880** |
| Of those, carrying usable dates | **872** |
| Median single extension | **364 days** |
| Median project's total extension | **474 days** |
| Longest single project | **3,690 days** |

**The two counts are reported separately on purpose.** 880 is the number of
extension rows the portal lists; 872 is how many of them have both dates usable.
An earlier draft printed 872 as "extension periods" while the distribution table
summed to 880 — an eight-record discrepancy that took a verification pass to find.
Both are now stated.

### Worked example — the longest extension on record

`Felicity Irene Usha Tower` (Jaipur, Group Housing, `RAJ/P/2017/119`, registered
2017-08-30) carries six extensions:

| From | To | Days |
|---|---|---:|
| 2017-11-17 | 2018-11-16 | 364 |
| 2018-11-17 | 2023-11-16 | **1,825** |
| 2023-11-17 | 2024-08-30 | 287 |
| 2024-08-31 | 2025-08-29 | 363 |
| 2025-08-30 | 2027-08-29 | 729 |
| 2027-08-29 | 2027-12-29 | 122 |
| | **total** | **3,690** |

Note the total is a **sum of the periods the portal records** — and one block is
five years on its own. 3,690 days is therefore not "ten separate one-year
renewals"; it is six rows, one of which is very long.

### Worked example — the headline percentages

```
Completed   1,155 / 2,389 = 48.35 %   -> 48 %
Lapsed        421 / 2,389 = 17.62 %   -> ~18 %   (Lapsed-list definition)
Group Hsg   1,248 / 2,389 = 52.24 %   -> 52 %
```

## 5. Units

```
units(project) = int(float(r["units"]))        # from GetDetailsbyProjectId.total_units
total          = Σ units over all 2,389        -> 328,469
```

Units are the promoter's **declared** count on the registration, not a certificate
of what was built. Every project reports one, so the total is complete across the
register — which is what makes it the reliable size measure for this dataset.

## 6. Pincode — the geography used

```
pincode(project) = GetDetailsbyProjectId.PinCode
```

**2,387 of 2,389** projects carry one (2 do not), across **88 pincode values** —
plus one row for the 2 with none, so the table has 89 rows. Projects are grouped by
that value, and within each group by:

```
type   = register.ProjectTypeName
status = detail.StatusOfProject   (the taxonomy in §3)
units  = detail.total_units
ext    = whether len(detail.GetPreviousExtsList) > 0
```

The deck shows the **top 15** pincodes and aggregates the remaining 74 into one
"all other pincodes (74)" row, because **53 of the 88 values hold fewer than 10
projects each** and a per-pincode type breakdown is not meaningful at that size.

### Worked example — the pincode contrast the deck is built on

| Pincode | Projects | Group Housing | Plotted |
|---|---:|---:|---:|
| 302017 | 133 | **113** | 13 |
| 303904 | 72 | 4 | **68** |

Both are simple counts of `ProjectTypeName` within the pincode group. The deck
reports them as counts and does not explain the difference.

## 7. What is *not* calculated

- **No geography beyond the pincode.** No map, no spatial join, no zones. (The
  spatial route was tried and dropped — see [`caveats.md`](caveats.md#4-the-spatial-route-we-dropped).)
- **No rates, no price, no value.** The register has no transaction data.
- **No completion-date analysis.** `RevisedDateOfComplation` exists but records on
  it are not consistent enough to support a claim (many sit in the past for projects
  still marked in progress), so the deck does not use it.
- **No interpretation of why.** The deck reports what the portal records. It does
  not explain the 2017 spike, the lapse pattern or the pincode contrast.
