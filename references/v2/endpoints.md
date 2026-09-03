# Endpoint catalog (v2)

All v2 routes live under `https://api.qapla.it/v2/` and take a **Bearer JWT**
(`Authorization: Bearer <token>`) — never `apiKey` in the body. See
[`authentication.md`](authentication.md) and [`overview.md`](overview.md) for the
shared conventions (RFC 7807 errors, ETag/`304`, async jobs, granular scopes,
and the **mixed** date/time formats — v2 is not uniformly UTC).

> **Two tiers below.** The **stable core** is documented in depth in this skill and
> was verified against the deployed `qore/api`. The **second tier** is published in
> the Swagger but not written up here in depth, and its contracts may still move —
> build against the live docs (<https://api.qapla.dev/v2/>) when you need them.

## Stable core (documented here)

| Method(s) | Path | Purpose | Scope |
|---|---|---|---|
| `POST` | [`/v2/auth/token`](authentication.md) | Exchange `apiKey` → Bearer JWT | — |
| `POST` | [`/v2/parcels`](parcels.md) | Create parcels for an order (≤10 sync, >10 async) | `parcels:create` |
| `GET` | [`/v2/parcels`](parcels.md#list--get-v2parcels) | List parcels of an order (paginated) | `parcels:read` |
| `GET` | [`/v2/parcels/{hash}`](parcels.md#get-one--get-v2parcelshash) | Get one parcel | `parcels:read` |
| `PATCH` | [`/v2/parcels/{hash}`](parcels.md#update--patch-v2parcelshash) | Update a parcel | `parcels:update` |
| `DELETE` | [`/v2/parcels/{hash}`](parcels.md#delete) | Delete a parcel | `parcels:delete` |
| `DELETE` | [`/v2/parcels`](parcels.md#delete) | Delete all parcels of an order | `parcels:delete` |
| `GET` | [`/v2/jobs/{jobId}`](overview.md#async-jobs-pattern) | Poll an async job's status/result | `jobs:read` |
| `GET`/`POST` | [`/v2/sandbox`](sandbox.md) | CRUD playground entity (list / create) | `sandbox:read` / `sandbox:write` |
| `GET`/`PUT`/`PATCH`/`DELETE` | [`/v2/sandbox/{id}`](sandbox.md) | CRUD playground entity (read / replace / update / delete) | `sandbox:read` / `sandbox:write` |
| `POST` | [`/v2/couriers/delivery-times`](couriers.md#compare-delivery-times--post-v2couriersdelivery-times) | Rank couriers fastest-first for a destination CAP | `delivery-times:read` |
| `POST` | [`/v2/couriers/efficiency-index`](couriers.md#score-courier-efficiency--post-v2couriersefficiency-index) | Score couriers 0–100 (speed + consistency + reliability) for a destination CAP | `efficiency-index:read` |
| `POST` | [`/v2/shipments/{id}/stock-release`](stock-release.md) | Ask the courier to redeliver / redeliver elsewhere / return to sender a shipment held in depot | `shipments:write` |

## Published, but not written up in depth here

⚠️ These **are** in the public Swagger — the spec snapshot was stale for a long
time and was regenerated on 2026-09-03 (2.14.0 → 2.21.9), which is when they
appeared. They are simply not documented in detail in this skill, and their
contracts may still move. **Do not hardcode** against them from this skill —
confirm on <https://api.qapla.dev/v2/>.

| Resource | Methods (observed) | Notes |
|---|---|---|
| `orders` | `GET`/`POST` `/v2/orders`, `GET`/`PUT`/`PATCH`/`DELETE` `/v2/orders/{id}` | Order CRUD; lookup by `(reference, source)` |
| `shipments` | `POST`/`GET` `/v2/shipments`, `GET /v2/shipments/{id}` | Bulk create (max 100), search, read. (The `stock-release` action on an existing shipment is already stable — see above) |
| `labels` | `POST /v2/labels` | Create shipping label (idempotent) |
| `couriers` | `GET /v2/couriers`, `GET /v2/couriers/{code}` | List couriers / get by code. (The `delivery-times`/`efficiency-index` benchmark endpoints are already stable — see above) |

> Internal/admin routes (`/v2/admin/*`) exist for operations tooling and are not
> part of the public API — ignore them for integrations.

## How v2 maps onto the v1.3 mental model

| You want to… | v1.3 | v2 (today) |
|---|---|---|
| Authenticate | `apiKey` per call | `POST /v2/auth/token` → Bearer JWT |
| Import an order | `pushOrder` | `POST /v2/orders` |
| Manage packages | (part of order/label) | `POST/GET/PATCH/DELETE /v2/parcels` ✅ |
| Track a shipment | `pushShipment` / `getShipment` | `/v2/shipments` |
| Generate a label | `createLabel` → `confirmLabel` | `POST /v2/labels` |
| List couriers | `couriers` / `getCouriers` | `/v2/couriers` |
| Release a held shipment | *(no v1.3 equivalent)* | `POST /v2/shipments/{id}/stock-release` ✅ |
| Compare/score couriers on a lane | *(no v1.3 equivalent)* | `POST /v2/couriers/delivery-times` / `efficiency-index` ✅ |

For the version policy and when to choose v1.3 vs v2, see
[`../versioning.md`](../versioning.md) and [`../migration.md`](../migration.md).
