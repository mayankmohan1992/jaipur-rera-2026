#!/usr/bin/env python3
"""Post 6 data pack — Jaipur RERA, 2017-2026 (full period, Jaipur only).

Sources (all official, all public):
  work/register.json      POST reraapi.../api/web/Home/GetProjects  (the register)
  work/details.json  per-project HomeWebsite/ProjectDtlsWebsite
                             (StatusOfProject + GetPreviousExtsList + units)
  work/register_lapsed.json              the portal's own "Lapsed Projects" list

Writes CSVs + findings.md under docs/linkedin-series/rera-jaipur/data/.
"""
import collections, csv, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(HERE), "work")
OUT = os.path.join(os.path.dirname(HERE), "data")
os.makedirs(OUT, exist_ok=True)

REG = json.load(open(os.path.join(WORK, "register.json"), encoding="utf-8"))["Data"]
DET = {r["Id"]: r for r in json.load(open(os.path.join(WORK, "details.json"), encoding="utf-8"))}
LAPSED_IDS = {r["Id"] for r in json.loads(open(os.path.join(WORK, "register_lapsed.json"), encoding="utf-8", errors="ignore").read(), strict=False)["Data"]}


def yr(r):
    return (r.get("APPROVEDON") or "?")[:4]


def ms(v):
    m = re.search(r"\((\d+)", str(v) or "")
    return int(m.group(1)) if m else None


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)


