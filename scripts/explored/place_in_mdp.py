#!/usr/bin/env python3
"""Place every Jaipur RERA project in/out of the Jaipur MDP, using every
geometry the server publishes, in descending order of precision:

  1. RJGIS RERA area polygon  (FeatureServer/1, keyed by PROJECT_ID)
  2. RJGIS RERA location point (FeatureServer/0, keyed by PROJECT_ID)
  3. the project's own Latitude/Longitude (GetDetailsbyProjectId)
  4. the project's own KML boundary / marker (same endpoint) - only real KML;
     many `.kml` URLs actually serve a PDF capture sheet, which is skipped.

Then a point-in-polygon test against data/mdp_data.js.

Output: /tmp/jaipur_placement.json
"""
import io, json, os, re, zipfile

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def kml_point(path):
    b = open(path, "rb").read()
    if b[:4] == b"%PDF":                       # capture sheet, not geodata
        return None, "pdf-capture-sheet"
    if b[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(b))
        n = [x for x in z.namelist() if x.lower().endswith(".kml")][0]
        xml = z.read(n).decode("utf-8", "ignore")
    else:
        xml = b.decode("utf-8", "ignore")
    if "<coordinates>" not in xml:
        return None, "kml with no coordinates"
    best = []
    for blk in re.findall(r"<coordinates>(.*?)</coordinates>", xml, re.S):
        pts = []
        for tok in blk.split():
            p = tok.split(",")
            if len(p) >= 2:
                try:
                    pts.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
        if len(pts) > len(best):
            best = pts
    if not best:
        return None, "kml with no coordinates"
    if len(best) >= 4:
        g = shape({"type": "Polygon", "coordinates": [best]})
        if not g.is_valid:
            g = g.buffer(0)
        rp = g.representative_point()
        return (rp.x, rp.y), "kml-boundary"
    return best[0], "kml-point"


from shapely.geometry import Polygon


def rep_point(geom):
    """ArcGIS JSON geometry ({"x","y"} or {"rings":[...]}) -> a point inside it."""
    if "x" in geom and "y" in geom:
        return (geom["x"], geom["y"])
    rings = geom.get("rings") or []
    best, best_area = None, 0.0
    for ring in rings:                       # largest ring = outer boundary
        try:
            poly = Polygon(ring)
            if poly.is_valid and abs(poly.area) > best_area:
                best, best_area = poly, abs(poly.area)
        except Exception:
            continue
    if best is None:
        raise ValueError("no usable ring")
    rp = best.representative_point()
    return (rp.x, rp.y)


def main():
    s = open(os.path.join(ROOT, "data/mdp_data.js"), encoding="utf-8").read()
    mdp = json.loads(s[s.index("=") + 1:].rstrip().rstrip(";"))
    geoms, names = [], []
    for f in mdp["features"]:
        try:
            geoms.append(shape(f["geometry"])); names.append((f.get("properties") or {}).get("ADMIN_ZONE"))
        except Exception:
            pass
    tree = STRtree(geoms)

    poly = {int(f["attributes"]["PROJECT_ID"]): f["geometry"] for f in json.load(open("/tmp/rj_layer1.json"))}
    ptl = {int(f["attributes"]["PROJECT_ID"]): f["geometry"] for f in json.load(open("/tmp/rj_layer0.json"))}
    det = json.load(open("/tmp/rera_harvest/details.json", encoding="utf-8"))
    j = [r for r in det if r.get("district") == "Jaipur"]

    out = {}
    for r in j:
        pid = r["Id"]; point = None; how = None
        for cand_geom, label in ((poly.get(pid), "rgis-area-polygon"),
                                 (ptl.get(pid), "rgis-location-point")):
            if cand_geom is None:
                continue
            try:
                point, how = rep_point(cand_geom), label
                break
            except Exception:
                point = None
        if point is None and r.get("lat") not in (None, "", "0") and r.get("lon") not in (None, "", "0"):
            try:
                point, how = (float(r["lon"]), float(r["lat"])), "server-latlon"
            except (TypeError, ValueError):
                point = None
        if point is None:
            fn = f"/tmp/kml_jaipur/{pid}.kml"
            if os.path.exists(fn):
                try:
                    point, how = kml_point(fn)
                except Exception as e:
                    point, how = None, "kml err " + str(e)[:30]
            else:
                how = "no geometry published"
        if point is None:
            out[pid] = {"inside": None, "zone": None, "how": how or "no geometry published"}
            continue
        P = Point(point[0], point[1])
        cand = tree.query(P)
        zone = ""
        for i in cand:
            if geoms[i].contains(P):
                zone = names[i] or ""; break
        if not zone and cand.size:
            zone = names[cand[0]] or ""
        out[pid] = {"inside": bool(cand.size), "zone": zone or None, "how": how,
                    "lon": round(point[0], 6), "lat": round(point[1], 6)}

    json.dump(out, open("/tmp/jaipur_placement.json", "w"))
    import collections
    print("method:", dict(collections.Counter(v["how"] for v in out.values()).most_common()))
    print("inside:", dict(collections.Counter(v["inside"] for v in out.values())))
    print("zones:", dict(collections.Counter(v["zone"] for v in out.values() if v.get("zone")).most_common()))


if __name__ == "__main__":
    main()
