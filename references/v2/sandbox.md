# Sandbox (v2)

**Resource:** `https://api.qapla.it/v2/sandbox`
**Auth:** Bearer JWT (see [`authentication.md`](authentication.md)). Scopes:
`sandbox:read` / `sandbox:write`.

The sandbox resource is a **playground / reference CRUD entity**. It does not move
real shipments — it exists so you can exercise the full v2 mechanics (auth, Bearer
header, REST verbs, pagination, ETag/`304`, RFC 7807 errors, validation
`violations`) against a harmless resource before wiring up real ones. Treat it as
the canonical "hello world" for a v2 client.

> ⚠️ **Response casing depends on the deployed `qore/api` version.** Up to and
> including **2.21.9** — what is in production as of 2026-09-03 — the endpoint
> accepts camelCase but answers **snake_case**, so you cannot read back what you
> just wrote under the same names. From **2.21.10** both directions are camelCase.
> 2.21.10 is not deployed yet: write a parser that tolerates both, because the
> switch is a **breaking change** if you only handle snake_case.
>
> Note that <https://api.qapla.dev/v2/> already shows the 2.21.10 camelCase
> examples, ahead of production. **Request** bodies are camelCase in every version.

## The entity

Request fields are always camelCase. The response field name depends on the
deployed version (see the warning above).

| Response ≤2.21.9 | Response 2.21.10+ | Type | Notes |
|---|---|---|---|
| `id` | `id` | integer | Server-assigned |
| `string_value` | `stringValue` | string | min 3 chars |
| `int_value` | `intValue` | integer | |
| `bool_value` | `boolValue` | boolean | |
| `float_value` | `floatValue` | float | |
| `date_time_value` | `dateTimeValue` | string \| null | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |
| `created_at` | `createdAt` | string | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |
| `updated_at` | `updatedAt` | string \| null | `"Y-m-d H:i:s"`, no offset, `Europe/Rome` |

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
[request](../examples/v2/sandbox.request.json) (camelCase) /
[response](../examples/v2/sandbox.response.json) (snake_case, i.e. the deployed
2.21.9 shape — see the casing warning above).

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
