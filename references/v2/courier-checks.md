# Courier pre-checks (v2)

**What it answers:** *would the courier refuse this address at label creation?*
A field too long for the courier, a missing name/street/city, a province written
in full instead of its two-letter code, a malformed or non-existent Italian
postcode, a postcode + city pair the courier has never delivered to, or a postcode
in a zone where the courier has suspended deliveries.

It is a **warning only**: nothing is saved, nothing is blocked, and creating the
order or the label works exactly as before. Use it to fix the address *before*
the label fails.

It comes in two forms with the same outcome shape:

| Form | When | Courier checked |
|---|---|---|
| `courierChecks` field on every order response | You already pushed the order | The order's **preassigned** courier only |
| `POST /v2/orders/courier-checks` | The address is not an order yet (checkout, import preview, bulk clean-up) | The `courierId` you send, or **every active courier** of the channel |

> v2 surface as of `qore/api` **2.39.0** (2026-10-23; `ZONE_SUSPENDED` since
> 2.33.0, the field on orders since 2.32.0). Live docs:
> <https://api.qapla.dev/v2/#ordersPOSTcourierChecks>.

## The outcome — `{courierId, status, checks}`

```json
{
  "courierId": 4,
  "status": "WARNING",
  "checks": [
    { "code": "FIELD_TOO_LONG", "field": "consignee.street", "max": 35, "length": 41 },
    { "code": "PROVINCE_NOT_CODE", "field": "consignee.state", "suggestion": "RM" },
    { "code": "LOCALITY_NOT_DELIVERED", "field": "consignee.city",
      "suggestions": [ { "postcode": "00046", "city": "GROTTAFERRATA", "state": "RM" } ] }
  ]
}
```

| Key | Meaning |
|---|---|
| `courierId` | The **canonical** courier. A merchant with two contracts for the same carrier (a contract *variant*) always sees the parent id here |
| `status` | `OK` (no checks) or `WARNING` (at least one) |
| `checks[].code` | One of the codes below |
| `checks[].field` | Path of the field **in the v2 order payload**: `consignee.name`, `consignee.street`, `consignee.city`, `consignee.state`, `consignee.postcode`, `consignee.phone`, `consignee.email`, `notes` |

| Code | Extra keys | When |
|---|---|---|
| `FIELD_TOO_LONG` | `max`, `length` | The field exceeds the courier's limit. Not raised where the channel lets the courier truncate the field itself |
| `FIELD_REQUIRED` | — | A field the courier requires is empty |
| `PROVINCE_NOT_CODE` | `suggestion` (code or `null`) | `state` is not a two-letter code (e.g. `"Roma"`); `suggestion` is the code when it can be told |
| `POSTAL_CODE_INVALID` | — | The postcode is not 5 digits |
| `POSTAL_CODE_UNKNOWN` | — | 5 digits, but not an Italian postcode (and no courier ever delivered there) |
| `LOCALITY_NOT_DELIVERED` | `suggestions` (≤5 `{postcode, city, state}`) | The courier has never delivered to that postcode + city + province |
| `ZONE_SUSPENDED` | `until` (`YYYY-MM-DD` or `null`) | The courier has suspended deliveries to the area the postcode falls in; `null` = no end announced |

Scope of the rules: length and required-field limits apply to every address
(each courier has its own, some domestic-only). The postcode, province, locality
and suspended-zone checks run only for **Italy, San Marino and Vatican City**
(`country` `IT`/`SM`/`VA`); `POSTAL_CODE_UNKNOWN` only for `IT`.

**Do not hardcode the code list as closed**: new codes have been added in minor
releases (`ZONE_SUSPENDED`). Treat an unknown `code` as a generic warning on
`field`.

## On order responses — `courierChecks`

Every order payload (`GET /v2/orders`, `GET /v2/orders/{id}`, and the responses
of `POST /v2/orders`, `PUT`/`PATCH /v2/orders/{id}`, version `1.1`) carries
`courierChecks`: one outcome object as above for the preassigned `courierId`, or
**`null`** when the order has no courier (`courierId: 0`) or the courier is
unknown. No extra call, no extra scope.

## Check addresses without an order — `POST /v2/orders/courier-checks`

**Auth:** Bearer JWT, scope **`orders:read`** (nothing is written). Version
`1.0`. One request costs one rate-limit token, whatever the number of items.

```json
{
  "items": [
    {
      "courierId": 4,
      "consignee": { "name": "Barbara Gordon", "street": "Via Manin, 8",
                     "city": "Vigonza", "state": "Padova", "postcode": "35010", "country": "IT" }
    },
    {
      "consignee": { "name": "Barbara Gordon", "street": "Via Manin, 8",
                     "city": "Vigonza", "state": "PD", "postcode": "35010", "country": "IT" },
      "notes": "Ring twice"
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `items` | yes | **1 to 100** addresses |
| `items[].consignee` | yes | Same object as the order's `consignee` (`name`, `street`, `city`, `state`, `postcode`, `country`, `email`, `phone`), every key optional — a missing one is itself what `FIELD_REQUIRED` reports |
| `items[].notes` | no | Checked against the courier's limit on notes, as on the order |
| `items[].courierId` | no | Check against this courier (a contract variant uses its own channel settings and answers as its canonical courier). **Omitted: every active courier of the channel**, i.e. those it creates labels with |

**Response `200`** — an array with **one element per item, in the same order**;
each element is a **list** of outcomes, one per canonical courier (two contracts
with the same carrier give one outcome). An item without `courierId` on a channel
with no active courier gets `[]`.

```json
[
  [ { "courierId": 4, "status": "WARNING",
      "checks": [ { "code": "PROVINCE_NOT_CODE", "field": "consignee.state", "suggestion": "PD" } ] } ],
  [ { "courierId": 4, "status": "OK", "checks": [] },
    { "courierId": 24, "status": "OK", "checks": [] } ]
]
```

Note the shape difference: on an order `courierChecks` is **one object or
`null`**; here each item gets a **list** (possibly empty). Pair results to inputs
by **position**.

| Status | When |
|---|---|
| `401` | Missing/invalid token |
| `403` | Token without `orders:read` |
| `422` | `items` missing, empty or over 100; an item without `consignee`; `courierId` ≤ 0; invalid `email`; `country` longer than 2 chars; **a `courierId` that does not exist** (`detail: "Unknown courier N."`) |
| `429` | Rate limit (see [`overview.md`](overview.md)) |

Example payloads: [`../examples/v2/courierChecks.request.json`](../examples/v2/courierChecks.request.json),
[`../examples/v2/courierChecks.response.json`](../examples/v2/courierChecks.response.json).
Client: `QaplaV2Client.check_addresses(items)` in `scripts/qapla_v2_client.py`.
