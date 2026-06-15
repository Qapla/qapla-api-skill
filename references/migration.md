# Migrating between API versions

The production version is **`1.3`**. This page helps integrations on an older
version move forward, and explains how `v2` relates to `1.3`.

> Official docs: <https://api.qapla.dev>. Diff your actual calls against the
> current endpoint pages — this guide is a checklist, not a field-by-field map.

## Version landscape

| Version | Status | Notes |
|---|---|---|
| `1.3` | **Current** | Default for most endpoints |
| `1.2` | **Current** | Not retired — several endpoints are published **only** under `1.2` (e.g. `getPudos`, `trackingByTimeFrame`, `detectOrderCourier`, the platform-order endpoints). No `1.3` alias for those |
| `1.1` | Deprecated | Still served; migrate away |
| `1.0` | Deprecated | Still served; migrate away |
| `v2` | Opt-in (parallel) | New architecture, different auth — coexists with `1.3`; not a forced upgrade |

## `1.0` / `1.1` → `1.2` / `1.3`

1. Swap the version segment in the URL (`https://api.qapla.it/<version>/...`).
   Keep `1.2` for endpoints that have no `1.3` alias (see table above).
2. Re-check each payload against the current endpoint page — field names and
   shapes may differ from your old version.
3. Confirm you read the **two-level response envelope** (`conventions.md`): a
   call can be `OK` while individual batch items are `KO`.
4. Re-test against the `"sandbox": true` flow before going live.

## `1.x` → `v2` (optional)

`v2` is a separate, opt-in architecture. Migrate only if you need its features —
`1.3` is not being retired soon. Key differences:

| Aspect | `1.x` | `v2` |
|---|---|---|
| Auth | Per-channel API Key | **JWT Bearer** + granular scopes |
| Bulk ops | Synchronous | **Async** (`jobId` + poll) |
| Parcels | Embedded in the payload | First-class entity |
| Sandbox | `"sandbox": true` flag | Dedicated sandbox tenant |

## Which version should I target?

- On `1.0` / `1.1` → move to `1.3` (use `1.2` for the endpoints that only exist
  there).
- On `1.2` / `1.3` → you're current; adopt `v2` only if you need its features.
