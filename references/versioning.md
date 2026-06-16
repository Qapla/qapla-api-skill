# API versions

Qapla' selects the API version with a **path segment**:

```
https://api.qapla.it/<version>/<endpoint>
```

> **Source of truth:** <https://api.qapla.dev/1.3/> (and the per-version intros).
> This file mirrors the official version policy; if anything drifts, trust the
> live docs.

## Version status

| Version | Status | Notes |
|---|---|---|
| `1.0` | **Retired** | No longer offered. |
| `1.1` | **Deprecated** (still active) | Kept alive for legacy integrations; do not build new code against it. |
| `1.2` | **Deprecated** (still active) | Officially deprecated, but **still required**: many endpoints have not been migrated to 1.3 and are served only under `1.2`. |
| `1.3` | **Current / latest** | The production version. Use it wherever the endpoint exists. |
| `1.4` | **Narrow extension** | Only `createLabel` is published under `1.4`; it adds the `parcelsTracking` capability. Not a full version — use `1.3` for everything else. |
| `v2` | **Preview / opt-in** | A separate, RESTful generation with different auth and conventions (see below). Small surface today; not a drop-in replacement for v1.3. |

> The official 1.3 docs state it plainly: 1.3 is the latest version, **not all
> endpoints have been migrated to it yet**, and endpoints that haven't been
> migrated still reference the previous version (1.2). So calling a 1.2 endpoint
> is expected, not a mistake — it's simply where that endpoint currently lives.

## Which version do I call? (v1.x)

**Rule of thumb:** use `1.3` when the endpoint is published there; otherwise use
`1.2`. The per-endpoint version is in the **Ver.** column of `endpoints.md`.

Published under **1.3** today: `pushShipment`, `getShipment`,
`getCompanyShipment(s)`, `pushOrder`, `getOrder`, `markOrderReady`, `createLabel`,
`confirmLabel`, `getQuotes`, `checkAddress`, `couriers`.

Still **1.2-only** (no 1.3 equivalent yet): `getShipments`, `getOrders`,
`update*`/`delete*`/`undelete*` (shipments & orders), `trackingByTimeFrame`,
`getPudos`, `getLabel`, `checkLabel`, `deleteLabel`, `createReturnLabel`,
`getCouriers`, `detectCourier`, `detectOrderCourier`, `getCredits`,
`getQaplaStatus`, all channel-management endpoints, platform/marketplace
endpoints, and the virtual-courier endpoints.

> Mixing versions across a single integration is normal: e.g. push with
> `1.3/pushShipment` but poll with `1.2/trackingByTimeFrame`.

## v2 — separate generation (opt-in)

v2 is a distinct RESTful API, **not** a versioned variant of v1.x. It differs in
several fundamental ways, so do not assume v1.3 knowledge carries over:

| Aspect | v1.x | v2 |
|---|---|---|
| **Auth** | `apiKey` in the JSON body (per channel) | **Bearer JWT**: exchange the API key for a token, then send it as a header |
| **Errors** | `{"<endpoint>": {"result":"OK"\|"KO", "error":…}}` envelope | Standard **HTTP status codes** |
| **Time zone** | CEST (UTC+1/＋2) | **UTC** |
| **Datetime format** | `YYYY-MM-DD HH:MM:SS` | **ISO 8601** `YYYY-MM-DDTHH:MM:SSZ` |
| **Permissions** | Implicit (per channel key) | Explicit **scopes** (e.g. `parcels:create`, `sandbox:read`) |

### Authentication flow

```bash
# 1. Exchange the channel API key for a JWT
curl -X POST https://api.qapla.it/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"api_key": "API_KEY"}'
```

Response includes `token` (the JWT), `scopes`, `token_type` (`Bearer`),
`expires_in` (seconds — `86400` = 24 h), and a `rate_limit` object
(`refill_rate`, `bucket_size`).

```bash
# 2. Send the token as a Bearer header on every subsequent request
curl -X GET https://api.qapla.it/v2/<endpoint> \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Current v2 surface

The published v2 surface is still small (OpenAPI `2.8.8`):

| Method(s) | Path |
|---|---|
| `POST` | `/v2/auth/token` |
| `GET` / `POST` / `DELETE` | `/v2/parcels` |
| `GET` / `DELETE` / `PATCH` | `/v2/parcels/{hash}` |
| `GET` / `POST` | `/v2/sandbox` |
| `GET` / `PUT` / `DELETE` / `PATCH` | `/v2/sandbox/{id}` |

For new integrations today, stick with **v1.3** (this skill's focus). Reach for v2
only when you specifically need its model, and read the live v2 docs +
`/v2/swagger/openapi.json` first — its endpoints and payloads are out of scope
here.

> Upgrading an existing integration off an older version? See
> [`migration.md`](migration.md).
