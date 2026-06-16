# Endpoint catalog (v1.3)

Full list of public endpoints, grouped by area. Call as
`https://api.qapla.it/<version>/<endpoint>` with `apiKey` in the body.
"Ver." is the version under which the endpoint is documented/served (some
modern endpoints are 1.3/1.4; many are still only served under 1.2 — see
[`versioning.md`](versioning.md) for the version policy and which to call).

Endpoints with a dedicated deep-dive in this skill are linked. Some rows also
link a real request/response payload under `examples/`. For all others, the
source of truth is <https://api.qapla.dev/1.3/>.

## Shipments (pillar 1 — tracking)

| Endpoint | Ver. | Purpose |
|---|---|---|
| [`pushShipment`](pushshipment.md) | 1.3 | Insert shipments that already have a tracking number → enter tracking |
| `getShipment` / `getShipments` | 1.3 / 1.2 | Read one / many shipments of the channel (`getShipments` documented under 1.2) — [response example](examples/getShipment.response.json) |
| `getCompanyShipment` / `getCompanyShipments` | 1.3 | Read shipments across **all** channels of the company for a day |
| `updateShipment` | 1.2 | Update a shipment |
| `deleteShipment` / `undeleteShipment` | 1.2 | Soft-delete / restore a shipment |
| [`trackingByTimeFrame`](trackingbytimeframe.md) | 1.2 | Poll shipments whose status changed within a time window (pull alternative to webhooks) |

## Orders (pillar 3 — raw orders → labels)

| Endpoint | Ver. | Purpose |
|---|---|---|
| [`pushOrder`](pushorder.md) | 1.3 | Import raw orders (max ~100/request) |
| `getOrder` / `getOrders` | 1.3 / 1.2 | Read one / many raw orders (`getOrders` documented under 1.2) — [response example](examples/getOrder.response.json) |
| `updateOrder` | 1.2 | Update a raw order |
| `markOrderReady` | 1.3 | Mark an order ready for label creation — [request example](examples/markOrderReady.request.json) |
| `deleteOrder` / `undeleteOrder` | 1.2 | Soft-delete / restore a raw order |

## Labels (pillar 3 — generation & transmission)

| Endpoint | Ver. | Purpose |
|---|---|---|
| [`createLabel`](createlabel.md) | 1.3 / 1.4 | Generate a carrier label (1.4 adds `parcelsTracking`) |
| `createReturnLabel` | 1.2 | Generate a return label |
| `confirmLabel` | 1.2 / 1.3 | Confirm/transmit label(s) to the carrier → triggers entry into tracking |
| `getLabel` | 1.2 | Retrieve a generated label (PDF/ZPL) |
| `checkLabel` | 1.2 | Check label status |
| `deleteLabel` | 1.2 | Delete a generated label |

## Quotes & pickup points (billable products)

| Endpoint | Ver. | Purpose |
|---|---|---|
| [`getQuotes`](getquotes.md) | 1.3 | Real-time multi-carrier shipping quotes |
| [`getPudos`](getpudos.md) | 1.2 | Search pickup/drop-off points near an address for a carrier |

## Couriers

| Endpoint | Ver. | Purpose |
|---|---|---|
| `getCouriers` | 1.2 | List couriers enabled on the channel |
| `detectCourier` | 1.2 | Detect a courier from a tracking number |
| `detectOrderCourier` | 1.2 | Suggest a courier for an order by applying the channel's shipping rules |

## Address & utilities

| Endpoint | Ver. | Purpose |
|---|---|---|
| `checkAddress` | 1.3 | Verify / geocode a recipient address (billable) — [request](examples/checkAddress.request.json) / [response](examples/checkAddress.response.json) |
| `getCredits` | 1.2 | Read remaining credits/balance |
| [`getQaplaStatus`](statuses.md) | 1.2 | List the canonical Qapla' status definitions (id, label, color, sub-states) |

## Channels (channel management)

| Endpoint | Ver. | Purpose |
|---|---|---|
| `getChannel` | 1.2 | Read channel config — also the simplest connectivity test |
| `createChannel` / `updateChannel` / `deleteChannel` | 1.2 | Manage channels |
| `checkChannel` | 1.2 | Validate a channel |
| `getChannelMonitor` | 1.2 | Channel monitoring data |

## Platform / marketplace integration

| Endpoint | Ver. | Purpose |
|---|---|---|
| `fetchPlatformOrders` | 1.2 | Import orders from a connected marketplace |
| `updatePlatformOrder` | 1.2 | Push status/feedback back to the marketplace |

## Virtual courier

| Endpoint | Ver. | Purpose |
|---|---|---|
| [`apiVirtual`](apivirtual.md) / virtual-courier | `/virtual/` | Merchant prints its own labels and pushes statuses to Qapla' via API (no Qapla' tracking/label generation) |

## Webhooks (pillar 2 — outbound events)

Not REST endpoints you call, but outbound callbacks Qapla' sends **to you**. See
[`webhooks.md`](webhooks.md) for the full reference.

| Event | Trigger |
|---|---|
| Shipments | Carrier status change on a tracked shipment |
| Shipments Return | A customer return is registered (*Resi automatici* add-on) |
| Orders | Shipment creation or first carrier transmission |

> Documented at <https://webhook.qapla.dev> (separate from the REST docs).

---

**Not listed = not public.** If an endpoint or field is not here and not on
<https://api.qapla.dev>, do not assume it exists.
