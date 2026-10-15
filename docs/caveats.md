# Caveats and gotchas

## 1. Two definitions of "lapsed"

The portal publishes two, and they disagree:

| Source | Jaipur | Statewide |
|---|---:|---:|
| The portal's own **Lapsed list** (`ApplicationStatus: 7`) | **421** | 1,208 |
| The per-project **status field** (`StatusOfProject == "LAPSED"`) | **400** | 1,151 |

The deck leads with **421** and prints **400** beside it. The gap is real and not
resolvable from the public data: the list is a register-level classification, the
status field is set per project. **Never add the two together, and never present
one without saying which it is.**

Similarly, *"lapsed"* here means **the registration's validity expired without
completion**. It is the authority's own classification — it is **not** proof that
construction stopped on the ground.

## 2. The register is alive — this is a snapshot

`GetProjects` returned **5,408** projects when the deck was built and **5,414** two
days later. Six new registrations. Every figure in `data/` is as of **2026-10-13**.

Re-running the pipeline gives slightly different totals. That is correct behaviour.
Quote the deck's figures with their date, or re-run and re-date them.

## 3. 880 extension records, 872 with usable dates

`GetPreviousExtsList` returned **880** rows across Jaipur. **872** of them have both
`ExtensionFromDt` and `ExtensionToDt` parseable and ordered. An early draft printed
one number as the other and the distribution table caught it. **Both numbers are
now stated** and they are different things.

Also: extension lengths are **sums of the portal's own periods**. A project can have
one five-year block (see the `Felicity Irene Usha Tower` example in
[`method.md`](method.md#worked-example--the-longest-extension-on-record)) rather
than ten annual renewals — the totals are still exact, but "3,690 days of extension"
should not be read as "ten renewals".

## 4. The spatial route we dropped

The obvious way to make this richer is to place each project on the map and report
it by planning zone. We built it, and then **discarded it**. The reasons are worth
recording:

- **Only ~40 % of Jaipur projects are locatable.** Of 2,389, just **949** have any
  machine-readable geometry the portal publishes (RJGIS polygon, RJGIS point,
  server latitude/longitude, or a real KML). **795** of those fall inside the MDP.
  Reporting "MDP zone" would silently describe a third of the register.
- **The `kmlfile` link is unreliable.** For **1,329** projects it does not serve a
  KML at all — it serves a **PDF**. One sampled file was a 763-page iLovePDF document
  bundle. `is_kml_file` and `IsKMLUpdated` do **not** reliably tell you which.
- **Coverage is wildly uneven by year**: 99 % of 2026 registrations are locatable
  against 14 % of 2024's — so a zonal cut is also a distortion of *time*.
- **The two RERA GIS layers are different datasets, not a point/polygon pair** — they
  have disjoint id ranges and cover different eras. See
  [`rjgis-layers.md`](rjgis-layers.md).

**The pincode is the better geography here**: it is present for **2,387 of 2,389**
projects, it needs no inference, and it is a field the portal states. The exploratory
scripts are kept in [`../scripts/explored/`](../scripts/explored/) for anyone who
wants to see the attempt.

## 5. A pincode is postal, not planning

It does not correspond to an MDP zone, a ward or any administrative boundary, and
the deck never implies it does. Two further data notes:

- **2 projects carry no pincode at all** (2,387 of 2,389 do).
- **5 projects carry a pincode outside Jaipur's ranges** (`302xxx` / `303xxx`) — two
  read as Jodhpur (`342001`) and Sikar (`332718`) values against Jaipur localities,
  which are promoter data-entry slips. They are left in place and not corrected;
  correcting them would be us editing the source.

## 6. 2026 is a partial year

The deck's 2026 figure is **251 projects** as of the retrieval date — eight and a
half months. It must not be read as a decline against 2025's 456.

## 7. Units are declared, not certified

`total_units` is the promoter's count on the registration. It is complete across the
register (every project reports one), which is why it is used — but it is a declared
figure, not a verified one.

## 8. Status-taxonomy quirks

- **`COMPLETED & OC ISSUED ` carries a trailing space** on the server. Without
  `.strip()` it becomes a second category and the counts break.
- **An unknown `ApplicationStatus` code is silently ignored** by `GetProjects` and
  the endpoint returns **all** projects. A wrong filter therefore looks like a valid
  full response. Always check the row count, not just that you got data.
- The register's `ProjectStatus` (`3`/`5`/`6`) and the detail page's
  `StatusOfProject` (strings) are **different fields with different vocabularies**.
  The deck uses the detail page's, because it is the more granular one.

## 9. The register has no coordinates or pincode

`GetProjects` gives district and a **numeric** `Taluka` code only. Pincode, city,
tehsil name, khasra and coordinates all require one detail request **per project** —
which is why the pipeline is slow and why the register alone cannot answer a
geographic question.

## 10. Be considerate with the API

The harvest makes **one POST and ~5,400 GETs per full run**. It is a public service;
the scripts use modest concurrency and retries. Do not hammer it, and do not run the
full pipeline repeatedly for no reason — the resulting tables are committed.

The register API's `X-API-KEY` is a **static value embedded in the portal's own
JavaScript bundle**. It is reproduced in `scripts/01_fetch_register.py` because the
endpoints cannot be called without it. It is a client-side value, not a credential
of ours, and it may change without notice.

## 11. Attribution

The data is published by the **Rajasthan Real Estate Regulatory Authority** via its
public portal and GIS services. This repository is not affiliated with or endorsed
by the authority.
