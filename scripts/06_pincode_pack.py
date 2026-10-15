#!/usr/bin/env python3
"""Pincode pack for the Jaipur RERA deck (replaces the MDP view).

Every value is a server fact: the pincode the portal records for the project
(Home/GetDetailsbyProjectId), the register's type/date, and the per-project
detail page's status and extension list.

Writes to docs/linkedin-series/rera-jaipur/data/:
  by_pincode.csv          pincode x projects/units/type-mix/status
  by_pincode_top.csv      the top 15 pincodes, then one "all other" row
  pincode_summary.md      the tables the deck quotes
"""
import collections, csv, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(HERE), "work")
OUT = os.path.join(os.path.dirname(HERE), "data")
os.makedirs(OUT, exist_ok=True)

DET = {r["Id"]: r for r in json.load(open(os.path.join(WORK, "details.json"), encoding="utf-8"))}
PC = json.load(open(os.path.join(WORK, "pincodes.json"), encoding="utf-8"))

TYPES = ["GROUP HOUSING", "PLOTTED", "Commercial", "Mixed (Residential And Commercial)"]
STATUSES = ["COMPLETED", "INPROGRESS", "LAPSED", "REVOKED", "SUSPENDED", "EXEMPTED"]


def st(r):
    s = (r.get("status") or "").strip()
    return "COMPLETED" if "COMPLETED" in s else s


def units(r):
    try:
        return int(float(r.get("units")))
    except (TypeError, ValueError):
        return 0


def main():
    rows = list(PC.values())
    by = collections.defaultdict(list)
    for r in rows:
        by[str(r.get("pincode") or "(no pincode)")].append(DET.get(r["Id"], {}))
    recs = []
    for p, items in by.items():
        t = collections.Counter((i.get("type") or "").strip() for i in items)
        s = collections.Counter(st(i) for i in items)
        ext = sum(1 for i in items if (i.get("next") or 0) > 0)
        recs.append({
            "pincode": p, "projects": len(items), "units": sum(units(i) for i in items),
            "types": {k: t[k] for k in TYPES},
            "status": {k: s[k] for k in STATUSES},
            "extensions": ext,
        })
    recs.sort(key=lambda r: (-r["projects"], r["pincode"]))

    with open(os.path.join(OUT, "by_pincode.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pincode", "projects", "units", "group_housing", "plotted", "commercial", "mixed",
                    "completed", "inprogress", "lapsed", "revoked", "suspended", "exempted", "extensions"])
        for r in recs:
            w.writerow([r["pincode"], r["projects"], r["units"],
                        r["types"]["GROUP HOUSING"], r["types"]["PLOTTED"],
                        r["types"]["Commercial"], r["types"]["Mixed (Residential And Commercial)"],
                        r["status"]["COMPLETED"], r["status"]["INPROGRESS"], r["status"]["LAPSED"],
                        r["status"]["REVOKED"], r["status"]["SUSPENDED"], r["status"]["EXEMPTED"],
                        r["extensions"]])

    top = recs[:15]
    rest = recs[15:]
    def agg(rs):
        g = {k: sum(r[k] for r in rs) for k in ("projects", "units", "extensions")}
        g["types"] = {t: sum(r["types"][t] for r in rs) for t in TYPES}
        g["status"] = {s: sum(r["status"][s] for r in rs) for s in STATUSES}
        return g
    with open(os.path.join(OUT, "by_pincode_top.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pincode", "projects", "units", "group_housing", "plotted", "commercial", "mixed",
                    "completed", "inprogress", "lapsed", "extensions"])
        for r in top:
            w.writerow([r["pincode"], r["projects"], r["units"], r["types"]["GROUP HOUSING"],
                        r["types"]["PLOTTED"], r["types"]["Commercial"],
                        r["types"]["Mixed (Residential And Commercial)"],
                        r["status"]["COMPLETED"], r["status"]["INPROGRESS"], r["status"]["LAPSED"], r["extensions"]])
        a = agg(rest)
        w.writerow([f"all other pincodes ({len(rest)})", a["projects"], a["units"], a["types"]["GROUP HOUSING"],
                    a["types"]["PLOTTED"], a["types"]["Commercial"],
                    a["types"]["Mixed (Residential And Commercial)"],
                    a["status"]["COMPLETED"], a["status"]["INPROGRESS"], a["status"]["LAPSED"], a["extensions"]])

    sizes = [r["projects"] for r in recs]
    tot = sum(sizes)
    md = [
        "# Jaipur RERA by pincode\n",
        f"**{tot-2:,} of Jaipur's {tot:,} projects** carry a pincode (2 have none), "
        f"across **{len(recs)-1} pincode values** (the table has {len(recs)} rows: those "
        f"{len(recs)-1} values plus one row for the 2 projects with no pincode). Top 10 pincodes hold "
        f"{100*sum(sizes[:10])/tot:.0f}% of the projects.\n",
        f"- pincodes with >=100 projects: {sum(1 for x in sizes if x>=100)}\n"
        f"- pincodes with >=50: {sum(1 for x in sizes if x>=50)}\n"
        f"- pincodes with <10: {sum(1 for x in sizes if x<10)}\n"
        f"- median projects per pincode: {statistics.median(sizes):.0f}\n",
        "\n## Top 15 pincodes\n",
        "| Pincode | Projects | Units | GH | Plotted | Comm | Mixed | Completed | In prog. | Lapsed | Extensions |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in top:
        md.append(f"| {r['pincode']} | {r['projects']} | {r['units']:,} | {r['types']['GROUP HOUSING']} | "
                  f"{r['types']['PLOTTED']} | {r['types']['Commercial']} | "
                  f"{r['types']['Mixed (Residential And Commercial)']} | {r['status']['COMPLETED']} | "
                  f"{r['status']['INPROGRESS']} | {r['status']['LAPSED']} | {r['extensions']} |")
    a = agg(rest)
    md.append(f"| *all other pincodes ({len(rest)})* | {a['projects']} | {a['units']:,} | {a['types']['GROUP HOUSING']} | "
              f"{a['types']['PLOTTED']} | {a['types']['Commercial']} | {a['types']['Mixed (Residential And Commercial)']} | "
              f"{a['status']['COMPLETED']} | {a['status']['INPROGRESS']} | {a['status']['LAPSED']} | {a['extensions']} |")
    open(os.path.join(OUT, "pincode_summary.md"), "w", encoding="utf-8").write("\n".join(md))
    print(f"pincodes {len(recs)} | projects {tot} | top10 {100*sum(sizes[:10])/tot:.0f}%")
    print("top5:", [(r['pincode'], r['projects']) for r in recs[:5]])


if __name__ == "__main__":
    main()
