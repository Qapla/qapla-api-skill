# Qapla' Public API (v1.3) — overview

> **Canonical orientation.** This file is the single source of truth for the
> high-level facts about the Qapla' API. Every agent entrypoint (`SKILL.md`,
> `AGENTS.md`, `.cursor/rules/qapla-api.mdc`) points here instead of repeating
> the content, so a fix lands in one place.

Qapla' is a SaaS platform for e-commerce logistics: multi-carrier shipping,
real-time tracking, label printing (PDF/ZPL), transactional notifications, and
analytics. This document orients you to its **public REST API**.

> **Official docs (always the source of truth):** <https://api.qapla.dev/1.3/>
> The pages are bilingual (IT default, `/1.3/en/` for English). This repo
> mirrors the public docs so you can work offline, but when a parameter is
> ambiguous or you suspect drift, defer to the live docs.

## Core facts — read these first

| Topic | Value |
|---|---|
| **Base URL** | `https://api.qapla.it/<version>/<endpoint>` (e.g. `https://api.qapla.it/1.3/pushShipment`) |
| **Protocol** | REST over HTTPS; JSON in, JSON out. Methods: GET/POST/PUT/DELETE/PATCH (most write endpoints use POST) |
| **Auth** | Per-**channel** API Key, sent as `apiKey` in the JSON body (see `authentication.md`) |
| **Response envelope** | `{"<endpointName>": {"result": "OK"\|"KO", "error": null\|"<message>"}}` |
| **Rate limit** | Token bucket: 120 capacity, refill 2 tokens/sec. A batch of N items costs N tokens. Over limit → HTTP `429 Too Many Requests` |
| **Time zone** | CEST (UTC+2 DST / UTC+1 winter). Dates are `YYYY-MM-DD`, datetimes `YYYY-MM-DD HH:MM:SS` |
| **Sandbox** | No separate environment. Pass `"sandbox": true` in the body on endpoints that support it (e.g. `createLabel`) to test without real effects (no carrier pickup, no billing). **`getQuotes` is the exception**: it uses an `x-sandbox` header (see its reference) |
| **Versions** | `1.3` is the current version; use it where the endpoint exists. `1.1`/`1.2` are deprecated but still active — and **many endpoints are still 1.2-only** (not yet migrated), so calling them under `/1.2/` is expected. `1.4` exists for `createLabel` only (`parcelsTracking`). A separate **v2** (Bearer/JWT, UTC, HTTP-status errors) is a distinct RESTful generation, evolving toward becoming the primary surface — its stable core is documented under `v2/` (start at `v2/overview.md`). See `versioning.md` |

## Domain model in one minute

Qapla' has three orthogonal "pillars"; a merchant may use only some:

1. **Tracking** — shipments that already have a tracking number live in `ordini`
   (the central shipments table). Push them with **`pushShipment`**.
2. **Transactional events** — on each tracking status change, Qapla' fires
   notifications (email/SMS/webhook) to merchant and recipient. To react in your
   own code, register an outbound **webhook** (see `webhooks.md`).
3. **Labels** — import raw orders (**`pushOrder`**), generate a carrier label
   (**`createLabel`**), then confirm/transmit it (**`confirmLabel`**). On
   transmission the shipment automatically enters pillars 1 & 2.

Key vocabulary:
- **channel** — a merchant's store/marketplace; owns its own `apiKey`. All API
  calls are scoped to one channel.
- **raw order** — an imported order, not yet a label (`pushOrder`).
- **label** — a generated carrier label (`createLabel`).
- **shipment** — a confirmed label or a pushed tracking number, now in active
  tracking (`pushShipment` / result of label transmission).
- **courier** — the carrier (GLS, BRT, DHL, UPS…). Identified by a string code
  in the API.

**Decision rule — which endpoint do I need?**
- Have a tracking number already, just want tracking + notifications → `pushShipment`
- Want Qapla' to produce the label → `pushOrder` → `createLabel` → `confirmLabel`
- Want to know shipping options/prices before shipping → `getQuotes`
- Need a pickup point → `getPudos`

## Where to go next

1. Read `conventions.md` and `authentication.md` once — they apply to **every**
   call (envelope, errors, rate limiting, the `apiKey`).
2. Pick the endpoint from `endpoints.md` (full catalog) or the per-endpoint
   deep-dives:
   - `pushshipment.md`
   - `pushorder.md`
   - `createlabel.md`
   - `getquotes.md`
   - `getpudos.md`
   - `trackingbytimeframe.md` (poll status changes — pull alternative to webhooks)
   - `apivirtual.md` (virtual courier — push your own status updates)
   - `webhooks.md` (Pillar 2 — receive outbound event callbacks)
   - `statuses.md` (how to read tracking statuses — branch on the canonical id)
   - `versioning.md` (which version to call; v1.2-only endpoints; v2 overview)
   - `migration.md` (upgrading a legacy integration; v1.x → v2)
   - `v2/overview.md` (the **v2** generation — JWT auth, REST, async jobs; its
     stable core: `v2/authentication.md`, `v2/parcels.md`, `v2/sandbox.md`,
     `v2/endpoints.md`)
3. Use the runnable example payloads in `examples/` as a starting point — they
   are the real request/response samples from the official docs.

## When writing client code

- Always send `apiKey`. Never hard-code it — read it from config/env. Treat it
  as a secret; it grants full access to a channel.
- Always check `result == "OK"` **and**, for batch endpoints, the per-item
  `result` inside the array (a call can be `OK` overall while individual items
  are `KO`).
- Handle `429`: back off and retry. Remember a batch of N costs N tokens, so
  large `pushShipment`/`pushOrder` batches drain the bucket fast.
- Batch where the endpoint allows it (`pushShipment`, `pushOrder` accept arrays)
  instead of one HTTP call per item — but mind the 100-item practical cap and
  the token cost.
- Use `"sandbox": true` while developing on label/quote endpoints.

A ready-made, dependency-free Python client is bundled: see
`../scripts/qapla_client.py`. It injects `apiKey`, parses the two-level envelope
(`split_batch()`), and retries `429` with backoff — read it as a reference when
writing client code, or run it (`QAPLA_API_KEY=… python3 scripts/qapla_client.py`)
for a connectivity smoke test against `getChannel`.

## Guardrails

- This documents the **public** API only. Do not invent endpoints, parameters,
  or fields. If something isn't here or on <https://api.qapla.dev>, say so
  rather than guessing.
- Carrier-specific required fields (customs blocks, PUDO, service codes) vary a
  lot — see the per-endpoint references and the live docs before assuming.
