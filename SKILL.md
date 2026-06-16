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
  catalog with request/response examples.
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
   `createlabel.md`, `getquotes.md`, `getpudos.md`). To receive event callbacks
   instead of calling an endpoint, see `references/webhooks.md` (Pillar 2). To
   interpret tracking statuses, see `references/statuses.md` (branch on the
   canonical id, never the label). For the version policy (which version to call,
   v1.2-only endpoints, the v2 preview), see `references/versioning.md`.
4. Use the runnable example payloads in `references/examples/` as a starting
   point, and the dependency-free reference client in `scripts/qapla_client.py`
   when writing code.

> The same knowledge powers the cross-agent entrypoints in this repo
> (`AGENTS.md`, `.cursor/rules/qapla-api.mdc`); all of them point back to
> `references/overview.md` so there is a single source of truth.

> **Source of truth:** the live docs at <https://api.qapla.dev/1.3/>. This skill
> mirrors them so you can work offline; if anything drifts, trust the live docs.
