# getQuotes

**Endpoint:** `POST https://api.qapla.it/1.3/getQuotes`
**Billable product** (each quote request may be charged). Supports sandbox.
**Must be activated by Qapla' Customer Care before use.**

Get **real-time multi-carrier shipping quotes** for a destination + shipment
value, before deciding how to ship. Returns one entry per courier, each with one
or more service quotes (cost, estimated pickup/delivery dates).

> ⚠️ **Auth is different here.** Unlike every other v1.3 endpoint, `getQuotes`
> does **not** take `apiKey` in the JSON body. The key goes in an HTTP **header**
> `x-api-key`, and sandbox is the header `x-sandbox: "true"|"false"`.

## Request

Headers:

| Header | Required | Meaning |
|---|---|---|
| `x-api-key` | yes | Channel API Key |
| `x-sandbox` | no | `"true"` to run in sandbox (returned values may be unrealistic; GLS-ITA has no sandbox and is always sent to production) |

Body (note the **nested `recipient` object** and the `amount*` field names):

```json
{
  "reference": "unique",
  "senderCode": "SENDER",
  "recipient": {
    "street": "Address",
    "city": "Milano",
    "province": "MI",
    "zipCode": "20100",
    "country": "IT"
  },
  "currency": "EUR",
  "amountShipment": "200.20",
  "amountInsurance": "200.20",
  "amountCash": "200.20",
  "parcels": [
    { "weight": 0.8, "height": 12.0, "length": 10.0, "width": 20.0 }
  ],
  "couriers": ["UPS", "DHL"]
}
```

Full samples: `examples/getQuotes.request.json` and
`examples/getQuotes.response.json`.

## Body fields

| Field | Required | Meaning |
|---|---|---|
| `reference` | yes | Your reference, echoed back |
| `senderCode` | no | Sender code (configured sender) |
| `recipient` | yes | Recipient object (see below) |
| `recipient.street` | yes | Street/address |
| `recipient.city` | yes | City (use the international/English name abroad) |
| `recipient.country` | yes | ISO alpha-2 code |
| `recipient.zipCode` | no | Recipient ZIP |
| `recipient.province` | no | Province/state |
| `currency` | no | Currency for the amounts |
| `amountShipment` | yes | Shipment value, float `#.##` (no symbol) |
| `amountInsurance` | no | Insured value |
| `amountCash` | no | Cash-on-delivery amount |
| `parcels[]` | yes | One or more parcels, each with `weight`, `width`, `height`, `length` (all required per parcel) |
| `couriers[]` | no | Restrict the quote to these courier codes; omit for all enabled |

## Response structure

Wrapped in `getQuotes`:

| Field | Meaning |
|---|---|
| `result` | `OK`/`KO` |
| `version` | API version (e.g. `1.3.0`) |
| `reference` | Echoed request reference |
| `quotationId` | UUID of the quote request |
| `startTimestamp` / `endTimestamp` | RFC3339 processing window |
| `couriers[]` | One per courier, each with `code`, `quotes[]`, and courier-level `messages[]` |

Each `couriers[].quotes[]` entry:

| Field | Meaning |
|---|---|
| `service.courierCode` | Carrier service code |
| `service.qaplaCode` | Qapla' service code |
| `service.description` | Human-readable service name |
| `messages[]` | Per-quote messages: `{ type, code, content }` |
| `deliveryOptions` | Delivery options (may be `null`) |
| `currency` | Currency of the quoted amount |
| `amount` | The quoted price |
| `expectedPickupDate` | Estimated pickup date (may be `null`) |
| `expectedDeliveryDate` | Estimated delivery date (may be `null`) |

> Quoted costs are reference rates and may differ from the final invoice
> (carriers return a `messages[]` note about this). Check the live docs.

## Notes

- This is a real-time call to carriers; expect higher latency than a plain DB
  read, and quotes that vary over time.
- Use the `x-sandbox` header while developing.
- The service codes returned (`service.courierCode` → `courierService`,
  `service.qaplaCode`) feed into `createLabel` to ship with the chosen service.
- Official docs: <https://api.qapla.dev/1.3/getQuotes>.
