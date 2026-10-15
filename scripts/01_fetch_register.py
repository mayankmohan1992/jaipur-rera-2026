#!/usr/bin/env python3
"""Step 1 - download the Rajasthan RERA project register.

This is the master list every other script joins to.

Endpoint (a JSON POST, and it rejects GET):

    POST https://reraapi.rajasthan.gov.in/api/web/Home/GetProjects
    Headers: Content-Type: application/json
             X-API-KEY: <the key the portal's own front-end bundle carries>
    Body:    {}                      -> every project in the state

The same endpoint takes a status filter, which is how the portal's own
"Lapsed / Suspended / Revoked" pages are built:

    Body:    {"ApplicationStatus": 5}   -> 106 projects   (revoked)
    Body:    {"ApplicationStatus": 6}   ->  21 projects   (suspended)
    Body:    {"ApplicationStatus": 7}   -> 1,208 projects (lapsed)

Writes:
    work/register.json          the full register
    work/register_lapsed.json   the portal's own Lapsed list

NOTE ON THE API KEY
The portal authenticates its public API with a static key embedded in its own
JavaScript bundle. It is reproduced here because the endpoints cannot be queried
without it; it is a client-side value, not a secret of ours.
"""
import json, os, ssl, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
API = "https://reraapi.rajasthan.gov.in/api/web/Home"
API_KEY = "MySuperSecretApiKey_123"          # carried in the portal's own bundle

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def post(path, body):
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "X-API-KEY": API_KEY,
                 "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=180) as r:
        # the payload contains control characters in a few free-text fields
        return json.loads(r.read().decode("utf-8", "ignore"), strict=False)


def main():
    os.makedirs(WORK, exist_ok=True)
    # Save the response EXACTLY as the API returns it ({"State", "Data": [...]}),
    # so the work/ files mirror the wire format and can be diffed against it.
    reg = post("/GetProjects", {})
    rows = reg.get("Data") or []
    if not rows:
        sys.exit("register returned no rows: %r" % (reg.get("Message"),))
    json.dump(reg, open(os.path.join(WORK, "register.json"), "w", encoding="utf-8"))
    print("register: %d projects" % len(rows))

    lap = post("/GetProjects", {"ApplicationStatus": 7})
    json.dump(lap, open(os.path.join(WORK, "register_lapsed.json"), "w", encoding="utf-8"))
    print("lapsed list: %d projects" % len(lap.get("Data") or []))

    print("\nexpected at the time of writing: 5,408 register / 1,208 lapsed")


if __name__ == "__main__":
    main()
