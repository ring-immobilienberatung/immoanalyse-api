// ImmoAnalyse.Pro API – JavaScript examples (Node.js 18+, built-in fetch).
// Server-side only: never ship your API key to a browser or app.
//   export IMMOANALYSE_API_KEY="..."   (never hard-code or commit a real key)

const BASE_URL = process.env.IMMOANALYSE_BASE_URL ?? "https://immoanalyse.pro/api/v1";
const API_KEY = process.env.IMMOANALYSE_API_KEY;
if (!API_KEY) {
  console.error("Please set IMMOANALYSE_API_KEY");
  process.exit(1);
}

async function call(method, path, { params, body } = {}) {
  const url = new URL(BASE_URL + path);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const res = await fetch(url, {
    method,
    headers: {
      "X-API-Key": API_KEY,
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json().catch(() => ({}));
  return res.ok ? json : { http_status: res.status, ...json };
}

const show = (title, data) =>
  console.log(`== ${title}\n${JSON.stringify(data, null, 2).slice(0, 2000)}`);

// Discovery: /schema does not count against the quota
show("GET /types", await call("GET", "/types"));
show("GET /schema?haustyp=mfh", await call("GET", "/schema", { params: { haustyp: "mfh" } }));

// 1) Geocode the address
const lookup = await call("POST", "/address-lookup", {
  body: { adresse: "Suderwichstraße 143, 45665 Recklinghausen" },
});
show("POST /address-lookup", lookup);

// 2) Valuation; pass lat/lon only if the lookup quality is "exact"
const valuationBody = {
  adresse: "Suderwichstraße 143", plz: "45665", ort: "Recklinghausen",
  haustyp: "mfh", baujahr: 1965, wohnflaeche: 320, grundstuecksflaeche: 1668,
  kaltmiete: 1800, zustandSterne: 3, zustand: "modernisiert", energieklasse: "E",
  kaufpreis: 400000,
};
if (lookup.quality === "exact" && lookup.koordinaten?.lat != null) {
  Object.assign(valuationBody, { lat: lookup.koordinaten.lat, lon: lookup.koordinaten.lon });
}
const valuation = await call("POST", "/valuation", { body: valuationBody });
show("POST /valuation", valuation);

// 3) Retrieve the stored result again (no quota)
if (valuation.request_id) {
  show(`GET /result/${valuation.request_id}`, await call("GET", `/result/${valuation.request_id}`));
}

// Market data: asking rents
show("GET /angebotsmieten", await call("GET", "/angebotsmieten", {
  params: { stadt_slug: "recklinghausen", plz: "45663", mit_stadtteilen: "true" },
}));
show("GET /angebotsmieten/liste", await call("GET", "/angebotsmieten/liste", {
  params: { stadt_slug: "recklinghausen", mit_werten: "true" },
}));
