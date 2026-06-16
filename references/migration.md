# Migrating a legacy integration

For developers with an existing Qapla' integration who need to move off an older
API version. There is **no automated migration path** — work through the
checklist and diff your payloads against the current docs.

> Version status, the base-URL pattern, and the full "which version hosts which
> endpoint" matrix live in [`versioning.md`](versioning.md). This file is the
> upgrade *procedure*; read `versioning.md` first for the policy.

## Where you are → what to do

| Current version | Action |
|---|---|
| `1.0` | Retired — migrate now. Follow the checklist below (target `1.3`, plus `1.2` for endpoints not yet on `1.3`). |
| `1.1` | Deprecated but still active — migrate when you can. Same checklist. |
| `1.2` | Deprecated but still active. No forced migration; but build *new* code against `1.3` where the endpoint exists. Many endpoints remain `1.2`-only by design — keep calling those at `1.2`. |
| `1.3` | Current. Consider `v2` only if you need what it adds (see below); `1.3` is not being retired to make room for it. |

> **Do not "upgrade everything to 1.3".** `1.3` and `1.2` coexist by design: a
> large set of endpoints (`getShipments`, `getOrders`, `updateShipment`,
> `updateOrder`, `deleteShipment`, `trackingByTimeFrame`, `getPudos`, the label
> read/check/delete endpoints, channel management, platform, virtual courier, …)
> have **no `1.3` equivalent** and must still be called at `1.2`. See
> `versioning.md` for the per-endpoint list.

## v1.0 / v1.1 → v1.2 / v1.3 checklist

### 1. Update the version segment in the base URL

The version is a path segment. Find every hardcoded `/1.0/` or `/1.1/` and
retarget per the matrix in `versioning.md`:

```
# old
https://api.qapla.it/1.1/pushShipment/
# new
https://api.qapla.it/1.3/pushShipment/      ← 1.3 where the endpoint exists
https://api.qapla.it/1.2/getShipments/      ← 1.2 where it's the only host
```

### 2. Authentication — same mechanism, confirm placement

v1.x auth has always been a **per-channel private API key**, sent as:
- `apiKey` in the JSON **body** for POST requests, or
- `apiKey` query parameter for GET requests.

If your legacy code placed the key elsewhere, align it. See
[`authentication.md`](authentication.md) for details (and the `getQuotes`
`x-api-key`/`x-sandbox` header exceptions in [`getquotes.md`](getquotes.md)).

### 3. Diff each request payload against the live docs

Field-level changes between v1.0/1.1 and v1.2/1.3 are not published as a
changelog, so verify each endpoint your code calls against
<https://api.qapla.dev>: remove fields that no longer exist, add newly-required
ones. Apply the standing conventions (see [`conventions.md`](conventions.md)):
- Dates `YYYY-MM-DD`, datetimes `YYYY-MM-DD HH:MM:SS` (space, **not** `T`), CEST.
- Decimals use `.`, no thousands separator.
- Country codes ISO 3166-1 alpha-2 (`IT`, `GB`, …).
- Courier codes must match the list from `getCouriers` — do not invent them.

### 4. Update response-envelope parsing

Every v1.2/1.3 response is wrapped under a key named after the endpoint, and
batch endpoints repeat `result` per item. Real `pushShipment` shape:

```json
{
  "pushShipment": {
    "result": "OK",
    "error": null,
    "count": 2,
    "imported": 2,
    "shipments": [
      { "result": "OK", "error": null, "id": 9999999, "hash": "…", "url": "https://tracking.qapla.it/…", "courier": "DHL", "trackingNumber": "123987299" }
    ]
  }
}
```

If your legacy parser read a flat body, update it to navigate
`response["<endpointName>"]` and to check the **per-item** `result` inside the
array, not just the top-level one.

### 5. Rate limiting

v1.x enforces a token bucket (capacity 120, refill 2/s); a batch costs one token
**per item** (100 shipments = 100 tokens). Add `429` handling with exponential
back-off. The bundled `scripts/qapla_client.py` already does this.

### 6. Sandbox & test

Use `"sandbox": true` in the body where supported (no separate base URL), then
run your suite against a non-production channel before promoting.

## v1.x → v2 (optional)

v2 is a **separate generation**, not a v1 version bump, and it **coexists** with
v1.3 — migrate only for features you need. Verified differences:

| Aspect | v1.x | v2 |
|---|---|---|
| **Auth** | `apiKey` in body/query | Exchange the key for a **JWT** at `POST /v2/auth/token`, then send `Authorization: Bearer …`. Same channel key, different flow — v1-style auth won't work on v2. |
| **Permissions** | Implicit per key | Explicit **scopes** (e.g. `parcels:create`, `sandbox:read`) |
| **Errors** | `{"<endpoint>":{"result":"OK"\|"KO",…}}` envelope | Standard **HTTP status codes** |
| **Time / dates** | CEST, `YYYY-MM-DD HH:MM:SS` | **UTC**, ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` |
| **Parcels** | Embedded in shipment/order payloads | **First-class resource** with its own CRUD (`/v2/parcels`, `/v2/parcels/{hash}`) |
| **Bulk create** | Synchronous (result inline) | May be **asynchronous**: `POST /v2/parcels` can return `202` with an `AsyncJobResponse` (`jobId`, `status`, `statusUrl`, `hashes`, `totalParcels`) to poll |
| **Sandbox** | `sandbox: true` flag | Modeled as its own resource (`/v2/sandbox` CRUD) |

The published v2 surface is still small (auth / parcels / sandbox; OpenAPI
`2.8.8`). Before building against it, read the live v2 docs and
`/v2/swagger/openapi.json` — its endpoints and payloads are out of scope for this
skill. See [`versioning.md`](versioning.md#v2--separate-generation-opt-in) for the
auth flow.

## Related references

- [`versioning.md`](versioning.md) — version policy + endpoint version matrix
- [`authentication.md`](authentication.md) — API key, sandbox, rate limiting
- [`conventions.md`](conventions.md) — envelope, dates, errors, rate limits
