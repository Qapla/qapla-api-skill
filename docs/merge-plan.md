# Merge plan — import the best of `qapla-integration-skill` into `qapla-api`

**Date:** 2026-06-16
**Source repo:** `roberto976/qapla-integration-skill` (cloned at `/tmp/qapla-integration-skill`)
**Target repo:** this repo (`qapla-api-skill`)

## Goal

Keep our engineered base (hub-and-spoke single source of truth, multi-agent
entrypoints, runnable Python client, eval suite, CHANGELOG/semver) and absorb the
content areas where the partner skill is more complete: **webhooks (Pillar 2),
canonical status model, v1.2 parity, and legacy migration.** We merge content,
not structure — everything new must still point back to `references/overview.md`.

## Guiding principles

1. **Our architecture wins.** New material becomes new `references/*.md` files in
   our flat layout; we do not adopt the partner's `skill/qapla-integration/...`
   nesting or its per-file `source:`/`synced:` frontmatter (our single-source-of-
   truth model + CHANGELOG already covers freshness).
2. **Verify before importing.** The partner's status table and webhook payloads
   contain likely-invented specifics and are mutually inconsistent (see Risks).
   Nothing gets copied verbatim; every imported fact is checked against the
   authoritative docs (live `api.qapla.dev` / `webhook.qapla.dev` + our `docs`
   MCP) and reconciled.
3. **No drift.** Each new reference file is wired into `overview.md`,
   `endpoints.md`, `SKILL.md`, `AGENTS.md`, and the Cursor rule so all entrypoints
   stay consistent.
4. **One concern per commit**, mirrored in CHANGELOG `Unreleased`, shipped as a
   minor version bump (`1.1.0`).

## Per-file decision (partner → us)

| Partner file | Decision | Target in our repo |
|---|---|---|
| `references/webhooks.md` | **Import + verify** | `references/webhooks.md` (new) |
| `references/statuses.md` | **Import + verify** (reconcile ID table) | `references/statuses.md` (new) |
| `references/versioning.md` | **Merge facts** into our `overview.md` + a short `references/versioning.md` | `overview.md` edits + new `versioning.md` |
| `references/migration.md` | **Import + verify** | `references/migration.md` (new) |
| `references/concepts.md` | **Skip** — our `overview.md` domain model already covers the 3-pillar model + glossary; cherry-pick any missing vocab into `overview.md` | — |
| `references/authentication.md` | **Skip** — ours exists; cherry-pick only the token-bucket wording if clearer | (maybe small edit) |
| `references/errors.md` | **Compare** with our `conventions.md`; import retryable-vs-fatal classification + idempotency notes if missing | possible `conventions.md` edit |
| `references/checkaddress.md` | **Skip** — we have `checkAddress` examples + endpoint catalog; add a deep-dive only if we later expand |
| `references/orders.md` / `shipments.md` / `labels.md` / `couriers.md` | **Cherry-pick only.** We already have `pushshipment/pushorder/createlabel/getquotes/getpudos` deep-dives. Pull in specific gaps: `trackingByTimeFrame` (pull model), `confirmLabel`, virtual-courier / tracking-only, COD & customs notes, `addParcel` | targeted edits to existing deep-dives + `endpoints.md` |
| `examples/*.md` (curl + Node + PHP) | **Adapt** — add a `webhook-receiver` example; consider curl snippets alongside our JSON | new `references/examples/` entries |
| `scripts/sync-docs.sh` | **Skip** — checklist-only, superseded by our model | — |
| `docs/plans`, `docs/specs` | **Skip** — their planning docs | — |

## Concrete work items

### Phase 1 — Webhooks (highest-value gap)
- [ ] Create `references/webhooks.md` from the partner version, after verifying
      against `https://webhook.qapla.dev` + `docs` MCP:
  - event types (Shipments / Shipments Return / Orders)
  - payload (v1.2 core + v1.3 enhanced: `rows`/`parcels`/`consignee`)
  - **response contract** `{"result":"OK"}` / `{"result":"KO"}`
  - retry (3 attempts) + auto-disable (100 consecutive failures)
  - security (verify `apiKey`, respond <2s, idempotency key)
- [ ] **Reconcile field names** — partner's two files disagree (`qaplaStatusID`
      vs `statusID`, `reference` vs `orderReference`, `courier` vs `courierCode`).
      Pick the real names from authoritative docs; document one schema only.
- [ ] Add `references/examples/webhookReceiver.md` (or `.php`/`.js`) — minimal
      receiver that validates `apiKey`, queues async, returns the contract body.
- [ ] Wire into `overview.md` Pillar 2 ("Transactional events" now has a file),
      `endpoints.md`, `SKILL.md`, `AGENTS.md`, Cursor rule.

### Phase 2 — Canonical status model
- [ ] Create `references/statuses.md`: two-layer model (raw `courierStatus` vs
      canonical id), "branch on the integer id, never the label" rule,
      `getQaplaStatus` endpoint, `lang` (it/en/es), sub-states (`detailID`).
