# pushOrder

**Endpoint:** `POST https://api.qapla.it/1.3/pushOrder`
**Pillar:** 3 (labels). **Batch:** yes (array, ~100 max per request).

Import **raw orders** into Qapla' so they can later become labels. This is the
first step of the label pillar: `pushOrder` → `createLabel` → `confirmLabel`.

`pushOrder` performs an **upsert** keyed on your order identity: re-sending an
order with a newer `updatedAt` updates the existing record instead of
duplicating it.

## Request shape

```json
{
  "apiKey": "YOUR_KEY",
  "origin": "magento2",
  "pushOrder": [ { /* order 1 */ }, { /* order 2 */ } ]
}
```

Full runnable sample: `examples/pushOrder.request.json`.

## Required per-order fields (marked `*` in the docs)

`reference`, `courier`, `createdAt`, `updatedAt`, `name`, `street`, `city`,
`state`, `postCode`, `country` are **mandatory** for each order (plus the
root-level `apiKey`). Everything in the next table beyond these is optional.

## Per-order fields (common)

| Field | Meaning |
|---|---|
| `reference` | Your order reference (recommended unique) — **required** |
| `orderID` | Order ID on the source platform (optional) |
| `courier` | Desired courier code — **required**. `courierService` (service code) is optional at import |
| `status` | Order status string (optional) |
| `createdAt`, `updatedAt` | `YYYY-MM-DD HH:MM:SS` — **required**. `updatedAt` drives the upsert |
| `name`, `street`, `city`, `state`, `postCode`, `country` | Recipient address — **required** (`country` = ISO alpha-2). **Note:** here the ZIP field is `postCode` (not `ZIP` as in `pushShipment`) |
| `email`, `telephone` | Recipient contacts |
| `amount`, `shippingCost`, `currencyCode` | Order totals |
| `payment`, `isCOD` | Payment method / cash-on-delivery |
| `notes` | Order notes |
| `isReturnable` | Whole-order return allowed |
| `costCenterCode` | Cost-center code |

**Shipping hints / options:**

`shippingCODPaymentOption`, `shippingInsurance`, `shippingDeliveryOptions`,
`shippingRequiredDeliveryDate`, `latestShipDate`, etc.

**Nested blocks:**

| Block | Meaning |
|---|---|
| `parcels[]` | One entry per parcel: `width`, `height`, `weight`, `length`, `boxCode`, `content`, `originCountry` |
| `rows[]` | Line items (sku/name/qty/price/…) |
| `sender` | Override sender details |
| `invoice` | Invoice data |
| `PUDO` | Pickup-point destination (see `getpudos.md`) |
| FedEx / customs blocks | International / customs fields (carrier-specific) |

> Carrier- and destination-specific required fields vary widely (customs for
> international, PUDO blocks, FedEx). Check the live docs at
> <https://api.qapla.dev/1.3/pushOrder> for the exact requirements.

## Response

Top-level `result`/`error` plus counters describing how many orders were
created vs updated vs failed, with per-item detail. Always inspect per-item
results.

## Notes

- `origin` identifies the source platform and can be set at root and/or per
  order.
- Max ~100 orders per request; a batch of N costs N rate-limit tokens.
- After import, an order can be marked ready (`markOrderReady`) and turned into
  a label with `createLabel`.
