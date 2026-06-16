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

**Required core (marked `*` in the docs):**

| Field | Meaning |
|---|---|
| `reference` | Your label/order reference |
| `courier` | Qapla' courier code (e.g. `CRONO-PTI`, `GLS`, `BRT`) |
| `courierService` | Carrier service code (e.g. `P46`) — valid values depend on the courier |
| `name`, `address`, `city`, `state`, `postCode`, `country` | Recipient (`country` = ISO alpha-2) |

(plus the root-level `apiKey`.)

**Strongly recommended / usually needed (not flagged mandatory at top level):**

| Field | Meaning |
|---|---|
| `parcels[]` | One or more parcels: `weight`, `length`, `width`, `height` (`boxCode`, `content`, `originCountry` optional). Required in practice by virtually every carrier |
| `email`, `telephone` | Recipient contacts (for notifications) |

**Order / commercial:**

`orderID`, `origin`, `amount`, `shippingCost`, `currencyCode`,
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

## Confirming & transmitting — `confirmLabel`

`createLabel` only **generates** the label. To actually hand the shipment(s) to
the carrier (and trigger entry into tracking + transactional events), confirm
them with `confirmLabel`:

**Endpoint:** `POST https://api.qapla.it/1.3/confirmLabel/` (also `1.2`).
**Note:** must be enabled by Customer Care before use.

```json
{
  "apiKey": "YOUR_KEY",
  "confirmLabel": {
    "courier": "DHL",
    "labelCreationDate": "2026-06-16",
    "pickupDate": "2026-06-18",
    "labelID": [100, 101, 102, 103]
  }
}
```

| Field | Meaning |
|---|---|
| `courier`* | Qapla' courier code |
| `labelCreationDate`* / `labelID`* | Use **one or the other**: confirm all labels created on a date, **or** an explicit array of label IDs from `createLabel`. (Some couriers, e.g. GLS-AT, support only `labelCreationDate`.) |
| `pickupDate` | Chosen pickup date (`YYYY-MM-DD`) — only for certain couriers (CRONO-PTI, DHLPARCEL-ES, FEDEX, GLS-SPAIN, PTI, SDA, SEUR, TNT-ITA, TWS) |
| `pickupTime` | `HH:MM`; requires `pickupDate`; only SDA, CRONO-PTI, FEDEX |

The response returns the **manifest (borderò / distinta di carico)** as a
base64-encoded PDF, plus the confirmation `number`, `date`, and `shipments` count.
A per-label `error` array reports any labels that failed to confirm.

> Full flow: `pushOrder` → `createLabel` → **`confirmLabel`** → shipment enters
> pillars 1 & 2.

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
