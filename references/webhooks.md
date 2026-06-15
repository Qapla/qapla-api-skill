# Webhooks (outbound)

Qapla' can **push** events to your server as they happen, instead of you polling
`trackingByTimeFrame`. A webhook is an HTTP `POST` Qapla' sends to a URL you
configure per channel.

> Official docs: <https://webhook.qapla.dev>. This page mirrors them; if anything
> drifts, trust the live docs.

## Event types

| Event | Fires when |
|---|---|
| **Shipment** | A shipment's tracking status changes (e.g. *in transit* → *delivered*) |
| **Shipment return** | A return is requested/updated (may require a separate service) |
| **Order** | A shipment is created / transmitted to the carrier |

## Configuration

Endpoints are configured **per channel** in the Control Panel
(*Settings → Channels → [channel] → Configure*). You can optionally enable the
richer payload (product / parcel / recipient detail).

## Payload

JSON `POST` body. Representative shipment-status event:

```json
{
  "apiKey": "CHANNEL_API_KEY",
  "trackingNumber": "2253647804",
  "courier": "GLS-ITA",
  "reference": "ORD-1042",
  "qaplaStatusID": "30",
  "courierStatus": "IN TRANSIT"
}
```

- `apiKey` identifies the sending channel — use it to authenticate the call.
- Branch on **`qaplaStatusID`** (the canonical Qapla' status), not on raw courier
  text. See the status list via `getQaplaStatus`.

## Response contract (required)

Your endpoint **must** answer with exactly:

```json
{ "result": "OK" }
```

on success, or `{ "result": "KO" }` on failure. Any other body — or a malformed
reply — is treated as a failure.

## Retries & auto-disable

- A failed delivery (`KO` or malformed) is retried **twice** in the following
  hours.
- After **100 consecutive failures** the webhook is **automatically deactivated** —
  monitor your endpoint's health.

## Receiver checklist

1. Serve over **HTTPS**.
2. Validate the payload `apiKey` against your channel key before trusting it.
3. **Acknowledge fast**: return the `{"result":"OK"}` body within a couple of
   seconds; do heavy processing asynchronously.
4. Be idempotent — the same event may arrive more than once (retries).

## Push vs pull

Webhooks (push) give near-real-time updates but need a stable public endpoint.
If you can't expose one, poll **`trackingByTimeFrame`** (`/1.2/`) instead — see
`endpoints.md`.
