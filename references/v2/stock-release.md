# Stock release (v2)

**Resource:** `https://api.qapla.it/v2/shipments/{id}/stock-release`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)). Scope:
`shipments:write`.

Asks the courier to act on a shipment currently held in depot (**giacenza**):
re-deliver it, re-deliver it to a new address, or return it to the sender. The
shipment must belong to the authenticated channel and currently be held in
depot.

> v2 surface as of `qore/api` **2.12.0** (2026-07-06). This is a single action
> endpoint on the `shipments` resource — the general `shipments` CRUD (bulk
> create, search, read) is still in flight; see [`endpoints.md`](endpoints.md).
> Also billable in principle, but — like [`couriers.md`](couriers.md) — the
> product-ownership gate is not wired yet; a valid token + scope is enough for
> now.

## Request — `POST /v2/shipments/{id}/stock-release`

`{id}` is the numeric id of the shipment held in depot.

```json
{
  "action": "redeliver_new_address",
  "notes": "Ring the bell twice",
  "address": {
    "name": "Mario Rossi",
    "street": "Via Roma 1",
    "city": "Milano",
    "zip": "20100",
    "province": "MI",
    "phone": "+39061234567"
  }
}
```

| Field | Required | Meaning |
|---|---|---|
| `action` | yes | `redeliver` \| `redeliver_new_address` \| `return_to_sender` |
| `notes` | no | Free-text note for the courier |
| `address` | **iff** `action = redeliver_new_address` | New delivery address — `name`, `street`, `city`, `zip`, `province` required, `phone` optional. `422` if missing when required, or present when not allowed |

Sample: [request](../examples/v2/stockRelease.request.json) /
[response](../examples/v2/stockRelease.response.json).

## Response

The call is always accepted synchronously; the real outcome is carried by
`courierOutcome`:

```json
{
  "status": "sent",
  "courierOutcome": "ok",
  "message": "OK",
  "releaseId": 12345
}
```

| Field | Meaning |
|---|---|
| `status` | Always `"sent"` — accepted and transmitted to the courier |
| `courierOutcome` | `ok` \| `error` for synchronous couriers (**GLS**, **TNT**); `pending` for deferred couriers (**BRT** — transmitted asynchronously by an FTP daemon, real outcome shows up later in the shipment's tracking events) |
| `message` | Courier outcome message, when available; `null` otherwise |
| `releaseId` | Internal id of the stored release request |

## Errors

| Status | Meaning |
|---|---|
| `403` | Channel context missing from the token, or the token lacks `shipments:write` |
| `404` | Shipment not found, or doesn't belong to the authenticated channel |
| `409` | Shipment is not currently held in depot (no giacenza to release) |
| `422` | Invalid `action`, missing/unexpected `address`, or the carrier rejected the request |
| `429` | Rate limit exceeded |

## Notes

- BRT's `pending` outcome is not final — poll the shipment's tracking events (or
  wait for the next webhook) to see the real result; GLS/TNT resolve inline.
- Live reference: <https://api.qapla.dev/v2/>.
