# Webhooks — receiver reference (Pillar 2)

Qapla' webhooks are **outbound HTTP POST callbacks**: you register an HTTPS URL on
a channel, and Qapla' calls it when something happens to a shipment or order.
This is the **push** model for Pillar 2 (transactional events) — your job is to
expose an endpoint, verify the payload, and reply with the exact contract body.

> **Source of truth (always):** <https://webhook.qapla.dev>. The webhook service
> is an integral part of the API but is documented separately from
> <https://api.qapla.dev/1.3/>. This file mirrors it so you can work offline; if
> anything drifts, trust the live docs.

## Event types

| Type | Trigger | Add-on required |
|---|---|---|
| **Shipments** | Every carrier status change on a tracked shipment | — |
| **Shipments Return** | A customer return is registered | *Resi automatici* service |
| **Orders** | Shipment creation **or** first transmission to the carrier (selectable per channel) | — |

## Per-channel configuration

Webhooks are configured **per channel** in the Control Panel (<https://cp.qapla.it>):
**Impostazioni → Canali → [canale] → Configura → Canale**.

- Set the webhook **URL**.
- Copy the channel's **API Key Privata** — this is the `apiKey` value that will
  arrive in every payload; you validate against it.
- Optionally enable the **v1.3 enhanced payload** to receive product line items,
  parcel dimensions, and recipient (`consignee`) details alongside the core
  tracking fields.
- For the *Orders* event, pick the trigger (creation vs carrier transmission)
  under **Aggiornamenti → Webhook**.
- *Shipments Return* webhooks require the *Resi automatici* service on the channel.

## Payload — Shipments (status change)

Sent as `Content-Type: application/json`. Core fields (v1.2 baseline):

```json
{
  "apiKey": "YOUR_CHANNEL_PRIVATE_KEY",
  "trackingNumber": "XX580104809",
  "courier": "GLS-ITA",
  "reference": "ORDER-51704",
  "date": "2024-03-15 10:22:00",
  "courierStatus": "delivered",
  "place": "Milan, IT",
  "qaplaStatusID": 99,
  "qaplaStatus": "CONSEGNATO",
  "statusDetails": [],
  "return": 0,
  "hasChildren": 0,
  "isChild": 0,
  "custom1": "",
  "custom2": "",
  "custom3": ""
}
```

| Field | Description |
|---|---|
| `apiKey` | The channel's **private** key — always verify it matches your stored key |
| `trackingNumber` | Carrier tracking number |
| `courier` | Qapla' courier code (e.g. `GLS-ITA`) |
| `reference` | Your order reference |
| `date` | Timestamp of the status event (`YYYY-MM-DD HH:MM:SS`, CEST) |
| `courierStatus` | Raw status text from the carrier — **do not branch on this** |
| `qaplaStatusID` | Canonical Qapla' status id — **branch on this** (see `statuses.md`) |
| `qaplaStatus` | Human-readable canonical label (localized) |
| `statusDetails` | Array of `{id, detail}` sub-state objects |
| `place` | Last known location text |
| `return` / `hasChildren` / `isChild` | Flags (`0`/`1`) for returns and multi-parcel groups |
| `custom1`–`custom3` | Merchant-defined metadata |

> **Branch on `qaplaStatusID`, never on `courierStatus`.** Raw carrier strings are
> unstable across couriers and versions; the canonical id is the stable contract.
> Full id table in [`statuses.md`](./statuses.md).

### v1.3 enhanced payload — extra objects

When the enhanced payload is enabled, three more objects are appended:

```json
{
  "rows": [
    {
      "id": 1, "sku": "WIDGET-42", "name": "Widget",
      "price": 9.99, "total": 19.98, "qty": 2,
      "weight": 0.3, "netWeight": 0.28, "unitOfMeasurement": "kg",
      "url": "https://store.example.com/widget",
      "imageUrl": "https://cdn.example.com/widget.jpg",
      "isReturnable": true, "customsCode": "9503.00",
      "originCountry": "IT", "notes": "", "parcelID": 1
    }
  ],
  "parcels": [
    {
      "boxCode": "BOX-M", "weight": 1.2,
      "length": 30, "width": 20, "height": 15,
      "originCountry": "IT", "content": "Electronics"
    }
  ],
  "consignee": {
    "name": "Jane Doe", "address": "Via Roma 1", "city": "Milan",
    "state": "MI", "postCode": "20100", "country": "IT",
    "email": "jane@example.com", "phone": "+39 02 1234567"
  }
}
```

## Payload — Shipments Return

Sent when a customer return is registered (requires *Resi automatici*). The
payload is wrapped in a `webhookReturnShipments` envelope and can carry several
returns:

```json
{
  "webhookReturnShipments": {
    "id": "evt-123",
    "apiKey": "YOUR_CHANNEL_PRIVATE_KEY",
    "version": 1.3,
    "count": 1,
    "returnShipments": [
      {
        "date": "2024-03-20 14:05:00",
        "reference": "ORDER-51704",
        "RMA": "RMA-9981",
        "parcels": 1,
        "weight": 1.2,
        "trackingNumber": "RT580104809",
        "refundMethodCode": "ORIGINAL",
        "courier": { "code": "GLS-ITA", "name": "GLS", "icon": "https://cdn.qapla.it/couriers/gls.svg" },
        "sender": {
          "name": "Jane Doe", "address": "Via Roma 1", "city": "Milan",
          "state": "MI", "postCode": "20100", "country": "IT",
          "email": "jane@example.com", "telephone": "+39 02 1234567"
        },
        "consignee": {
          "name": "Acme Warehouse", "address": "Via Logistica 9", "city": "Bologna",
          "state": "BO", "postCode": "40100", "country": "IT"
        },
        "rows": [
          { "sku": "WIDGET-42", "name": "Widget", "qty": "1", "total": "9.99", "reason": "Wrong size" }
        ]
      }
    ]
  }
}
```

Note the orientation flip versus an outbound shipment: on a return, `sender` is
the **customer** and `consignee` is the **merchant/warehouse**.

## Payload — Orders

Sent on shipment creation or first carrier transmission (per the channel's
trigger setting). The `orders` array may contain one or more entries:

```json
{
  "apiKey": "YOUR_CHANNEL_PRIVATE_KEY",
  "orders": [
    {
      "reference": "ORDER-51704",
      "orderDate": "2024-03-14 09:00:00",
      "shipDate": "2024-03-15 08:30:00",
      "courier": "GLS-ITA",
      "trackingNumber": "XX580104809",
      "return": null,
      "returnTrackingNumber": null,
      "weight": 1.2, "parcels": 1, "length": 30, "width": 20, "height": 15,
      "amount": "€ 28.74", "isPOD": false,
      "customerName": "Jane Doe", "customerAddress": "Via Roma 1",
      "customerCity": "Milan", "customerState": "MI", "customerZip": "20100",
      "customerCountry": "IT", "customerTelephone": "+39 02 1234567",
      "customerEmail": "jane@example.com", "notes": ""
    }
  ]
}
```

## Response contract

Your endpoint **must** reply with exactly one of these JSON bodies:

| Outcome | Response body |
|---|---|
| Success | `{"result":"OK"}` |
| Failure | `{"result":"KO"}` |

Anything else — an empty body, an HTML error page, or a non-2xx status — is
treated as a failure and triggers the retry logic. (This mirrors the standard API
envelope, where `result` is `OK`/`KO`.)

## Retry and auto-disable

- **Retries:** on `{"result":"KO"}` or a malformed/missing response, Qapla'
  retries the delivery **2 more times** over the following hours (3 attempts
  total per event).
- **Auto-disable:** after **100 consecutive failed deliveries** the webhook is
  automatically deactivated on the channel; you must re-enable it in the Control
  Panel.

## Security and operational guidance

1. **Verify `apiKey`** on every request against your stored channel private key;
   reject with `{"result":"KO"}` if it does not match. Never branch business logic
   before this check.
2. **Use HTTPS.** Plain HTTP endpoints are not supported in practice.
3. **Respond fast** (aim < 2 s). Return the contract body immediately and offload
   DB writes, emails, and downstream calls to a background queue.
4. **Be idempotent.** The same event may arrive more than once (retries). Use
   `trackingNumber` + `qaplaStatusID` + `date` as a dedup key.
5. **Treat the key as a secret** — never commit it to version control.

## Webhooks vs. the pull API

Webhooks are push (Qapla' calls you on change, no polling). If you instead need
to poll status on your own schedule, use the `trackingByTimeFrame` pull endpoint
(returns shipments whose status changed within a time window) — see
[`trackingbytimeframe.md`](./trackingbytimeframe.md). A minimal receiver lives in
[`examples/webhookReceiver.md`](./examples/webhookReceiver.md).
