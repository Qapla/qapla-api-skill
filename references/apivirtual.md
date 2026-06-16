# apiVirtual — virtual courier

**Endpoint:** `POST https://api.qapla.it/virtual/` (note: **not** a versioned
path). **Batch:** array, up to **100** updates per call.

The *virtual courier* is for merchants who ship with their own/offline logistics
(no real carrier tracking). You print your own labels and **push status updates
to Qapla' yourself**, so the shipment still gets a Qapla' tracking page and fires
transactional events — without Qapla' polling a carrier.

> Get the shipment into Qapla' first with `pushShipment` (using your own
> tracking number and the virtual courier), then drive its status with this
> endpoint. To branch/choose `statusID` values, see `statuses.md`.

## Request

```json
{
  "apiKey": "YOUR_KEY",
  "virtual": [
    {
      "trackingNumber": "xxxxxxxxxxxxxx",
      "statusID": 20,
      "statusDetailID": 0,
      "status": "Processato",
      "place": "Modena (MO)",
      "date": "2026-06-16 14:22:00",
      "note": "Out for delivery tomorrow morning"
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `apiKey` | yes | Channel API key (root level) |
| `trackingNumber` | yes | The tracking number of the shipment to update |
| `statusID` (+ `statusDetailID`) | yes | The canonical Qapla' status id (and optional sub-state) to set — see `statuses.md` |
| `status` | no | Free-text label for the status |
| `place` | no | Current location |
| `date` | no | Event timestamp, `YYYY-MM-DD HH:MM:SS` |
| `note` | no | Free note |

The `virtual` array may contain at most 100 updates per request.

## Response

Standard envelope (`{"virtual": {"result": …}}`) with per-item results — loop and
check each. For exact response fields and any courier nuances, confirm against the
live docs.
