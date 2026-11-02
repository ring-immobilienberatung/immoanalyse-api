# ImmoAnalyse.Pro API – examples

Code examples (curl, Python, JavaScript/Node.js) and a Postman collection for the
**ImmoAnalyse.Pro valuation API**: automated value indications for residential
property in Germany, plus address lookup and asking-rent market data.

📖 Documentation: https://immoanalyse.pro/api-docs?utm_source=github&utm_medium=referral&utm_campaign=api-launch
📄 OpenAPI 3.1: https://immoanalyse.pro/api/v1/openapi.json

## What the API delivers

| Endpoint | Purpose |
|---|---|
| `POST /valuation` | Value indication following ImmoWertV (sales comparison, income and land value): market value with range, valuation confidence, individual method results |
| `POST /address-lookup` | Normalise and geocode a German address (quality flag, lat/lon for the valuation) |
| `GET /types` | Supported property types |
| `GET /schema?haustyp=…` | Field schema per property type (required level, effect, unit, options) |
| `GET /result/{request_id}` | Retrieve a stored valuation again (reproducible) |
| `GET /angebotsmieten` | Latest monthly asking rent (case count, median, P25, P75 in €/m²) for a municipality or postcode; optional districts, purchase prices and location index |
| `GET /angebotsmieten/liste` | Directory of all municipalities, postcodes and districts with case counts (optionally with values) |

- **Coverage:** Germany. Asking rents cover every German municipality (values from 10 listings upward).
- **Base URL:** `https://immoanalyse.pro/api/v1`
- **Auth:** API key in the `X-API-Key` header (alternatively `Authorization: Bearer <key>`).
- **Server-to-server only.** Never put your key into a browser, a mobile app or a public repository.
- Results are value indications. They do not replace a formal appraisal under § 194 BauGB.

## Plans

- **Developer plan: free.** Up to 10 valuations per month, with no payment details needed.
- **Paid plans from €29 net per month** (Starter). Billing is monthly only, and you can cancel monthly.
- Current limits and prices: see the [documentation](https://immoanalyse.pro/api-docs?utm_source=github&utm_medium=referral&utm_campaign=api-launch).

## Quick start

```bash
export IMMOANALYSE_API_KEY="your_key_here"   # never commit a real key
bash examples/curl/examples.sh
python3 examples/python/examples.py
node examples/javascript/examples.mjs        # Node.js 18+
```

Postman: import `postman/immoanalyse-api.postman_collection.json` and set the
collection variable `apiKey`. `baseUrl` is preset to `https://immoanalyse.pro/api/v1`.

Quotas: `/valuation` and `/address-lookup` each have their own monthly quota, and
the plans include a separate allowance of market-data calls. `/schema` and
`/result/{request_id}` do not count against the quota. Identical valuation requests
within 10 minutes are served from cache (`cached: true`) and are not counted again.

## Deutsch

Beispiele und Postman-Collection für die **Bewertungs-API von ImmoAnalyse.Pro**.
Die API liefert automatisierte Wertindikationen für Wohnimmobilien in ganz
Deutschland nach ImmoWertV (Vergleichs-, Ertrags- und Bodenwert). Dazu kommen ein
Adress-Lookup mit Geocoding sowie Angebotsmieten und Marktdaten je Gemeinde,
PLZ und Stadtteil.

- **Developer-Plan kostenlos:** bis zu 10 Bewertungen pro Monat, ohne Zahlungsdaten.
- **Bezahlte Tarife ab 29 € netto im Monat.** Die Zahlung ist nur monatlich möglich, monatlich kündbar.
- Den Schlüssel als Header `X-API-Key` senden, nur von Server zu Server.
- Dokumentation: https://immoanalyse.pro/api-docs?utm_source=github&utm_medium=referral&utm_campaign=api-launch

## License

The example code in this repository is licensed under the MIT License (see `LICENSE`).
Use of the API itself is governed by the
[API terms of use](https://immoanalyse.pro/rechtliches/api-nutzungsbedingungen).