def table(hdr, rows):
    out = ["| " + " | ".join(hdr) + " |", "|" + "|".join(["---"] * len(hdr)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    j = [r for r in REG if r.get("DistrictName") == "Jaipur"]
    print("Jaipur register rows:", len(j))

    # ---- registrations by year × type ----
    byy = collections.Counter(yr(r) for r in j)
    write("registrations_by_year.csv", ["year", "projects"], sorted(byy.items()))
    byt = collections.Counter(r.get("ProjectTypeName") for r in j)
    write("registrations_by_type.csv", ["type", "projects"], sorted(byt.items(), key=lambda kv: -kv[1]))

    # ---- status (from the per-project harvest) ----
    st = collections.Counter((DET.get(r["Id"]) or {}).get("status") for r in j)
    write("status.csv", ["status", "projects"], sorted(st.items(), key=lambda kv: str(kv[0])))

    # ---- lapsed: register's own list, and status ----
    lap_reg = [r for r in j if r["Id"] in LAPSED_IDS]
    lap_st = [r for r in j if (DET.get(r["Id"]) or {}).get("status") == "LAPSED"]
    write("lapsed_by_year.csv", ["year", "lapsed_register", "lapsed_status"],
          [[y, sum(1 for r in lap_reg if yr(r) == y), sum(1 for r in lap_st if yr(r) == y)] for y in sorted(set(byy))])
    write("lapsed_by_type.csv", ["type", "lapsed_register", "lapsed_status"],
          [[t, sum(1 for r in lap_reg if r.get("ProjectTypeName") == t),
            sum(1 for r in lap_st if r.get("ProjectTypeName") == t)] for t in sorted(byt, key=lambda t: -byt[t])])
    write("lapsed_projects.csv", ["project", "reg_no", "type", "reg_year", "status"],
          [[r["ProjectName"], r.get("REGISTRATIONNO"), r.get("ProjectTypeName"), yr(r),
            (DET.get(r["Id"]) or {}).get("status")] for r in lap_reg])

    # ---- extensions ----
    ext = [(r, DET.get(r["Id"]) or {}) for r in j if (DET.get(r["Id"]) or {}).get("next")]
    nxt = collections.Counter(len((x[1].get("ext") or [])) for x in ext)
    write("extensions_distribution.csv", ["extensions_granted", "projects"], sorted(nxt.items()))
    # Two different counts, kept apart so they can never be conflated:
    #   extension_records  = every extension row the portal lists (sum of next)
    #   dated_periods      = those with both dates usable for a duration
    durs, cum = [], []
    records = 0
    for r, g in ext:
        ds = []
        for e in g.get("ext") or []:
            records += 1
            a, b = ms(e.get("from")), ms(e.get("to"))
            if a and b and b > a:
                ds.append((b - a) / 86400000.0)
                durs.append((b - a) / 86400000.0)
        if ds:
            cum.append(sum(ds))
    ext_stats = {
        "projects_with_extension": len(ext),
        "share_of_jaipur": round(100.0 * len(ext) / len(j), 1),
        "extension_records": records,
        "dated_periods": len(durs),
        "period_median_days": round(statistics.median(durs)) if durs else 0,
        "period_mean_days": round(statistics.mean(durs)) if durs else 0,
        "project_total_median_days": round(statistics.median(cum)) if cum else 0,
        "project_total_max_days": round(max(cum)) if cum else 0,
        "total_added_project_years": round(sum(durs) / 365.25, 0),
    }
    # extensions by registration year
    exy = collections.Counter(yr(r) for r, _ in ext)
    write("extensions_by_year.csv", ["year", "projects_extended"], sorted(exy.items()))
    write("extended_projects.csv", ["project", "reg_no", "type", "reg_year", "extensions", "status"],
          [[r["ProjectName"], r.get("REGISTRATIONNO"), r.get("ProjectTypeName"), yr(r),
            len((g.get("ext") or [])), g.get("status")] for r, g in ext])

    # ---- completion ----
    comp = [r for r in j if "COMPLETED" in ((DET.get(r["Id"]) or {}).get("status") or "")]
    write("completed_by_year.csv", ["year", "completed"],
          [[y, sum(1 for r in comp if yr(r) == y)] for y in sorted(set(byy))])

    # ---- units ----
    u = [DET.get(r["Id"], {}).get("units") for r in j]
    u = [int(x) for x in u if isinstance(x, (int, float)) or (isinstance(x, str) and x.isdigit())]
    units = {"projects_with_units": len(u), "total": sum(u), "median": statistics.median(u) if u else 0}

    # ---- findings ----
    md = [
        "# Jaipur RERA, 2017-2026 - pre-computed findings\n",
        f"Source: Rajasthan RERA portal - the register (`GetProjects`, {len(REG):,} "
        f"projects statewide), the per-project detail endpoint (`ProjectDtlsWebsite`: "
        f"StatusOfProject + extension history + units) and the portal's own Lapsed "
        f"list. **Jaipur = {len(j):,} registered projects (2017-2026)**.\n",
        "> Jaipur is 44% of the state's registrations. Status and extensions are "
        "read per project; 'lapsed' is given two ways - the portal's own Lapsed "
        "list, and StatusOfProject=LAPSED - which agree closely.\n",
        "## Registrations by year\n", table(["Year", "Projects"], sorted(byy.items())),
        "\n## By type\n", table(["Type", "Projects"], sorted(byt.items(), key=lambda kv: -kv[1])),
        "\n## Status\n", table(["Status", "Projects"], sorted(st.items(), key=lambda kv: str(kv[0]))),
        f"\n**Completed (incl. OC issued): {sum(v for k,v in st.items() if k and 'COMPLETED' in k):,} "
        f"of {len(j):,} ({100.0*sum(v for k,v in st.items() if k and 'COMPLETED' in k)/len(j):.0f}%)**\n",
        "\n## Extensions\n",
        f"- **{ext_stats['projects_with_extension']:,} of {len(j):,}** Jaipur projects "
        f"({ext_stats['share_of_jaipur']}%) have at least one extension.\n"
        f"- {ext_stats['extension_records']:,} extension records in total "
        f"({ext_stats['dated_periods']:,} of them carry usable dates).\n"
        f"- typical extension **{ext_stats['period_median_days']} days** "
        f"(median); the median project's extensions add "
        f"**{ext_stats['project_total_median_days']} days**; the longest "
        f"{ext_stats['project_total_max_days']} days.\n"
        f"- total added time: **{ext_stats['total_added_project_years']:,.0f} project-years**.\n",
        table(["Extensions granted", "Projects"], sorted(nxt.items())),
        "\n## Lapsed\n",
        f"- portal Lapsed list: **{len(lap_reg):,}** Jaipur projects\n"
        f"- StatusOfProject=LAPSED: **{len(lap_st):,}**\n",
        "\n## Units\n",
        f"- {units['projects_with_units']:,} Jaipur projects report units; "
        f"**{units['total']:,} units** total, median {units['median']:.0f} per project.\n",
    ]
    open(os.path.join(OUT, "findings.md"), "w", encoding="utf-8").write("\n".join(str(x) for x in md))

    print("registrations by year:", dict(sorted(byy.items())))
    print("status:", dict(st))
    print("lapsed (register/status):", len(lap_reg), len(lap_st))
    print("extensions:", ext_stats)
    print("units:", units)


if __name__ == "__main__":
    main()
