# Qapla' API v2 — overview

Qapla' **v2** is a new, separate generation of the API — a clean RESTful redesign,
**not** a version bump of v1.x. It is being built out incrementally and is the
direction the platform is moving toward (the long-term goal is for the whole API
surface to live under v2). Today it ships a stable core (auth, parcels, sandbox,
jobs) while other resources are still being migrated.

> **Source of truth & drift warning.** This section reflects the **real
> implementation** in `qore/api` as of **v2.9.4** (2026-06-16), which is more
> current than the public Swagger. The public Swagger (`api.qapla.dev/v2`, baseline
> 2.8.8) **lags** the deployed API — it only lists `auth`/`parcels`/`sandbox` and
> still shows some outdated field names. v2 is **actively evolving**: when in doubt,
> verify against the live docs and Swagger UI at <https://api.qapla.dev/v2/>.

## How v2 differs from v1.3 — read this first

| Topic | v1.3 | **v2** |
|---|---|---|
| **Base URL** | `https://api.qapla.it/1.3/<endpoint>` | `https://api.qapla.it/v2/<resource>` |
| **Auth** | `apiKey` in the JSON body, every call | Exchange `apiKey` → **Bearer JWT** once, then `Authorization: Bearer <token>` |
| **Style** | RPC-ish: one endpoint name per action | RESTful: resources + HTTP verbs (`GET`/`POST`/`PUT`/`PATCH`/`DELETE`) |
| **Success / errors** | Always `200` + `{"<endpoint>":{"result":"OK"\|"KO"}}` envelope | Real HTTP status codes (`200`/`201`/`202`/`204`/`4xx`/`5xx`); **no** envelope |
| **Error body** | `error` string inside the envelope | **RFC 7807** `application/problem+json` (`type`/`title`/`status`/`detail`/`violations`) |
| **Time** | CEST, `YYYY-MM-DD HH:MM:SS` (space) | **UTC**, ISO 8601 / ATOM (`YYYY-MM-DDTHH:MM:SS+00:00`) |
| **Scopes** | None (key grants full channel access) | **Granular scopes** enforced per endpoint (e.g. `parcels:create`) |
| **Bulk** | Synchronous batches | Large batches go **async** → `202` + a job to poll |

## Core facts

| Topic | Value |
|---|---|
| **Base URL** | `https://api.qapla.it/v2` (all routes prefixed `/v2` since v2.8.6) |
| **Auth** | `POST /v2/auth/token` with `{"apiKey": "..."}` → JWT; send it as `Authorization: Bearer <token>`. Token lives **24h**. See [`authentication.md`](authentication.md) |
| **Content type** | JSON in, JSON out. Errors are `application/problem+json` |
| **Errors** | Standard HTTP status + RFC 7807 body. `422` carries a `violations[]` array of field errors |
| **Time** | UTC, ISO 8601. Responses use ATOM (`…+00:00`); sandbox datetime input uses `"Y-m-d H:i:s"` |
| **Rate limit** | Token bucket (default 120 capacity, refill 2/sec), Redis-backed. Over limit → `429` with `X-RateLimit-*` headers. Your channel's actual limits come back in the token response (`rate_limit`) |
| **Async jobs** | Bulk writes (>10 items) return `202 Accepted` + a job; poll `GET /v2/jobs/{jobId}` until `completed`/`failed`. See below |
| **Product gating** | Some resources require an active product on the channel; otherwise `403` with `detail: PRODUCT_NOT_OWNED` |
| **Caching** | Read endpoints support HTTP **ETag** / `304 Not Modified` (`X-Cache-Status: HIT\|MISS`, `Cache-Control: max-age=3600`) |
| **Version** | `2.9.4` (2026-06-16). Tracks `qore/api`, evolving independently of v1.x |

## Async jobs pattern

Write operations on a large batch don't block. The rule of thumb in the current
implementation: **≤10 items → synchronous** (`201`, full result inline); **>10
items → asynchronous** (`202`, a job to poll).

A `202` returns an **AsyncJobResponse**:

```json
{
  "jobId": "a1b2c3…",
  "status": "processing",
  "statusUrl": "/jobs/a1b2c3…",
  "hashes": ["…", "…"],
  "totalParcels": 50
}
```

Then poll `GET /v2/jobs/{jobId}`:

```json
{
  "jobId": "a1b2c3…",
  "type": "create_parcels",
  "status": "pending|processing|completed|failed",
  "totalItems": 50,
  "processedItems": 50,
  "failedItems": 0,
  "result": { },
  "error": null,
  "createdAt": "2026-06-21T10:00:00+00:00",
  "completedAt": "2026-06-21T10:00:07+00:00"
}
```

Poll until `status` is `completed` or `failed`. Several write endpoints also accept
an optional `webhookUrl` so the job can notify you on completion instead of polling.

Samples: [`../examples/v2/createParcelsAsync.response.json`](../examples/v2/createParcelsAsync.response.json)
(the `202`) and [`../examples/v2/job.response.json`](../examples/v2/job.response.json)
(a finished job). An RFC 7807 error body looks like
[`../examples/v2/error.problem.json`](../examples/v2/error.problem.json).

## Where to go next

1. [`authentication.md`](authentication.md) — the token exchange and Bearer flow (read first).
2. [`endpoints.md`](endpoints.md) — the v2 catalog: stable resources + what's still in flight.
3. Deep-dives for the stable resources: [`parcels.md`](parcels.md), [`sandbox.md`](sandbox.md).
4. The bundled v2 client [`../../scripts/qapla_v2_client.py`](../../scripts/qapla_v2_client.py)
   (token exchange, Bearer, RFC 7807 errors, `429` retry, job polling) and the
   runnable sample payloads in [`../examples/v2/`](../examples/v2/).
5. The live Swagger UI at <https://api.qapla.dev/v2/> for anything not covered here
   or that may have changed.

> **When should I use v2 vs v1.3?** For now, v1.3 remains the documented target for
> most integrations (see [`../versioning.md`](../versioning.md) and
> [`../migration.md`](../migration.md)). Reach for v2 when you specifically need a
> resource it already exposes well (e.g. the parcels model) or its model (JWT,
> REST, async jobs). v1.3 and v2 **coexist**; v1.3 is not being retired abruptly.
