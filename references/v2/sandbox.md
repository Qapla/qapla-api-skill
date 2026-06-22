# Sandbox (v2)

**Resource:** `https://api.qapla.it/v2/sandbox`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)). Scopes:
`sandbox:read` / `sandbox:write`.

The sandbox resource is a **playground / reference CRUD entity**. It does not move
real shipments — it exists so you can exercise the full v2 mechanics (auth, Bearer
header, REST verbs, pagination, ETag/`304`, RFC 7807 errors, validation
`violations`) against a harmless resource before wiring up real ones. Treat it as
the canonical "hello world" for a v2 client.

> ⚠️ **Field-casing quirk:** the **request** bodies use camelCase
> (`stringValue`, `dateTimeValue`), but the **response** comes back in snake_case
> (`string_value`, `date_time_value`, `created_at`). This mirrors the
> implementation as of `qore/api` 2.9.4 — don't assume symmetry.

## The entity

| Response field | Type | Notes |
|---|---|---|
| `id` | integer | Server-assigned |
| `string_value` | string | min 3 chars |
| `int_value` | integer | |
| `bool_value` | boolean | |
| `float_value` | float | |
| `date_time_value` | string \| null | `"Y-m-d H:i:s"` |
| `created_at` | string | `"Y-m-d H:i:s"` |
| `updated_at` | string \| null | `"Y-m-d H:i:s"` |

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
→ `201 Created` with the entity (snake_case fields). Samples:
[request](../examples/v2/sandbox.request.json) (camelCase) /
[response](../examples/v2/sandbox.response.json) (snake_case).

## List — `GET /v2/sandbox`

| Query param | Default | Meaning |
|---|---|---|
| `page` | 1 | positive |
| `limit` | 20 | positive, max 100 |
| `updatedAfter` | — | ISO 8601 datetime filter |
| `updatedBefore` | — | ISO 8601 datetime filter |

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
