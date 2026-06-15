# pushShipment

**Endpoint:** `POST https://api.qapla.it/1.3/pushShipment`
**Pillar:** 1 (tracking). **Batch:** yes (array).

Insert shipments that **already have a tracking number** into Qapla' so they
enter active tracking and trigger transactional events. Use this when the label
was produced outside Qapla' (your own system, the carrier portal, a virtual
courier) and you only need tracking + notifications.

> If instead you want Qapla' to generate the label, use `pushOrder` →
> `createLabel` → `confirmLabel`.

## Request shape

```json
{
  "apiKey": "YOUR_KEY",
  "pushShipment": [ { /* shipment 1 */ }, { /* shipment 2 */ } ]
}
```

Full runnable sample: `examples/pushShipment.request.json` (response in
`examples/pushShipment.response.json`).

## Per-shipment fields

**Required (marked `*` in the docs):**

| Field | Meaning |
|---|---|
| `trackingNumber` | The carrier tracking number / waybill |
| `courier` | Qapla' courier code (e.g. `DHL`, `UPS`, `GLS`). See `getCouriers` |
| `shipDate` | Ship date (`YYYY-MM-DD`) |

**Required to activate transactional emails/SMS** (these four are the fields the
docs mark with `•` — without them notifications can't be sent):

| Field | Meaning |
|---|---|
| `reference` | Your order reference |
| `name` | Recipient name |
| `email` | Recipient email |
| `telephone` | Recipient phone |

**Recommended (recipient address & tracking-page data):**

| Field | Meaning |
|---|---|
| `street`, `city`, `ZIP`, `state`, `country` | Recipient address. `country` is ISO 3166-1 alpha-2 (e.g. `IT`) |
| `orderDate` | Order date (`YYYY-MM-DD`) |
| `language` | ISO 639-1 (e.g. `it`, `fr`). Unknown/null → `it` |

**Optional / advanced:**

| Field | Meaning |
|---|---|
| `amount` | Shipment value to communicate to the customer (e.g. COD) |
| `pod` / `isCOD` | Cash-on-delivery flag |
| `shipping` | Shipping cost |
| `custom1`–`custom3` | Free custom values (echoed in the response) |
| `note` | Note (max 255 chars) |
| `isReturnable` | Whole-shipment return allowed |
| `tag` | Group tag |
| `deliveryDate`, `latestShipDate`, `latestDeliveryDate` | Date hints |
| `isTrackingNumber` | `true` when `trackingNumber` is the **real** TN. Some carriers (e.g. BRT) first return a `parcelID` that is not yet the definitive TN — set `false` in that case |
| `origin` | Source platform (e.g. `magento`) |
| `platformOrderID` | Order ID on the source platform |
| `agent` | A commercial contact email for the customer |
| `parcels[]` | `weight`, `length`, `width`, `height`, `boxCode`, `content`, `originCountry` |
| `rows[]` | Order line items: `sku`, `name`, `qty`, `weight`, `price`, `total`, `url`, `imageUrl`, `isReturnable`, `customsCode`, … |

## Response

Top-level `result`/`error` plus `count`, `imported`, and a `shipments[]` array
with **per-item** `result`/`error`. Successful items return `id`, `url`,
`hash` (the public tracking-page token), and echo `trackingNumber`/`reference`/
`custom*`.

Always loop `shipments[]` and check each `result` — the call can be `OK` while
individual items are `KO` (e.g. `"Invalid courier"`).

## Common errors

- `Invalid courier` — `courier` code not recognized / not enabled on the channel.
- Duplicate tracking numbers are de-duplicated server-side.
- `429 Too Many Requests` — a batch of N counts as N tokens (see
  `conventions.md`).
