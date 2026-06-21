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

> ⚠️ The field is **`apiKey`** (camelCase). The public Swagger may still show
> `api_key` (snake_case) — that is stale; the deployed API renamed it to `apiKey`
> in v2.8.8 ("consistent with all other endpoints"). Use `apiKey`.

### Response

```json
{
  "token": "<JWT>",
  "scopes": ["parcels:create", "parcels:read", "..."],
  "token_type": "Bearer",
  "expires_in": 86400,
  "rate_limit": { "refill_rate": 2, "bucket_size": 120 },
  "cache": false
}
```

| Field | Meaning |
|---|---|
| `token` | The JWT to send on every subsequent call |
| `scopes` | The permissions embedded in this token (what the key is allowed to do) |
| `token_type` | Always `Bearer` |
| `expires_in` | Token lifetime in **seconds** — `86400` = 24h |
| `rate_limit` | This channel's bucket: `refill_rate` (tokens/sec) and `bucket_size` (capacity) |
| `cache` | `true` if the token came from Qapla's cache, `false` if freshly minted (also surfaced as the `X-Auth-Cache: HIT\|MISS` header) |

## 2. Use the token

Send it as a Bearer header on every other v2 call:

```
GET https://api.qapla.it/v2/parcels?orderReference=ABC&orderOrigin=shopify
Authorization: Bearer <JWT>
```

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
| `400` | Malformed request (e.g. missing/!`apiKey`) |
| `401` | Invalid/expired token, or unknown API key |
| `403` | Authenticated but missing the required **scope** (or product) |

## Security

Same rules as v1.x: the API key is a secret that mints tokens — never commit it,
never ship it client-side, read it from env/config, rotate from the Control Panel
if leaked. Treat the issued JWT as a bearer credential too: it grants the channel's
access until it expires.

> v1.x by contrast sends `apiKey` in the body/query on every call with no token
> step — see [`../authentication.md`](../authentication.md).
