# Authentication (v2)

v2 does **not** accept the channel API key on every call the way v1.x does.
Instead you **exchange** the key once for a short-lived **Bearer JWT**, then send
that token on subsequent requests.

The credential is the *same* per-channel private API key from the Control Panel
(<https://cp.qapla.it> → Settings → Channels → Configure → Private API Key) — only
the flow changes.

## 1. Get a token

```
POST https://api.qapla.it/v2/auth/token
Content-Type: application/json

{ "apiKey": "YOUR_CHANNEL_PRIVATE_API_KEY" }
```

> The field is **`apiKey`** (camelCase), renamed from `api_key` in v2.8.8
> ("consistent with all other endpoints"). The public docs showed the stale
> `api_key` until 2026-09-03 and are now corrected. A wrong field name gives
> **`422`** (`apiKey should not be blank`), not `400`: with
> `#[MapRequestPayload]`, `400` means a missing or malformed body.

### Response

```json
{
  "token": "<JWT>",
  "scopes": ["parcels:create", "parcels:read", "..."],
  "token_type": "Bearer",
  "expires_in": 86400,
  "rate_limit": { "refill_rate": 150, "bucket_size": 300 },
  "cache": false
}
```

| Field | Meaning |
|---|---|
| `token` | The JWT to send on every subsequent call |
| `scopes` | The permissions embedded in this token (what the key is allowed to do) |
| `token_type` | Always `Bearer` |
| `expires_in` | Token lifetime in **seconds** — `86400` = 24h |
| `rate_limit` | This channel's bucket: `refill_rate` (tokens restored per **minute**) and `bucket_size` (burst capacity). Defaults are 150 / 300 since `qore/api` v2.20.0; a channel can be given custom values |
| `cache` | `true` if the token came from Qapla's cache, `false` if freshly minted (also surfaced as the `X-Auth-Cache: HIT\|MISS` header) |

Sample payloads: [`../examples/v2/authToken.request.json`](../examples/v2/authToken.request.json)
and [`../examples/v2/authToken.response.json`](../examples/v2/authToken.response.json).

## 2. Use the token

Send it as a Bearer header on every other v2 call:

```
GET https://api.qapla.it/v2/parcels?orderReference=ABC&orderOrigin=shopify
Authorization: Bearer <JWT>
```

> A ready-made, dependency-free Python client for v2 is bundled:
> [`../../scripts/qapla_v2_client.py`](../../scripts/qapla_v2_client.py). It does
> the token exchange, caches/refreshes the JWT, sends the Bearer header, parses
> RFC 7807 errors, retries `429`, and polls async jobs. Run it as a connectivity
> test: `QAPLA_API_KEY=… python3 scripts/qapla_v2_client.py` (exchanges a token and
> prints the granted scopes).

## Token lifetime & caching

- A token is valid for **24 hours** (`expires_in: 86400`).
- Qapla' caches issued tokens server-side (~23h), so repeated `auth/token` calls
  with the same key return the same token cheaply — you do **not** need to fetch a
  new one per request. Cache the token client-side and refresh on expiry (or on a
  `401`).

## Scopes (this is enforced)

Unlike v1.x, v2 enforces **granular scopes** per endpoint (via a `RequiresScope`
check). The scopes you have are listed in the token response and baked into the
JWT. Calling an endpoint you lack the scope for returns **`403 Forbidden`**.

Examples seen in the implementation: `parcels:create`, `parcels:read`,
`parcels:update`, `parcels:delete`, `orders:read`, `sandbox:read`,
`sandbox:write`, `jobs:read`. The exact scope a given endpoint needs is on the live
Swagger; treat the token's `scopes` array as the authoritative list of what you can
do.

## Errors

Auth/authorization failures use the standard v2 RFC 7807 error body (see
[`overview.md`](overview.md)):

| Status | When |
|---|---|
| `400` | Body absent or malformed JSON — **not** a bad field name |
| `401` | Invalid/expired token, or unknown API key |
| `403` | Authenticated but missing the required **scope** (or product) |
| `422` | Validation failed, e.g. a wrong or missing `apiKey` field (`apiKey should not be blank`) |
| `429` | Rate limit exceeded — the token endpoint is throttled like any other |

`422` and `429` were missing from the public Swagger for `POST /v2/auth/token`,
which listed only `400`/`401`; corrected in `qore/api` 2.21.10.

## Security

Same rules as v1.x: the API key is a secret that mints tokens — never commit it,
never ship it client-side, read it from env/config, rotate from the Control Panel
if leaked. Treat the issued JWT as a bearer credential too: it grants the channel's
access until it expires.

> v1.x by contrast sends `apiKey` in the body/query on every call with no token
> step — see [`../authentication.md`](../authentication.md).
