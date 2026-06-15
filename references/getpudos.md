# getPudos

**Endpoint:** `POST https://api.qapla.it/1.2/getPudos`
(served under `/1.2/` — there is **no** `1.3` alias).
**Billable product.**

Search **PUDO** points — pickup/drop-off locations (lockers, convenience stores,
post offices) — near an address, for a given courier. Each courier has its own
network. Use the result to ship to a pickup point via `pushOrder`/`createLabel`
(the `PUDO` block).

## Request (key fields)

| Field | Meaning |
|---|---|
| `apiKey` | Channel API Key |
| `courier` | Qapla' courier code whose PUDO network to search |
| address fields | The address/coordinates to search around (ZIP, city, country, …) |

> Parameter names and which couriers are supported are carrier-dependent —
> confirm against <https://api.qapla.dev/1.2/getPudos>.

## Response (structure)

Returns a list of service points. Each `ServicePoint` typically includes:

- identifier/code of the point
- name and full address
- geo coordinates
- `businessDays` / opening hours
- a `statusCode` for availability

## Using a PUDO in a shipment

The chosen pickup point is passed back in the `PUDO` block of `pushOrder` /
`createLabel` (sometimes referred to as `pushOrderPUDO`). Required PUDO fields
vary per courier — check the per-courier requirements in the `createLabel` docs.

## Notes

- Billable + a live call to the carrier — cache results where sensible.
- Official docs: <https://api.qapla.dev/1.2/getPudos>.
