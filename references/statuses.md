# Status model — canonical Qapla' statuses

Every tracking event carries **two status representations at once**:

| Layer | Field | Description |
|---|---|---|
| **Raw carrier status** | `courierStatus` (and a free-text `status` inside the carrier block) | Exact text/code from the carrier — varies by courier, locale, and carrier API version. |
| **Canonical Qapla' status** | the `qaplaStatus` object / `qaplaStatusID` | Normalized, carrier-agnostic status with a **stable numeric id**, label, color, icon, and optional sub-state. |

> **The one rule that matters:** branch your logic on the **canonical integer id**,
> never on raw carrier strings. Carrier strings are unstable across couriers and
> versions; the canonical id is the stable contract.

## Canonical status table

Authoritative list as returned by `getQaplaStatus` (labels shown in Italian, the
default; pass `lang=en`/`es` for translations — the **id and color never
change**). Verified against `https://api.qapla.it/1.2/getQaplaStatus/`.

| id | Label (IT, default) | Color | Meaning |
|---|---|---|---|
| `0` | ATTESA ELABORAZIONE | `#ecf0f1` | Queued; automatic carrier polling has not run yet. |
| `1` | IN SOSPESO | `#abbad4` | Shipment found, but no carrier news yet. |
| `2` | ATTESA RITIRO | `#35495e` | Carrier has not collected the parcel yet. |
| `3` | IN TRANSITO | `#1D76D8` | Goods are moving through the carrier network. |
| `4` | IN CONSEGNA | `#376600` | Out for last-mile delivery. |
| `5` | TENTATIVO DI CONSEGNA FALLITO | `#FF6E00` | Delivery attempt failed (pre-alarm for possible issues). |
| `6` | ECCEZIONE | `#970D00` | A problem is reported — generic, or qualified by a sub-state (see below). |
| `8` | RITARDO | `#e9be57` | Shipment is delayed. |
| `10` | PUNTO DI RITIRO | `#FFDE00` | Delivered to a pickup point. |
| `20` | PARTITO | `#8A2BE2` | Shipment has departed. |
| `50` | IN LAVORAZIONE | `#BDB76B` | Shipment is being processed. |
| `95` | RIENTRATO | `#620000` | Returned to sender. |
| `99` | CONSEGNATO | `#66cc00` | Delivered to recipient. Primary trigger for review-request flows. |

> The ids are **not** contiguous and **not** ordered by lifecycle (e.g. `IN
> TRANSITO` is `3`, `IN CONSEGNA` is `4`, `PARTITO` is `20`, `IN LAVORAZIONE` is
> `50`). Do not infer an id from a status name — look it up here or via the live
> endpoint.

### Sub-states (`statusDetailID`)

Only **ECCEZIONE (`6`)** carries sub-states today:

| id | statusDetailID | Sub-state (IT) | Meaning |
|---|---|---|---|
| `6` | `1` | GIACENZA | Held in depot. |
| `6` | `2` | SPEDIZIONE IN RIENTRO / RIFIUTATA | Refused; goods being returned. |
| `6` | `3` | DANNEGGIAMENTO | Carrier reports the goods are damaged. |
| `6` | `4` | SMARRIMENTO | Carrier reports the goods are lost. |

A `statusDetailID` of `0` (or absent) means no sub-state.

## Field naming differs by context ⚠️

The **same** canonical status is exposed under **different field names** depending
on where it appears. This is the single most common integration mistake — get it
right per endpoint:

| Context | Status id field | Sub-state field | Label field |
|---|---|---|---|
| `getQaplaStatus` list | `statusID` | `statusDetailID` (+ `statusDetail`) | `status` |
| Embedded `qaplaStatus` object (`getShipment`, `getCompanyShipments`, `trackingByTimeFrame`) | `id` | `detailID` (+ `detail`) | `status` |
| Webhook payload | `qaplaStatusID` | `statusDetails[]` (array of `{id, detail}`) | `qaplaStatus` |

### `getQaplaStatus` list entry

```json
{
  "statusID": 6,
  "status": "ECCEZIONE",
  "statusDescription": null,
  "color": "#970D00",
  "icon": "https://cdn.qapla.it/status/6-1.svg",
  "statusDetailID": 1,
  "statusDetail": "GIACENZA",
  "statusDetailDescription": "La spedizione è in giacenza"
}
```

### Embedded `qaplaStatus` object (in shipment reads)

```json
{
  "qaplaStatus": {
    "id": 3,
    "status": "IN TRANSIT",
    "detailID": 0,
    "detail": null,
    "color": "#1D76D8",
    "icon": "https://cdn.qapla.it/status/3.svg"
  }
}
```

(For webhook status fields see [`webhooks.md`](./webhooks.md).)

## The `getQaplaStatus` endpoint

```
GET https://api.qapla.it/1.2/getQaplaStatus/?apiKey=YOUR_KEY&lang=en
```

| Param | Notes |
|---|---|
| `apiKey` | Channel API key (required) |
| `lang` | `it` (default), `en`, `es` — affects label text only |
| `id` | Optional: return only the entry/entries for one status id |

Run it once at integration time to obtain the live list, then **pin the numeric
ids** in your code. Do not hard-code label strings — they are translated and may
change wording.

## Multilingual labels

`lang` (`it`/`en`/`es`) is accepted on `getQaplaStatus`, `getShipment`,
`getCompanyShipments`, and `trackingByTimeFrame`. Only the `status` /
`statusDetail` label text changes; `id`, `statusDetailID`, and `color` are
language-independent. Store the numeric id for business logic; render the
localized label only for display.

## Branching pattern

```js
// Always switch on the canonical integer id, never on the label.
switch (Number(qaplaStatusId)) {        // qaplaStatus.id | statusID | qaplaStatusID
  case 99: markDelivered(s); break;     // CONSEGNATO
  case 95: flagReturned(s); break;      // RIENTRATO
  case 5:  scheduleRetry(s); break;     // TENTATIVO DI CONSEGNA FALLITO
  case 6:  handleException(s, detailId); break; // ECCEZIONE (+ sub-state)
  default: recordProgress(s);
}
```
