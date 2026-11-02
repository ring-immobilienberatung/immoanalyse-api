"""Build a Postman Collection v2.1 from the ImmoAnalyse.Pro OpenAPI spec.

Usage: python3 scripts/build_postman_collection.py [openapi.json]
Without an argument the spec is downloaded from https://immoanalyse.pro/api/v1/openapi.json.
No API key is written; the collection uses the variables {{baseUrl}} and {{apiKey}}.
"""
import json
import sys
import urllib.request
import uuid

SPEC_URL = "https://immoanalyse.pro/api/v1/openapi.json"
OUT = "postman/immoanalyse-api.postman_collection.json"

# Request bodies/params taken from the examples in the public API documentation.
EXAMPLE_BODIES = {
    ("post", "/valuation"): {
        "adresse": "Suderwichstraße 143", "plz": "45665", "ort": "Recklinghausen",
        "haustyp": "mfh", "baujahr": 1965, "wohnflaeche": 320,
        "grundstuecksflaeche": 1668, "kaltmiete": 1800, "zustandSterne": 3,
        "zustand": "modernisiert", "energieklasse": "E", "kaufpreis": 400000,
    },
    ("post", "/address-lookup"): {"adresse": "Suderwichstraße 143, 45665 Recklinghausen"},
}
EXAMPLE_QUERY = {
    ("get", "/schema"): {"haustyp": "mfh"},
    ("get", "/angebotsmieten"): {"stadt_slug": "recklinghausen", "plz": "45663", "mit_stadtteilen": "true"},
    ("get", "/angebotsmieten/liste"): {"stadt_slug": "recklinghausen", "mit_werten": "true"},
}
EXAMPLE_PATH = {"request_id": "{{requestId}}"}


def load_spec():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as fh:
            return json.load(fh)
    with urllib.request.urlopen(SPEC_URL, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def resolve(spec, obj):
    if isinstance(obj, dict) and "$ref" in obj:
        node = spec
        for part in obj["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return node
    return obj


def build(spec):
    items = []
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            params = [resolve(spec, p) for p in op.get("parameters", []) + ops.get("parameters", [])]
            raw_path = path
            path_vars = []
            for p in params:
                if p.get("in") == "path":
                    raw_path = raw_path.replace("{%s}" % p["name"], ":" + p["name"])
                    path_vars.append({"key": p["name"], "value": EXAMPLE_PATH.get(p["name"], ""),
                                      "description": p.get("description", "")})
            ex_q = EXAMPLE_QUERY.get((method, path), {})
            query = []
            for p in params:
                if p.get("in") != "query":
                    continue
                q = {"key": p["name"], "value": ex_q.get(p["name"], ""),
                     "description": ("(required) " if p.get("required") else "") + p.get("description", "")}
                if p["name"] not in ex_q:
                    q["disabled"] = True
                query.append(q)
            qs = "&".join(f"{q['key']}={q['value']}" for q in query if not q.get("disabled"))
            url = {
                "raw": "{{baseUrl}}" + raw_path + (("?" + qs) if qs else ""),
                "host": ["{{baseUrl}}"],
                "path": [s for s in raw_path.strip("/").split("/")],
            }
            if query:
                url["query"] = query
            if path_vars:
                url["variable"] = path_vars
            request = {
                "method": method.upper(),
                "header": [],
                "url": url,
                "description": (op.get("summary", "") + "\n\n" + op.get("description", "")).strip(),
            }
            if "requestBody" in op:
                request["header"].append({"key": "Content-Type", "value": "application/json"})
                request["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(EXAMPLE_BODIES.get((method, path), {}), ensure_ascii=False, indent=2),
                    "options": {"raw": {"language": "json"}},
                }
            item = {"name": f"{method.upper()} {path} – {op.get('summary', '')}".strip(" –"),
                    "request": request, "response": []}
            if (method, path) == ("post", "/valuation"):
                item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": [
                    "// Store request_id for GET /result/{request_id}",
                    "try { const j = pm.response.json(); if (j.request_id) pm.collectionVariables.set('requestId', j.request_id); } catch (e) {}",
                ]}}]
            items.append(item)

    info = spec["info"]
    server = spec["servers"][0]["url"]
    return {
        "info": {
            "_postman_id": str(uuid.uuid5(uuid.NAMESPACE_URL, "https://immoanalyse.pro/api/v1")),
            "name": "ImmoAnalyse.Pro API",
            "description": (
                f"{info.get('title', '')} (OpenAPI {info.get('version', '')}).\n\n"
                "Set the collection variable `apiKey` to your own key. Never share a collection "
                "or environment that contains a real key. Server-to-server use only.\n\n"
                "Docs: https://immoanalyse.pro/api-docs"
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {"type": "apikey", "apikey": [
            {"key": "key", "value": "X-API-Key", "type": "string"},
            {"key": "value", "value": "{{apiKey}}", "type": "string"},
            {"key": "in", "value": "header", "type": "string"},
        ]},
        "variable": [
            {"key": "baseUrl", "value": server, "type": "string"},
            {"key": "apiKey", "value": "", "type": "string",
             "description": "Your ImmoAnalyse.Pro API key (iap_live_…). Leave empty in shared copies."},
            {"key": "requestId", "value": "", "type": "string",
             "description": "Filled automatically by POST /valuation."},
        ],
        "item": items,
    }


if __name__ == "__main__":
    collection = build(load_spec())
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(collection, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Wrote {OUT} with {len(collection['item'])} requests")
