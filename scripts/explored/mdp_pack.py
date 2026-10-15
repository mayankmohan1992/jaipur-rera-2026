#!/usr/bin/env python3
"""Jaipur-MDP subset of the RERA register (Post 6, MDP view).

Uses /tmp/jaipur_placement.json (the project's own coordinates / KML boundary
tested against the viewer's MDP layer) to keep only Jaipur projects that fall
inside the Jaipur MDP, then reports the same facts as the citywide pack.

Nothing here is inferred: every field is a server value (register, project
detail page) or the result of a point-in-polygon test against the MDP layer.
"""
import collections, csv, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")
os.makedirs(OUT, exist_ok=True)

REG = {r["Id"]: r for r in json.load(open("/tmp/allprojects.json", encoding="utf-8"))["Data"]}
DET = {r["Id"]: r for r in json.load(open("/tmp/rera_harvest/details.json", encoding="utf-8"))}
PLC = json.load(open("/tmp/jaipur_placement.json", encoding="utf-8"))
LAPSED_IDS = {r["Id"] for r in json.loads(open("/tmp/st7.json", encoding="utf-8", errors="ignore").read(), strict=False)["Data"]}


def yr(r):
    return (r.get("approvedon") or "?")[:4]


def st(r):
    s = (r.get("status") or "").strip()
    return "COMPLETED" if "COMPLETED" in s else s


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows)


def table(hdr, rows):
    o = ["| " + " | ".join(hdr) + " |", "|" + "|".join(["---"] * len(hdr)) + "|"]
    o += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(o)


def main():
    jaipur = [r for r in DET.values() if r.get("district") == "Jaipur"]
    inside = [r for r in jaipur if (PLC.get(str(r["Id"])) or PLC.get(r["Id"]) or {}).get("inside") is True]
    print(f"Jaipur {len(jaipur)} | inside MDP {len(inside)}")

    # coverage of the placement test
    how = collections.Counter((PLC.get(str(r["Id"])) or {}).get("how") for r in jaipur)
    write("mdp_coverage.csv", ["method", "projects"], sorted(how.items(), key=lambda kv: -kv[1]))
    write("mdp_placement.csv", ["project", "reg_no", "type", "reg_year", "inside_mdp", "zone", "method"],
          [[r.get("name"), (REG.get(r["Id"]) or {}).get("REGISTRATIONNO"), r.get("type"), yr(r),
            (PLC.get(str(r["Id"])) or {}).get("inside"),
            (PLC.get(str(r["Id"])) or {}).get("zone"),
            (PLC.get(str(r["Id"])) or {}).get("how")] for r in jaipur])

    byy = collections.Counter(yr(r) for r in inside)
    byt = collections.Counter((r.get("type") or "").strip() for r in inside)
    sts = collections.Counter(st(r) for r in inside)
    zones = collections.Counter((PLC.get(str(r["Id"])) or {}).get("zone") for r in inside if (PLC.get(str(r["Id"])) or {}).get("zone"))
    lap = [r for r in inside if r["Id"] in LAPSED_IDS]
    ext = [r for r in inside if (r.get("next") or 0) > 0]
    units = 0
    for r in inside:
        try:
            units += int(float(r.get("units")))
        except (TypeError, ValueError):
            pass

    write("mdp_registrations_by_year.csv", ["year", "projects"], sorted(byy.items()))
    write("mdp_registrations_by_type.csv", ["type", "projects"], sorted(byt.items(), key=lambda kv: -kv[1]))
    write("mdp_status.csv", ["status", "projects"], sorted(sts.items(), key=lambda kv: -kv[1]))
    write("mdp_zones.csv", ["zone", "projects"], sorted(zones.items(), key=lambda kv: -kv[1]))

    rep = {
        "jaipur_projects": len(jaipur),
        "inside_mdp": len(inside),
        "outside_mdp": sum(1 for r in jaipur if (PLC.get(str(r["Id"])) or {}).get("inside") is False),
        "undetermined": sum(1 for r in jaipur if (PLC.get(str(r["Id"])) or {}).get("inside") is None),
        "units": units,
        "lapsed": len(lap),
        "with_extensions": len(ext),
    }
    json.dump(rep, open(os.path.join(OUT, "mdp_summary.json"), "w"), indent=1)

    md = [
        "# Jaipur MDP subset (Post 6)\n",
        f"Placement: each project's own coordinates (server `Latitude`/`Longitude`) "
        f"or its own KML boundary/marker, tested against the viewer's MDP land-use "
        f"layer. Of **{len(jaipur):,}** Jaipur projects: **{len(inside):,} inside the "
        f"MDP**, {rep['outside_mdp']:,} outside, {rep['undetermined']:,} with no "
        f"geometry to test.\n",
        "## Registrations by year (inside the MDP)\n",
        table(["Year", "Projects"], sorted(byy.items())),
        "\n## By type\n", table(["Type", "Projects"], sorted(byt.items(), key=lambda kv: -kv[1])),
        "\n## Status\n", table(["Status", "Projects"], sorted(sts.items(), key=lambda kv: -kv[1])),
        "\n## By zone\n", table(["Zone", "Projects"], sorted(zones.items(), key=lambda kv: -kv[1])),
        f"\n- units declared: **{units:,}**\n- on the portal's Lapsed list: **{len(lap):,}**\n"
        f"- with >=1 extension: **{len(ext):,}**\n",
        "\n## Placement method\n", table(["Method", "Projects"], sorted(how.items(), key=lambda kv: -kv[1])),
    ]
    open(os.path.join(OUT, "mdp_findings.md"), "w", encoding="utf-8").write("\n".join(str(x) for x in md))
    print("summary:", rep)
    print("zones:", dict(zones))
    print("status:", dict(sts))


if __name__ == "__main__":
    main()
