#!/usr/bin/env python3
"""Harvest per-project RERA status + extension history for all registered
projects, from the two public HomeWebsite endpoints. Read-only."""
import json, ssl, urllib.parse, urllib.request, concurrent.futures as cf, time, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
os.makedirs(WORK, exist_ok=True)

ctx = ssl.create_default_context()
HDR = {"User-Agent":"Mozilla/5.0", "Accept":"application/json"}
OUT = os.path.join(WORK, "details.json")

reg = json.load(open(os.path.join(WORK, "register.json"), encoding="utf-8"))["Data"]
print("projects:", len(reg), flush=True)

done = {}
if os.path.exists(OUT):
    done = {r["Id"]: r for r in json.load(open(OUT, encoding="utf-8"))}
    print("already have:", len(done), flush=True)

def get(url, tries=3):
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, context=ctx, timeout=45) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as e:
            if i==tries-1: return {"_err": str(e)[:80]}
            time.sleep(1.5)

def fetch(p):
    pid=p["Id"]; enc=p.get("EncryptedProjectId")
    rec={"Id":pid,"name":p.get("ProjectName"),"district":p.get("DistrictName"),
         "type":p.get("ProjectTypeName"),"regno":p.get("REGISTRATIONNO"),
         "approvedon":p.get("APPROVEDON"),"revcert":p.get("RevisedCertiRC"),
         "cc":p.get("IsCCUploaded"),"reg_completion":p.get("RevisedDateOfComplation")}
    d=get(f"https://reraapp.rajasthan.gov.in/HomeWebsite/ProjectDtlsWebsite/{enc}")
    if isinstance(d,dict) and d.get("success") and isinstance(d.get("data"),dict):
        x=d["data"]
        rec["status"]=x.get("StatusOfProject")
        rec["regdate"]=x.get("DateofRegistration")
        rec["completion"]=x.get("RevisedDateOfComplation")
        rec["phase_area"]=x.get("PhaseArea")
        rec["buildings"]=x.get("TotalBuildingCount")
        ext=x.get("GetPreviousExtsList") or []
        rec["next"]=len(ext)
        rec["ext"]=[{"from":e.get("ExtensionFromDt"),"to":e.get("ExtensionToDt")} for e in ext]
    else:
        rec["status"]=None; rec["next"]=None; rec["_err"]=(d or {}).get("_err","shape")
    # units + coordinates from the MVC detail endpoint
    u=get(f"https://reraapp.rajasthan.gov.in/Home/GetDetailsbyProjectId?REFID_id={pid}")
    if isinstance(u,dict) and u.get("success") and u.get("data"):
        y=u["data"][0] if isinstance(u["data"],list) else u["data"]
        rec["units"]=y.get("total_units"); rec["lon"]=y.get("Longitude"); rec["lat"]=y.get("Latitude")
        rec["kml"]=y.get("kmlfile")
    return rec

todo=[p for p in reg if p["Id"] not in done]
print("to fetch:", len(todo), flush=True)
t0=time.time(); n=0
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for rec in ex.map(fetch, todo):
        done[rec["Id"]]=rec; n+=1
        if n%250==0:
            json.dump(list(done.values()), open(OUT,"w",encoding="utf-8"))
            print(f"  {n}/{len(todo)}  ({time.time()-t0:.0f}s)", flush=True)
json.dump(list(done.values()), open(OUT,"w",encoding="utf-8"))
errs=sum(1 for r in done.values() if r.get("status") is None)
print(f"DONE {len(done)} records, {errs} with no status, {time.time()-t0:.0f}s", flush=True)
