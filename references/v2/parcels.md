# Parcels (v2)

**Resource:** `https://api.qapla.it/v2/parcels`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)). Requires the
relevant `parcels:*` scope and the parcels product on the channel (else `403`).

A *parcel* is a physical package belonging to an *order*. An order is identified by
the pair **(`reference`, `origin`)** — your order id plus the source system it came
from (e.g. `shopify`). All units are metric (kg, cm).

> v2 surface as of `qore/api` 2.9.4. Field names are copied verbatim from the
> implementation DTOs — note the request bodies are **camelCase**, and the parcel
> **response** is camelCase too (the sandbox resource, by contrast, responds in
> snake_case). Verify against <https://api.qapla.dev/v2/> if anything looks off.

## Create — `POST /v2/parcels`

Scope: `parcels:create`. Optional request header **`x-label-format`** selects the
returned label format: `PDF` (default) or `ZPL`.

```json
{
  "order": { "reference": "ORDER-123", "origin": "shopify" },
  "parcels": [
    {
      "weightKg": 0.8,
      "lengthCm": 20.0,
      "widthCm": 15.0,
      "heightCm": 10.0,
      "originCountryIso": "IT",
      "contentsDescription": "T-shirt",
      "clientInternalCode": "SKU-001",
      "shippingNotes": "Fragile"
    }
  ],
  "webhookUrl": "https://your.app/qapla/jobs"
}
```

| Field | Required | Meaning |
|---|---|---|
| `order.reference` | yes | Your order identifier |
| `order.origin` | yes | Source system (e.g. `shopify`) |
| `parcels[]` | yes | 1–100 items |
| `parcels[].weightKg` | yes | Weight in kg, positive |
| `parcels[].lengthCm` / `widthCm` / `heightCm` | yes | Dimensions in cm, positive |
| `parcels[].originCountryIso` | yes | ISO 3166-1 alpha-2 (2 chars) |
| `parcels[].contentsDescription` | no | max 255 |
| `parcels[].clientInternalCode` | no | max 255 |
| `parcels[].shippingNotes` | no | max 255 |
| `webhookUrl` | no | Valid URL; notified when an async job finishes |

Sample request: [`../examples/v2/createParcels.request.json`](../examples/v2/createParcels.request.json).

**Responses:**

| Status | When | Body |
|---|---|---|
| `201 Created` | ≤10 parcels (synchronous) | a `ParcelResponse`, or an array if >1 — [example](../examples/v2/createParcels.response.json) |
| `202 Accepted` | >10 parcels (async) | an `AsyncJobResponse` ([example](../examples/v2/createParcelsAsync.response.json)) — poll `GET /v2/jobs/{jobId}` (see [`overview.md`](overview.md#async-jobs-pattern)) |
| `409 Conflict` | An order with the same channel + `origin` + `reference` already exists | RFC 7807 error ([example](../examples/v2/error.problem.json)) |

### ParcelResponse

```json
{
  "parcelHash": "f3a9…",
  "parcelNumber": 1,
  "label": { "format": "PDF", "label": "<base64-or-binary>" },
  "totalParcelCount": 1,
  "originCountryIso": "IT",
  "clientInternalCode": "SKU-001",
  "weightKg": 0.8,
  "lengthCm": 20.0,
  "widthCm": 15.0,
  "heightCm": 10.0,
  "contentsDescription": "T-shirt",
  "shippingNotes": "Fragile",
  "createdAt": "2026-06-21T10:00:00+00:00",
  "updatedAt": null
}
```

`parcelHash` is the parcel's unique id, used in the `/{hash}` routes below.

## List — `GET /v2/parcels`

Scope: `parcels:read`. Lists the parcels of one order.

| Query param | Required | Default | Meaning |
|---|---|---|---|
| `orderReference` | yes | — | The order's reference |
| `orderOrigin` | yes | — | The order's origin |
| `page` | no | 1 | Page number (positive) |
| `limit` | no | 20 | Page size (positive, max 100) |

Returns a paginated envelope (and supports ETag / `304`):

```json
{ "items": [ /* ParcelResponse… */ ], "total": 3, "page": 1, "limit": 20, "pages": 1 }
```

## Get one — `GET /v2/parcels/{hash}`

Scope: `parcels:read`. Returns a single `ParcelResponse` (`200`, or `304` with a
matching ETag). `404` if the hash is unknown.

## Update — `PATCH /v2/parcels/{hash}`

Scope: `parcels:update`. Partial update — send only the fields you want to change;
all are optional, same names/constraints as on create:

```json
{ "weightKg": 1.2, "shippingNotes": "Updated" }
```

Returns the updated `ParcelResponse` (`200`); `404` if not found.

## Delete

Scope: `parcels:delete`.

| Call | Effect |
|---|---|
| `DELETE /v2/parcels/{hash}` | Delete one parcel. `204` on success, `404` if not found |
| `DELETE /v2/parcels?orderReference=…&orderOrigin=…` | Delete **all** parcels of an order. `204` on success, `404` if none found |

## Notes

- Bulk create is the place to expect async: >10 parcels → `202` + job. Wire a
  `webhookUrl` or poll `/v2/jobs/{jobId}`.
- The pair `(orderReference, orderOrigin)` is how you address an order everywhere —
  there is no separate numeric order id on this resource.
- Live reference: <https://api.qapla.dev/v2/>.
