---
name: qapla-api
description: >-
  Integrate with or answer questions about the Qapla' shipping & tracking REST
  API (public v1.3). Use this when working with Qapla' to push shipments or raw
  orders, generate and confirm carrier labels, track parcels, get real-time
  multi-carrier quotes, look up pickup points (PUDO), verify addresses, list
  couriers and channels, or receive outbound tracking-event webhooks. Covers
  authentication (per-channel API Key), the
  response envelope, rate limiting, the sandbox flag, and the full endpoint
  catalog with request/response examples. Also covers the newer **v2** generation
  (Bearer/JWT auth, RESTful resources, async jobs) for its stable core — parcels,
  sandbox, auth, jobs.
license: MIT
---

# Qapla' Public API (v1.3)

This skill teaches you to integrate with the **public REST API** of Qapla', a
SaaS platform for e-commerce logistics (multi-carrier shipping, real-time
tracking, label printing, transactional notifications).

## How to use this skill

1. **Read `references/overview.md` first** — it is the canonical orientation:
   core facts (base URL, auth, response envelope, rate limit, sandbox,
   versions), the domain model, and the "which endpoint do I need?" decision
   rule.
2. Then read `references/conventions.md` and `references/authentication.md` —
   they apply to **every** call.
3. Pick the endpoint from `references/endpoints.md` (full catalog) or the
   per-endpoint deep-dives (`references/pushshipment.md`, `pushorder.md`,
   `createlabel.md`, `getquotes.md`, `getpudos.md`, `trackingbytimeframe.md` —
   the pull alternative to webhooks — and `apivirtual.md` — the virtual courier).
   To receive event callbacks instead of calling an endpoint, see
   `references/webhooks.md` (Pillar 2). To interpret tracking statuses, see
   `references/statuses.md` (branch on the canonical id, never the label). For the
   version policy (which version to call, v1.2-only endpoints, the separate v2
   generation), see `references/versioning.md`; to upgrade a legacy integration,
   see `references/migration.md`.
4. Use the runnable example payloads in `references/examples/` as a starting
   point, and the dependency-free reference client in `scripts/qapla_client.py`
   when writing code.
5. **For the v2 API** (a separate, RESTful generation with Bearer/JWT auth — the
   direction the platform is heading), start at `references/v2/overview.md`, then
   `references/v2/authentication.md` and the resource deep-dives
   (`references/v2/parcels.md`, `references/v2/sandbox.md`,
   `references/v2/endpoints.md`). Most integrations still target v1.3 today; use
   v2 when you need a resource it exposes (e.g. parcels) or its model.

> The same knowledge powers the cross-agent entrypoints in this repo
> (`AGENTS.md`, `.cursor/rules/qapla-api.mdc`); all of them point back to
> `references/overview.md` so there is a single source of truth.

> **Source of truth:** the live docs at <https://api.qapla.dev/1.3/>. This skill
> mirrors them so you can work offline; if anything drifts, trust the live docs.
