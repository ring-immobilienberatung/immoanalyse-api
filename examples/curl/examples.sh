#!/usr/bin/env bash
# ImmoAnalyse.Pro API – curl examples
# Requires: export IMMOANALYSE_API_KEY="..."  (never hard-code a real key)
set -euo pipefail
: "${IMMOANALYSE_API_KEY:?Please set IMMOANALYSE_API_KEY}"
BASE_URL="${IMMOANALYSE_BASE_URL:-https://immoanalyse.pro/api/v1}"

echo "== GET /types"
curl -sS "$BASE_URL/types" -H "X-API-Key: $IMMOANALYSE_API_KEY"; echo

echo "== GET /schema?haustyp=mfh (does not count against quota)"
curl -sS "$BASE_URL/schema?haustyp=mfh" -H "X-API-Key: $IMMOANALYSE_API_KEY"; echo

echo "== POST /address-lookup (address-lookup quota)"
curl -sS -X POST "$BASE_URL/address-lookup" \
  -H "X-API-Key: $IMMOANALYSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"adresse":"Suderwichstraße 143, 45665 Recklinghausen"}'; echo

echo "== POST /valuation (valuation quota)"
curl -sS -X POST "$BASE_URL/valuation" \
  -H "X-API-Key: $IMMOANALYSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"adresse":"Suderwichstraße 143","plz":"45665","ort":"Recklinghausen","haustyp":"mfh","baujahr":1965,"wohnflaeche":320,"grundstuecksflaeche":1668,"kaltmiete":1800,"zustandSterne":3,"zustand":"modernisiert","energieklasse":"E","kaufpreis":400000}'; echo

# Retrieve a stored valuation (no quota). Use the request_id from the valuation response.
if [[ -n "${REQUEST_ID:-}" ]]; then
  echo "== GET /result/$REQUEST_ID"
  curl -sS "$BASE_URL/result/$REQUEST_ID" -H "X-API-Key: $IMMOANALYSE_API_KEY"; echo
fi

echo "== GET /angebotsmieten (market data)"
curl -sS "$BASE_URL/angebotsmieten?stadt_slug=recklinghausen&plz=45663&mit_stadtteilen=true" \
  -H "X-API-Key: $IMMOANALYSE_API_KEY"; echo

echo "== GET /angebotsmieten/liste (market data)"
curl -sS "$BASE_URL/angebotsmieten/liste?stadt_slug=recklinghausen&mit_werten=true" \
  -H "X-API-Key: $IMMOANALYSE_API_KEY"; echo
