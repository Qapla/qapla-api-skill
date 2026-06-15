---
name: qapla-api
description: >-
  Integrate with or answer questions about the Qapla' shipping & tracking REST
  API (public v1.3). Use this when working with Qapla' to push shipments or raw
  orders, generate and confirm carrier labels, track parcels, get real-time
  multi-carrier quotes, look up pickup points (PUDO), verify addresses, or list
  couriers and channels. Covers authentication (per-channel API Key), the
  response envelope, rate limiting, the sandbox flag, and the full endpoint
  catalog with request/response examples.
---

# Qapla' Public API (v1.3)

Qapla' is a SaaS platform for e-commerce logistics: multi-carrier shipping,
real-time tracking, label printing (PDF/ZPL), transactional notifications, and
analytics. This skill teaches you to integrate with its **public REST API**.

> **Official docs (always the source of truth):** <https://api.qapla.dev/1.3/>
> The pages are bilingual (IT default, `/1.3/en/` for English). This skill
> mirrors the public docs so you can work offline, but when a parameter is
> ambiguous or you suspect drift, defer to the live docs.

## Core facts — read these first

| Topic | Value |
|---|---|
| **Base URL** | `https://api.qapla.it/<version>/<endpoint>` (e.g. `https://api.qapla.it/1.3/pushShipment`) |
| **Protocol** | REST over HTTPS; JSON in, JSON out. Methods: GET/POST/PUT/DELETE/PATCH (most write endpoints use POST) |
| **Auth** | Per-**channel** API Key, sent as `apiKey` in the JSON body (see `references/authentication.md`) |
| **Response envelope** | `{"<endpointName>": {"result": "OK"\|"KO", "error": null\|"<message>"}}` |
| **Rate limit** | Token bucket: 120 capacity, refill 2 tokens/sec. A batch of N items costs N tokens. Over limit → HTTP `429 Too Many Requests` |
| **Time zone** | CEST (UTC+2 DST / UTC+1 winter). Dates are `YYYY-MM-DD`, datetimes `YYYY-MM-DD HH:MM:SS` |
| **Sandbox** | No separate environment. Pass `"sandbox": true` on endpoints that support it (e.g. `createLabel`, `getQuotes`) to test without real effects (no carrier pickup, no billing) |
| **Versions** | `1.3` is the production version. `1.1`/`1.2` are deprecated but still served. `getPudos` lives under `/1.2/`. A newer **v2** (different auth) exists at `/v2/` — out of scope here |

## Domain model in one minute

Qapla' has three orthogonal "pillars"; a merchant may use only some:

1. **Tracking** — shipments that already have a tracking number live in `ordini`
   (the central shipments table). Push them with **`pushShipment`**.
2. **Transactional events** — on each tracking status change, Qapla' fires
   notifications (email/SMS/webhook) to merchant and recipient.
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

## How to use this skill

1. Read `references/conventions.md` and `references/authentication.md` once —
   they apply to **every** call (envelope, errors, rate limiting, the `apiKey`).
2. Pick the endpoint from `references/endpoints.md` (full catalog) or the per-
   endpoint deep-dives:
   - `references/pushshipment.md`
   - `references/pushorder.md`
   - `references/createlabel.md`
   - `references/getquotes.md`
   - `references/getpudos.md`
3. Use the runnable example payloads in `references/examples/` as a starting
   point — they are the real request/response samples from the official docs.

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

## Guardrails

- This skill documents the **public** API only. Do not invent endpoints,
  parameters, or fields. If something isn't here or on <https://api.qapla.dev>,
  say so rather than guessing.
- Carrier-specific required fields (customs blocks, PUDO, service codes) vary a
  lot — see the per-endpoint references and the live docs before assuming.
