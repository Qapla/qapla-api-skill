# getQuotes

**Endpoint:** `POST https://api.qapla.it/1.3/getQuotes`
**Billable product** (each quote request may be charged). Supports `sandbox`.

Get **real-time multi-carrier shipping quotes** for a destination + shipment
value, before deciding how to ship. Returns one entry per courier, each with one
or more service quotes (cost, estimated pickup/delivery dates).

## Request shape

```json
{
  "apiKey": "YOUR_KEY",
  "reference": "QUOTE-001",
  "address": "...",
  "postCode": "35010",
  "city": "Padova",
  "state": "PD",
  "country": "IT",
  "value": 109.25
}
```

Full samples: `examples/getQuotes.request.json` and
`examples/getQuotes.response.json`.

## Key request fields

| Field | Required | Meaning |
|---|---|---|
| `apiKey` | yes | Channel API Key |
| `reference` | rec. | Your reference, echoed back. Allowed chars: letters, digits, `-`, `_`, `.` |
| `address` | rec. | Recipient address (incl. street number if available) |
| `postCode` | yes in EU | Recipient ZIP |
| `city` | yes | For international, use the international (English) city name |
| `state` | yes in IT | Province (IT) or state where applicable |
| `country` | yes | ISO alpha-2 code |
| `value` | yes | Shipment value in `currency`, float `#.##` (no symbol) |

## Response structure

Top-level: `result` (`OK`/`KO`), `version`, `reference` (echoed), `id`
(UUIDv4 request id), `receivedAt` / `processedAt` (RFC3339).

Then `couriers[]`, each with:

| Field | Meaning |
|---|---|
| `courier` | Qapla' courier code |
| `quotes[]` | One per service, each with: |
| └ `courierService` | Carrier service code |
| └ `qaplaService` | Qapla' service code |
| └ `serviceName` | Human-readable service name |
| └ `currency` | Currency of the quoted cost |
| └ `cost` | The quoted price |
| └ `pickupDate` | Estimated pickup date (`yyyy-MM-dd`) |
| └ `deliveryDate` | Estimated delivery date (`yyyy-MM-dd`) |

> Quoted costs may be net of VAT depending on the courier — check the live docs.

## Notes

- This is a real-time call to carriers; expect higher latency than a plain DB
  read, and quotes that vary over time.
- Use `sandbox` while developing.
- The carrier/service codes returned (`courier`, `courierService`) feed directly
  into `createLabel`.
- Official docs: <https://api.qapla.dev/1.3/getQuotes>.
