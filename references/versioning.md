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
| `v2` | **Separate generation** | A distinct RESTful API (Bearer/JWT auth), not a versioned variant of v1.x and evolving independently. Not a drop-in replacement for v1.3. See below. |

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

## v2 — separate generation

v2 is a distinct RESTful API, **not** a versioned variant of v1.x, so v1.3
knowledge does not carry over. At a high level it differs in:

- **Auth** — exchange the channel API key for a **Bearer JWT**, then send it as an
  `Authorization: Bearer …` header. v1-style auth (`apiKey` in the body) won't work.
- **Errors** — standard **HTTP status codes**, not the `{"<endpoint>":{"result":…}}`
  envelope.
- **Time** — **UTC**, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`), vs CEST + `YYYY-MM-DD HH:MM:SS`.

v2 is developed and documented independently and is actively evolving, so its
exact endpoints, fields, scopes, and auth request payload are **out of scope for
this skill** — and the published spec can lag the deployed API. For anything v2,
work from the live docs, which are the only authoritative, current source:

- Docs + Swagger UI: <https://api.qapla.dev/v2/>

For new integrations today, this skill targets **v1.3**. Reach for v2 only when
you specifically need its model, and follow the live v2 docs for the auth flow and
payloads — do not assume the field names or surface described elsewhere.

> Upgrading an existing integration off an older version? See
> [`migration.md`](migration.md).
