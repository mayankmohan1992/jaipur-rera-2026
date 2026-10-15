#!/usr/bin/env python3
"""Fetch the pincode (and city/town/village) the portal records for every
Jaipur RERA project, from Home/GetDetailsbyProjectId."""
import concurrent.futures as cf, json, ssl, urllib.request, time, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
os.makedirs(WORK, exist_ok=True)

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
HDR = {"User-Agent": "Mozilla/5.0"}
OUT = os.path.join(WORK, "pincodes.json")

reg = [r for r in json.load(open(os.path.join(WORK, "register.json"), encoding="utf-8"))["Data"]
       if r.get("DistrictName") == "Jaipur"]
done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
todo = [r for r in reg if str(r["Id"]) not in done]
print("Jaipur:", len(reg), "| to fetch:", len(todo), flush=True)


def one(r):
    rec = {"Id": r["Id"], "name": r.get("ProjectName"), "type": r.get("ProjectTypeName")}
    try:
        u = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"https://reraapp.rajasthan.gov.in/Home/GetDetailsbyProjectId?REFID_id={r['Id']}",
            headers=HDR), context=ctx, timeout=45).read().decode())
        d = (u.get("data") or [{}])[0]
        rec["pincode"] = d.get("PinCode")
        rec["city"] = d.get("CityTownVillage")
        rec["district"] = d.get("DistrictName")
    except Exception as e:
        rec["pincode"] = None; rec["_err"] = str(e)[:50]
    return rec


t0 = time.time()
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for i, rec in enumerate(ex.map(one, todo), 1):
        done[str(rec["Id"])] = rec
        if i % 250 == 0:
            json.dump(done, open(OUT, "w")); print(f"  {i}/{len(todo)} ({time.time()-t0:.0f}s)", flush=True)
json.dump(done, open(OUT, "w"))
have = sum(1 for v in done.values() if v.get("pincode") not in (None, "", "0"))
print(f"DONE {len(done)} records, {have} with a pincode ({time.time()-t0:.0f}s)", flush=True)
