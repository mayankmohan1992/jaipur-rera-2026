#!/usr/bin/env python3
"""Pincode -> place names for Jaipur RERA projects.

For every Jaipur project the portal records a PinCode and a CityTownVillage.
This pulls both from Home/GetDetailsbyProjectId and writes, per pincode, the
place names the portal itself uses — so the names can be cross-checked.

Writes docs/linkedin-series/rera-jaipur/data/pincode_names.csv and
pincode_city_names.md. Read-only against the portal.
"""
import collections, concurrent.futures as cf, csv, json, os, ssl, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data")
WORK = os.path.join(ROOT, "work")
ctx = ssl.create_default_context()
HDR = {"User-Agent": "Mozilla/5.0"}
API_KEY = os.environ.get("RERA_API_KEY", "MySuperSecretApiKey_123")  # gitleaks:allow


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), context=ctx, timeout=45) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def main():
    # the register (one POST - the endpoint rejects GET)
    req = urllib.request.Request(
        "https://reraapi.rajasthan.gov.in/api/web/Home/GetProjects",
        data=b"{}", headers={"Content-Type": "application/json",
                             "X-API-KEY": API_KEY})
    with urllib.request.urlopen(req, context=ctx, timeout=180) as r:
        reg = json.loads(r.read().decode("utf-8", "ignore"), strict=False)["Data"]
    jaipur = [r for r in reg if r.get("DistrictName") == "Jaipur"]
    print("Jaipur projects:", len(jaipur), flush=True)

    def one(r):
        try:
            d = (get(f"https://reraapp.rajasthan.gov.in/Home/GetDetailsbyProjectId?REFID_id={r['Id']}").get("data") or [{}])[0]
            return {"id": r["Id"], "name": r.get("ProjectName"), "type": r.get("ProjectTypeName"),
                    "pincode": d.get("PinCode"), "city": d.get("CityTownVillage"),
                    "khasra": d.get("PlotKhasraNo")}
        except Exception as e:
            return {"id": r["Id"], "name": r.get("ProjectName"), "type": r.get("ProjectTypeName"),
                    "pincode": None, "city": None, "_err": str(e)[:40]}

    recs = []
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        for i, rec in enumerate(ex.map(one, jaipur), 1):
            recs.append(rec)
            if i % 400 == 0:
                print(f"  {i}/{len(jaipur)}", flush=True)

    # a full per-project file (kept so names can be re-derived without re-pulling)
    with open(os.path.join(OUTDIR, "projects_pincode_city.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["project", "type", "pincode", "city_town_village", "khasra"])
        for r in recs:
            w.writerow([r["name"], r["type"], r.get("pincode"), r.get("city"), r.get("khasra")])

    by = collections.defaultdict(list)
    for r in recs:
        by[str(r.get("pincode") or "(none)")].append(r)
    with open(os.path.join(OUTDIR, "pincode_names.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["pincode", "projects", "distinct_names", "names_with_counts"])
        for p, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
            c = collections.Counter((str(r.get("city")).strip() if r.get("city") else "(blank)") for r in rows)
            w.writerow([p, len(rows), len(c), "; ".join(f"{n} ({k})" for n, k in c.most_common(8))])

    TOP = ["302026", "302012", "302029", "302020", "302017", "303905", "302021",
           "303904", "302022", "302033", "303901", "302006", "302019", "302013", "302001"]
    md = ["# Pincode -> place names (the portal's own CityTownVillage field)\n"]
    for p in TOP:
        rows = by.get(p, [])
        c = collections.Counter((str(r.get("city")).strip() if r.get("city") else "(blank)") for r in rows)
        md.append(f"\n## {p} — {len(rows)} projects, {len(c)} distinct names")
        for n, k in c.most_common(10):
            md.append(f"- {n} ({k})")
    open(os.path.join(OUTDIR, "pincode_city_names.md"), "w", encoding="utf-8").write("\n".join(md))

    for p in TOP:
        rows = by.get(p, [])
        c = collections.Counter((str(r.get("city")).strip() if r.get("city") else "(blank)") for r in rows)
        print(f"\n{p}  ({len(rows)} projects, {len(c)} distinct names)")
        for n, k in c.most_common(5):
            print(f"      {k:4}  {n}")


if __name__ == "__main__":
    main()
