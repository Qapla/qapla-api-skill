# Conventions — apply to every call

These rules are shared by all v1.3 endpoints. Read once.

## Base URL & versioning

```
https://api.qapla.it/<version>/<endpoint>
```

- `<version>`: `1.3` for production. `1.1`/`1.2` are deprecated but still served.
  A few endpoints are only published under an older version — notably
  **`getPudos` lives at `/1.2/getPudos`** (no `1.3` alias).
- `<endpoint>`: the endpoint name, e.g. `pushShipment`, `createLabel`.

> Note: the documentation site is `api.qapla.dev`; the API host you actually
> call is `api.qapla.it`.

## Request shape

- `Content-Type: application/json`.
- The **API Key goes in the JSON body** as `apiKey` (see `authentication.md`).
- Write endpoints are POST. Batch endpoints (`pushShipment`, `pushOrder`) take
  an **array** under the endpoint-named key.

## Response envelope

Every response is wrapped in a key equal to the endpoint name:

```json
{ "<endpointName>": { "result": "OK", "error": null } }
```

| Field | Meaning |
|---|---|
| `result` | `"OK"` on success, `"KO"` on error |
| `error`  | `null` when `OK`; the error message when `KO` |

**Batch endpoints** add a second layer: a top-level `result`/`error` for the
call, plus a per-item `result`/`error` inside the returned array. A call can be
`OK` overall while some items are `KO`. Always inspect both levels. Example
(`pushShipment`):

```json
{
  "pushShipment": {
    "result": "OK", "error": null, "count": 2, "imported": 1,
    "shipments": [
      { "result": "OK", "error": null, "trackingNumber": "123987299" },
      { "result": "KO", "error": "Invalid courier", "courier": "OPPS" }
    ]
  }
}
```

## Rate limiting (token bucket)

| Parameter | Value |
|---|---|
| Bucket capacity | 120 |
| Refill rate | 2 tokens/second |
| Cost | 1 token per item — a batch of 100 items costs **100 tokens** |

Over the limit → HTTP `429 Too Many Requests`, and the JSON `error` is
`"Too Many Requests"`. Back off and retry. **Abuse leads to an API Key ban.**

Practical guidance:
- Prefer batching, but cap batches (≈100 items) and pace them: at 2 tokens/sec
  a 120-item burst then needs ~60s to refill.
- Implement exponential backoff on `429`.

## Dates & time zone

- Reference time zone: **CEST** (UTC+2 during DST, UTC+1 in winter).
- Date format: `YYYY-MM-DD`. Datetime format: `YYYY-MM-DD HH:MM:SS`.

## Sandbox

There is **no separate sandbox environment**. Endpoints that support testing
accept a `"sandbox": true` flag (e.g. `createLabel`, `getQuotes`) so you can
exercise the flow without real effects — no carrier pickup request, no billing.

## Error handling checklist (for client code)

1. HTTP status: handle `429` (rate limit) and 5xx (retry with backoff).
2. Top-level `result`: bail if `"KO"`, surface `error`.
3. Per-item `result` (batch endpoints): collect failed items and their `error`.
4. Never assume success from HTTP `200` alone — always read the envelope.
