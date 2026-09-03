# Sandbox (v2)

**Resource:** `https://api.qapla.it/v2/sandbox`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)). Scopes:
`sandbox:read` / `sandbox:write`.

The sandbox resource is a **playground / reference CRUD entity**. It does not move
real shipments — it exists so you can exercise the full v2 mechanics (auth, Bearer
header, REST verbs, pagination, ETag/`304`, RFC 7807 errors, validation
`violations`) against a harmless resource before wiring up real ones. Treat it as
the canonical "hello world" for a v2 client.

> **Casing is symmetric since `qore/api` 2.21.10** (released 2026-09-03): request
> and response are both camelCase. ⚠️ Up to 2.21.9 the endpoint accepted
> `stringValue` but answered `string_value`, so you could not read back what you
> had just written under the same names. **If you integrated against that
> snake_case response, the upgrade is a breaking change** — rename the fields
> (`string_value` → `stringValue`, `created_at` → `createdAt`, and so on for all
> of them).

## The entity

Request and response use the same camelCase names.

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Server-assigned |
| `stringValue` | string | min 3 chars |
| `intValue` | integer | |
| `boolValue` | boolean | |
| `floatValue` | float | |
| `dateTimeValue` | string \| null | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |
| `createdAt` | string | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |
| `updatedAt` | string \| null | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |

## Create — `POST /v2/sandbox`

```json
{
  "stringValue": "hello",
  "intValue": 42,
  "boolValue": true,
  "floatValue": 3.14,
  "dateTimeValue": "2026-06-21 10:00:00"
}
```

All required except `dateTimeValue` (optional). `stringValue` needs ≥3 chars.
→ `201 Created` with the entity. Samples:
[request](../examples/v2/sandbox.request.json) /
[response](../examples/v2/sandbox.response.json) — both camelCase.

## List — `GET /v2/sandbox`

| Query param | Default | Meaning |
|---|---|---|
| `page` | 1 | positive |
| `limit` | 20 | positive, max 100 |
| `updatedAfter` | — | ISO 8601 datetime filter — ⚠️ **read in `Europe/Rome`**, see below |
| `updatedBefore` | — | ISO 8601 datetime filter — same zone |

⚠️ **Both filters are interpreted in `Europe/Rome`, not UTC.** Passing a UTC
cursor does not raise an error, it just **silently omits** rows in the offset
window (1–2h depending on DST). Convert your cursor to `Europe/Rome` before
sending it, or overlap the window and de-duplicate. The same applies to the
`updatedAfter` filter on the `shipments` resource.

Returns the paginated envelope (`items`/`total`/`page`/`limit`/`pages`); supports
ETag / `304`.

## Get one — `GET /v2/sandbox/{id}`

`{id}` is a positive integer. → `200` (or `304`), `404` if not found.

## Replace — `PUT /v2/sandbox/{id}`

Full replace: send the **complete** body (same shape as create, all fields
required). → `200`, `404` if not found.

## Partial update — `PATCH /v2/sandbox/{id}`

Send only the fields to change (all optional, same names/constraints as create):

```json
{ "intValue": 99 }
```

→ `200`, `404` if not found.

## Delete — `DELETE /v2/sandbox/{id}`

→ `204 No Content`, `404` if not found.

## Notes

- Use this to validate your client end-to-end (token exchange → Bearer call →
  parse RFC 7807 errors → handle `304`) before touching `parcels` or other real
  resources.
- Live reference: <https://api.qapla.dev/v2/>.
