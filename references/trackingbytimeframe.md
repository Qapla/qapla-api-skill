# trackingByTimeFrame

**Endpoint:** `GET https://api.qapla.it/1.2/trackingByTimeFrame/`
**Pillar:** 1/2 (tracking — the **pull** alternative to webhooks). **Served under 1.2.**

Return every shipment whose tracking status changed within a time window. This is
the polling counterpart to outbound webhooks (`webhooks.md`): use it when you
prefer to query on your own schedule instead of receiving push callbacks.

## Request

Query parameters (it's a GET — `apiKey` goes in the query string):

| Param | Required | Meaning |
|---|---|---|
| `apiKey` | yes | Channel API key |
| `dateFrom` | no | Window start, `YYYY-MM-DD HH:MM:SS`. Default: **one hour ago** |
| `dateTo` | no | Window end, `YYYY-MM-DD HH:MM:SS` |
| `lang` | no | Status label language: `it` (default), `en`, `es` |

```
GET https://api.qapla.it/1.2/trackingByTimeFrame/?apiKey=YOUR_KEY&dateFrom=2026-06-16%2008:00:00&dateTo=2026-06-16%2009:00:00&lang=en
```

## Response

Standard envelope plus `count` and a `shipments[]` array. Each shipment carries a
`status` block whose canonical status is the embedded **`qaplaStatus` object**
(`id`/`detailID`/…) — branch on `qaplaStatus.id`, never on the raw label (see
`statuses.md`):

```json
{
  "trackingByTimeFrame": {
    "result": "OK", "error": null, "count": 1,
    "dateFrom": "2026-06-16 08:00:00", "dateTo": "2026-06-16 09:00:00", "lang": "en",
    "shipments": [
      {
        "id": "000000000001",
        "reference": "0101000101002-A",
        "trackingNumber": "XX000001",
        "courier": "GLS-ITA",
        "status": {
          "dateISO": "2026-06-16 08:07:00",
          "place": "LUCCA",
          "qaplaStatus": { "id": 99, "status": "DELIVERED", "detailID": 0, "detail": null, "color": "#66CC00", "icon": "https://cdn.qapla.it/status/99.svg" }
        },
        "getShipment": "https://api.qapla.it/1.2/getShipment/?apiKey=[API_KEY]&id=000000000001"
      }
    ]
  }
}
```

## Notes

- **Polling cadence:** query slightly overlapping windows (e.g. every 5 min for
  the last ~6 min) and dedupe on `id` + `qaplaStatus.id` + status date to avoid
  missing or double-processing events at window edges.
- **Rate limit:** the standard token bucket applies (see `conventions.md`).
- **Push vs pull:** for near-real-time, low-overhead delivery prefer webhooks
  (`webhooks.md`); use this endpoint for batch/poll-based flows or as a backstop.
