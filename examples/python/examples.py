"""ImmoAnalyse.Pro API – Python examples (standard library only, Python 3.8+).

Set your key as an environment variable first:
    export IMMOANALYSE_API_KEY="..."   # never hard-code or commit a real key
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("IMMOANALYSE_BASE_URL", "https://immoanalyse.pro/api/v1")
API_KEY = os.environ.get("IMMOANALYSE_API_KEY")
if not API_KEY:
    sys.exit("Please set IMMOANALYSE_API_KEY")


def call(method, path, params=None, body=None):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-API-Key", API_KEY)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        # Error responses are JSON: {"error": {"code": ..., "message": ...}}
        return {"http_status": err.code, **json.loads(err.read().decode("utf-8") or "{}")}


def show(title, result):
    print(f"== {title}")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    # Discovery: /schema does not count against the quota
    show("GET /types", call("GET", "/types"))
    show("GET /schema?haustyp=mfh", call("GET", "/schema", {"haustyp": "mfh"}))

    # 1) Geocode the address
    lookup = call("POST", "/address-lookup",
                  body={"adresse": "Suderwichstraße 143, 45665 Recklinghausen"})
    show("POST /address-lookup", lookup)

    # 2) Valuation; pass lat/lon only if the lookup quality is "exact"
    valuation_body = {
        "adresse": "Suderwichstraße 143", "plz": "45665", "ort": "Recklinghausen",
        "haustyp": "mfh", "baujahr": 1965, "wohnflaeche": 320,
        "grundstuecksflaeche": 1668, "kaltmiete": 1800, "zustandSterne": 3,
        "zustand": "modernisiert", "energieklasse": "E", "kaufpreis": 400000,
    }
    coords = lookup.get("koordinaten") or {}
    if lookup.get("quality") == "exact" and coords.get("lat") is not None:
        valuation_body.update(lat=coords["lat"], lon=coords["lon"])
    valuation = call("POST", "/valuation", body=valuation_body)
    show("POST /valuation", valuation)

    # 3) Retrieve the stored result again (no quota)
    request_id = valuation.get("request_id")
    if request_id:
        show(f"GET /result/{request_id}", call("GET", f"/result/{request_id}"))

    # Market data: asking rents
    show("GET /angebotsmieten", call("GET", "/angebotsmieten", {
        "stadt_slug": "recklinghausen", "plz": "45663", "mit_stadtteilen": "true"}))
    show("GET /angebotsmieten/liste", call("GET", "/angebotsmieten/liste", {
        "stadt_slug": "recklinghausen", "mit_werten": "true"}))
