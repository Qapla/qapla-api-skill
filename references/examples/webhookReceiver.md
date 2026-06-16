# Example — webhook receiver

Minimal receivers for Qapla' webhooks (Pillar 2). Each one does the four things
that matter: **verify `apiKey`, respond fast with the contract body, offload work
to a queue, branch on `qaplaStatusID`.** See [`../webhooks.md`](../webhooks.md)
for the full payload and contract, and [`../statuses.md`](../statuses.md) for the
status ids.

## Node.js (Express)

```js
import express from "express";

const app = express();
app.use(express.json());

const CHANNEL_API_KEY = process.env.QAPLA_CHANNEL_KEY; // never hard-code

app.post("/qapla/webhook", (req, res) => {
  const body = req.body || {};

  // 1. Authenticate. The key is in the payload (also nested for returns).
  const incomingKey = body.apiKey ?? body.webhookReturnShipments?.apiKey;
  if (incomingKey !== CHANNEL_API_KEY) {
    return res.json({ result: "KO" }); // HTTP 200, body signals rejection
  }

  // 2. Acknowledge immediately; do the work asynchronously.
  res.json({ result: "OK" });

  // 3. Enqueue — do NOT block the response on DB/email/API calls.
  enqueue(body).catch((err) => console.error("enqueue failed", err));
});

async function enqueue(body) {
  if (body.webhookReturnShipments) {
    // return event
    for (const r of body.webhookReturnShipments.returnShipments) {
      await handleReturn(r);
    }
    return;
  }
  if (Array.isArray(body.orders)) {
    for (const o of body.orders) await handleOrder(o);
    return;
  }
  // shipment status event — branch on the canonical integer id, never the label
  // (ids per statuses.md: do NOT invent values like 60/70 — they don't exist)
  switch (Number(body.qaplaStatusID)) {
    case 99: await markDelivered(body); break;       // CONSEGNATO
    case 95: await flagReturned(body); break;        // RIENTRATO
    case 5:  await scheduleRetry(body); break;       // TENTATIVO DI CONSEGNA FALLITO
    case 6:  await raiseException(body); break;      // ECCEZIONE (+ statusDetails sub-state)
    default: await recordTransit(body);
  }
}

app.listen(3000);
```

## PHP

```php
<?php
const CHANNEL_API_KEY = 'YOUR_CHANNEL_PRIVATE_KEY'; // load from env/secret store

header('Content-Type: application/json');

$payload = json_decode(file_get_contents('php://input'), true);
$incomingKey = $payload['apiKey']
    ?? ($payload['webhookReturnShipments']['apiKey'] ?? null);

if (!$payload || $incomingKey !== CHANNEL_API_KEY) {
    http_response_code(200); // still 200; the body carries the verdict
    exit('{"result":"KO"}');
}

// Acknowledge first, then process out-of-band (queue/cron). Keep this fast.
echo '{"result":"OK"}';

// e.g. push $payload onto a job queue here.
```

## Idempotency

The same event can be delivered more than once. Dedup on
`trackingNumber` + `qaplaStatusID` + `date` (for status events) before applying
any side effect.
