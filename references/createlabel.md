# createLabel

**Endpoint:** `POST https://api.qapla.it/1.3/createLabel` (also `1.4`).
**Pillar:** 3 (labels). **Batch:** single object (one label per call).

Generate a carrier label by calling the carrier's API through Qapla'. In v1.3
the call is **synchronous** (you get the label back). v1.4 adds
`parcelsTracking` for richer multi-parcel tracking.

After a label is created it must be confirmed/transmitted with `confirmLabel`
to actually hand it to the carrier; on transmission the shipment enters tracking
(pillars 1 & 2).

## Request shape

```json
{
  "apiKey": "YOUR_KEY",
  "sandbox": true,
  "includeExtShipmentID": false,
  "createLabel": { /* single label */ }
}
```

Full runnable sample: `examples/createLabel.request.json`. **Always develop with
`"sandbox": true`** to avoid real carrier pickup requests and billing.

## Key fields

**Required core:**

| Field | Meaning |
|---|---|
| `courier` | Qapla' courier code (e.g. `CRONO-PTI`, `GLS`, `BRT`) |
| `courierService` | Carrier service code (e.g. `P46`) — valid values depend on the courier |
| `name`, `address`, `city`, `state`, `postCode`, `country` | Recipient (`country` = ISO alpha-2) |
| `email`, `telephone` | Recipient contacts |
| `parcels[]` | At least one parcel: `weight`, `length`, `width`, `height` (`boxCode`, `content`, `originCountry` optional) |

**Order / commercial:**

`reference`, `orderID`, `origin`, `amount`, `shippingCost`, `currencyCode`,
`payment`, `isCOD`, `notes`, `custom1`–`custom3`, `content`, `costCenterCode`.

**Shipping options:**

`shippingCODPaymentOption`, `shippingInsurance`, `shippingDeliveryOptions`,
`shippingRequiredDeliveryDate`, `shippingRequiredDeliveryTimeSlot` (`HS-HE`),
`pickupDate`.

**Advanced blocks:**

| Block | Meaning |
|---|---|
| `PUDO` | Deliver to a pickup point — required fields **vary per courier** (see `getpudos.md`) |
| `invoice` | Invoice data |
| `tradeDocuments` / customs / FedEx blocks | International shipments — customs documentation |
| `rows[]` | Line items |
| `parcelsTracking` | (v1.4) per-parcel tracking info |

## Response

Returns the generated label reference and the label content/URL (PDF/ZPL,
depending on the courier and channel config), plus the usual `result`/`error`.

## Common errors & gotchas

- Invalid/disabled `courier` or wrong `courierService` for that courier.
- Missing carrier-specific required fields (customs for non-EU, PUDO blocks).
- Some couriers (e.g. BRT, STEF_IT) return a `parcelID` that is **not yet** the
  definitive tracking number — the real TN is assigned later, asynchronously.
- Required field sets differ a lot per courier — verify against the live docs:
  <https://api.qapla.dev/1.3/createLabel>.

## v1.3 vs v1.4

- v1.3: synchronous label creation.
- v1.4: adds `parcelsTracking`; see <https://api.qapla.dev/1.4/createLabel>.