- [ ] **Verify the status ID table against `getQaplaStatus` live output** before
      committing — the partner's 0/10/20…99 mapping and sub-state codes are
      unverified and must not be shipped if they can't be confirmed. If we can't
      confirm specific rows, describe the model and point to the live endpoint
      rather than printing a possibly-wrong table.
- [ ] Cross-link with `webhooks.md` (the status id arrives in webhook payloads).

### Phase 3 — versioning [DONE]
> **Correction after verifying the live docs:** the partner's premise ("v1.2 NOT
> deprecated; both current") is **wrong**. The official 1.3 intro marks `1.1` and
> `1.2` as DEPRECATED (and `1.0` retired). The real nuance is that `1.2` is
> *deprecated but still active*, and **many endpoints have not been migrated to
> 1.3**, so they are still served only under `1.2`. Our existing `overview.md`
> wording was already correct.
- [x] Added `references/versioning.md`: version status table; 1.3-vs-1.2-only
      endpoint lists; `1.4` = `createLabel`-only (`parcelsTracking`); `v2`
      generation (Bearer/JWT via `/v2/auth/token`, UTC/ISO-8601, HTTP-status
      errors, scopes; surface = auth/parcels/sandbox, OpenAPI 2.8.8).
- [x] Refined `overview.md` + `AGENTS.md` version rows to capture the
      deprecated-but-required 1.2 nuance and point to `versioning.md`.

### Phase 4 — Migration [DONE]
> **Corrections after verifying sources:** the partner's `migration.md` repeated
> the "v1.2 not deprecated" error (fixed → deprecated-but-active), falsely claimed
> `updateOrder` was *removed* (it's simply 1.2-only — `1.2/updateOrder.php`
> exists), and invented `updated`/`skipped` response counters (real envelope has
> `count`/`imported`). Its v2 async claim, however, **checked out** — `POST
> /v2/parcels` really returns `202` + `AsyncJobResponse`.
- [x] Created `references/migration.md`: v1.0/1.1 → v1.2/1.3 checklist (URL
      segment, auth placement, payload diffing, real `pushShipment` envelope,
      rate limiting, sandbox) + verified v1.x → v2 differences (Bearer/JWT +
      scopes, HTTP-status errors, UTC/ISO-8601, parcels-as-CRUD, async bulk via
      `AsyncJobResponse`, sandbox-as-resource).
- [x] Wired into SKILL/AGENTS/Cursor/overview + cross-linked from `versioning.md`.

### Phase 5 — Cherry-picked endpoint gaps
- [ ] `trackingByTimeFrame` (pull alternative to webhooks) — add to
      `endpoints.md` + a short note in a deep-dive or `shipments` section.
- [ ] `confirmLabel` flow detail (create → confirm/transmit) — ensure
      `createlabel.md` covers the two-step transmission.
- [ ] Virtual courier / tracking-only shipments — note in `pushshipment.md`.
- [ ] COD / customs / `addParcel` (FedEx/UPS/TNT/GLS) multi-parcel notes — fold
      into `createlabel.md` where currently thin.

### Phase 6 — Tests + release
- [ ] Add eval scenarios in `evaluation/scenarios.md`: (a) webhook receiver
      returns correct contract body; (b) branch on canonical status id not label;
      (c) v1.2 endpoint awareness; (d) negative control on a fabricated status id.
- [ ] Run the full eval (target: still green).
- [ ] CHANGELOG `Unreleased` → `1.1.0`; bump version reference; tag + push.

## Wiring checklist (run after each new reference file)

Every new `references/X.md` must be referenced in **all** of:
- `references/overview.md` ("Where to go next" + relevant pillar)
- `references/endpoints.md` (catalog row)
- `SKILL.md` (reading order)
- `AGENTS.md` (same list)
- `.cursor/rules/qapla-api.mdc`

This is what preserves the single-source-of-truth invariant.

## Risks / things to watch

1. **Unverified specifics in partner content.** The status ID table, sub-state
   codes, retry counts, and auto-disable threshold may be invented. Treat all as
   *claims to verify*, not facts. When unverifiable, describe the model + link the
   live endpoint instead of printing exact numbers.
2. **Internal payload inconsistency.** `webhooks.md` and `statuses.md` use
   different field names for the same webhook payload. We must ship ONE
   reconciled schema, or we reproduce the partner's bug.
3. **Scope creep into v2.** Keep v2 as an opt-in overview only; no deep-dive
   until there's a real need.
4. **Example-format divergence.** We standardize on our JSON examples; adding
   curl/Node/PHP is fine but keep one canonical request payload per endpoint to
   avoid two sources of truth.

## Suggested commit sequence

1. `feat: add webhooks reference (Pillar 2) + receiver example`
2. `feat: add canonical status model reference`
3. `feat: document v1.2/v1.3 parity + versioning`
4. `feat: add legacy API migration guide`
5. `docs: fill endpoint gaps (trackingByTimeFrame, confirmLabel, COD/customs)`
6. `test: add eval scenarios for webhooks + status branching`
7. `chore: release 1.1.0`
