# Changelog

All notable changes to this package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note:** this version number is the **package** version (the agent knowledge
> pack), which is independent from the Qapla' **API** version it documents
> (currently public API `1.3`).

## [Unreleased]

## [1.4.2] - 2026-09-03

Validation release: the 1.4.1 corrections now have eval coverage, which
immediately turned up one place 1.4.1 had missed.

### Added
- **Six eval scenarios (#20–25), one per 1.4.1 correction** — `updatedAfter`'s
  timezone, the mixed timestamp formats, the sandbox casing break, the v2 rate
  limit, second-tier resources being published rather than in flight, and the
  spec's `info.version` proving nothing about its contents. Three are negative
  controls on a wrong premise, which is the shape these failures actually take.
  The full suite is 25/25 as of 2026-09-03; the previous 19 scenarios covered
  none of what 1.4.1 fixed, which is why that drift reached a customer.

### Changed
- **`evaluation/` is no longer installed with the skill.** It is marked
  `export-ignore` in `.gitattributes`, so the documented `git archive` install
  path (README updated) leaves it out, as do GitHub's release tarballs. It listed
  the expected answer for every validation prompt right next to the content it
  validates, and an eval run caught an agent reading it while answering one of
  those prompts. The suite stays in the repo — it is a maintainer tool, not part
  of the knowledge pack.

### Fixed
- **`v2/sandbox.md`: the `updatedAfter` / `updatedBefore` rows carried no
  timezone warning.** 1.4.1 said the `Europe/Rome` caveat was "called out
  wherever the filter appears"; that was overstated — it landed in
  `v2/overview.md` only, while the query-param table an integrator actually
  reads when calling `GET /v2/sandbox` still described them as plain "ISO 8601
  datetime filter". Both rows now carry the warning, with a note on what to do
  about it (convert the cursor, or overlap and de-duplicate) and a pointer that
  the `shipments` resource has the same filter. Found by writing eval scenario
  20, which exists precisely to cover this failure.

## [1.4.1] - 2026-09-03

Corrections to the v2 references, realigning them with the `qore/api`
implementation and the regenerated public spec. Two of the entries below change
behaviour you may already have coded against — read the `updatedAfter` and
sandbox notes.

### Fixed
- **v2 is not uniformly UTC, and never emits a literal `Z`.** `v2/overview.md`,
  `migration.md` and `versioning.md` each claimed UTC / `YYYY-MM-DDTHH:MM:SSZ`
  across the board — three copies of the same wrong sentence. Reality:
  `parcels` and `orders` use ATOM with an explicit `+00:00`, while **shipment
  tracking** (`statusDate`, `statusUpdatedAt`, `history[].date`) and **sandbox**
  return `"Y-m-d H:i:s"` with **no offset**, in `Europe/Rome`. Moving tracking to
  real UTC is a *planned* breaking change, not a done one.
- ⚠️ **`updatedAfter` is read in `Europe/Rome` too**, which is the dangerous half:
  polling incrementally in UTC does not raise an error, it **silently skips
  shipments** in the offset window. Now called out wherever the filter appears.
- **`orders`, `shipments`, `labels` and `couriers` are no longer "not yet in the
  public spec".** That was true when written; the Swagger snapshot had simply gone
  stale at 2.14.0 and was regenerated to 2.21.9 (published as api.qapla.dev
  `1.0.11` on 2026-09-03), at which point they appeared. Reworded to "published,
  but not detailed here", which is what actually distinguishes them.
- **`versioning.md`: the spec snapshot's `info.version` does not identify the
  contracts inside it.** It is a hand-dumped static file whose version label is
  whatever `APP_VERSION` was at dump time — verified today, the published snapshot
  reads `2.21.9` while the schemas in it are 2.21.10's (camelCase `sandbox`,
  `422`/`429` on `/v2/auth/token`). So the label spots a badly stale spec but
  cannot tell you whether a feature is present; read the content for that. The live
  `GET /v2/version` is exact, and carries a build stamp
  (`v2.21.10-202609031153`) — parse it as a prefix, not bare semver.
- **The `api_key` warning in `v2/authentication.md` is obsolete**: the public docs
  now show `apiKey`. Kept the field guidance and added the real failure mode — a
  wrong field name is **`422`** (`apiKey should not be blank`), not `400`; with
  `#[MapRequestPayload]`, `400` means a missing or malformed body.
- **Rate limit in `v2/overview.md` was two generations old** (120 capacity, refill
  2/sec). It is **300** capacity, refill **150/min** since `qore/api` v2.20.0. The
  same stale numbers were still in the token-response example in
  `v2/authentication.md` and in `references/examples/v2/authToken.response.json`,
  and `rate_limit.refill_rate` was described as tokens per **second** when it is
  per **minute** — all three fixed, along with the stale "refill ~2/sec" comment
  on the retry constants in `scripts/qapla_v2_client.py`. (The v1.x limit is a
  different bucket and is unchanged: 120 capacity, 2/sec.)
- **`v2/parcels.md` restated the sandbox casing** and was left inconsistent with
  the entry below; it now points at `v2/sandbox.md` instead of duplicating it.

### Changed
- ⚠️ **`v2/sandbox.md`: the casing asymmetry is gone — and that is a breaking
  change.** Up to `qore/api` 2.21.9 the endpoint accepted `stringValue` but
  answered `string_value`, so you could not read back what you had just written
  under the same names. `qore/api` **2.21.10** (released 2026-09-03) makes request
  and response both camelCase. Entity table, response example and the
  cross-reference in `v2/parcels.md` all updated. **If you parse the snake_case
  response, rename the fields.**
- **`v2/authentication.md` error table repeated the `400` mistake** it warns about
  two sections earlier: it listed `400` for a missing `apiKey`, when that is
  `422`. `400` is now described as an absent or malformed body, and the two codes
  the public Swagger omitted — `422` and `429`, both corrected in `qore/api`
  2.21.10 — are documented.


## [1.4.0] - 2026-07-07

### Added
- **v2: three new stable endpoints**, verified against `qore/api` **2.12.0**
  (2026-07-06):
  - `references/v2/couriers.md`: `POST /v2/couriers/delivery-times` (rank
    couriers fastest-first for a destination CAP, `detail: summary|full`) and
    `POST /v2/couriers/efficiency-index` (0–100 score blending
    speed/consistency/reliability 40/20/40, best-first). Both are cross-merchant
    network benchmarks, scopes `delivery-times:read` / `efficiency-index:read`.
    Noted: the product-entitlement gate is **not wired yet** on either endpoint
    despite being billable features internally (explicit TODO in the
    controllers) — don't assume `403 PRODUCT_NOT_OWNED` can't happen later.
  - `references/v2/stock-release.md`: `POST /v2/shipments/{id}/stock-release`
    (redeliver / redeliver to a new address / return to sender a shipment held
    in depot), scope `shipments:write`. GLS/TNT resolve synchronously
    (`courierOutcome: ok|error`); BRT is deferred (`pending`, resolved later via
    tracking events).
  - `references/v2/endpoints.md` moved these three into the stable-core table
    (with pointers back to the still-in-flight general `couriers`/`shipments`
    resources); `references/v2/overview.md` version bumped to 2.12.0.
  - New runnable examples in `references/examples/v2/`: `deliveryTimes`
    (+ `deliveryTimesFull`), `efficiencyIndex`, `stockRelease` request/response
    pairs.
  - `scripts/qapla_v2_client.py`: convenience methods `get_delivery_times`,
    `get_efficiency_index`, `request_stock_release`.

## [1.3.0] - 2026-06-22

### Added
- **v2 reference client** `scripts/qapla_v2_client.py` (stdlib-only, Python 3.8+):
  token exchange + JWT caching/refresh, Bearer auth, RESTful verbs, RFC 7807 error
  parsing (`QaplaV2Error` carries `status`/`title`/`detail`/`violations`), `429`
  retry with `X-RateLimit-Retry-After` support, parcels convenience methods, and
  async job polling (`poll_job`). CLI smoke test exchanges a token and prints the
  granted scopes.
- **Runnable v2 example payloads** in `references/examples/v2/`: `authToken`
  request/response, `createParcels` request + sync response + async `202`, `job`
  response, RFC 7807 `error.problem`, and `sandbox` request/response (showing the
  camelCase-in / snake_case-out quirk). Wired into the v2 deep-dives.

### Changed
- `references/v2/*` and `README.md`: link the new client and example payloads.

## [1.2.1] - 2026-06-22

### Added
- `v2/parcels.md`: documented the optional **`x-label-format`** request header
  (`PDF` default / `ZPL`) on `POST /v2/parcels`, found while verifying the
  controller.
- `evaluation/scenarios.md`: 4 new v2 scenarios (#13–16) covering parcels async
  jobs, the `403`/scope model, the `apiKey` auth field, and the envelope negative
  control — **run 4/4 PASS**, no content bug found. The `≤10` sync / `>10` async
  threshold was confirmed against the `qore/api` `ParcelsController`.

### Changed
- `README.md`: reflect that the skill now documents the **v2 stable core** —
  added a v2 badge, the `references/v2/` tree, and an updated scope/disclaimer.

## [1.2.0] - 2026-06-21

### Added
- **v2 API stable core now documented** under `references/v2/`. Reversing the
  1.1.2 "pointer-only" stance: v2 has matured (it is the generation the platform is
  moving toward), so the skill now teaches its stable surface, extracted from the
  real `qore/api` implementation (v2.9.4 — more current than the public Swagger,
  which lags). New files:
  - `v2/overview.md` — model, base URL (`api.qapla.it/v2`), JWT auth, RFC 7807
    errors, UTC/ISO 8601, ETag/`304`, rate limits, and the **async jobs** pattern
    (`202` + poll `/v2/jobs/{jobId}`), plus a v1.3↔v2 comparison.
  - `v2/authentication.md` — token exchange (`POST /v2/auth/token` with **`apiKey`**
    camelCase → Bearer JWT, 24h), token caching, and the now-**enforced granular
    scopes**.
  - `v2/parcels.md`, `v2/sandbox.md` — full CRUD deep-dives with verbatim field
    names from the implementation DTOs.
  - `v2/endpoints.md` — v2 catalog: the stable core plus the in-flight resources
    (orders, shipments, labels, couriers) flagged as not-yet-in-public-spec.

### Changed
- Wired v2 cross-references through `versioning.md`, `migration.md`, `overview.md`,
  `authentication.md`, `SKILL.md`, `AGENTS.md`, and the Cursor rule.
- Corrected two facts that drifted since 1.1.2 as v2 evolved: **scopes are now
  granular and enforced** (no longer wildcard `['*']`), and the auth field is
  confirmed **`apiKey`** (camelCase).

## [1.1.2] - 2026-06-17

### Changed
- **v2 section reduced to a drift-proof pointer.** A pre-release assessment
  against the real `qore/api` implementation found the v2 details had drifted: the
  auth field is `apiKey` (not `api_key`), scopes are not granular yet, the version
  label was wrong, the surface is larger than listed, and v2 is no longer
  "preview". Rather than ship specifics that conflict with the deployed API,
  `versioning.md` and `migration.md` now describe v2 only at a high level (Bearer
  JWT, HTTP-status errors, UTC/ISO 8601) and defer to the live docs at
  <https://api.qapla.dev/v2/> for endpoints, fields, scopes, and the auth payload.
  Aligned the v2 wording in `overview.md`, `SKILL.md`, `AGENTS.md`, and the Cursor
  rule (no more "preview/opt-in").

### Fixed
- `webhooks.md`: corrected the return-webhook `refundMethodCode` example value
  (`"ORIGINAL"` → `"0001"`) to match the `webhook.qapla.dev` source.

### Removed
- `docs/merge-plan.md` — internal one-off planning artifact (the merge it tracked
  is complete); removed so it no longer travels with the distributed pack.
- Sanitized the two internal "partner skill" references in
  `evaluation/scenarios.md`.

### Wired
- Added `trackingbytimeframe.md` and `apivirtual.md` to the reading order in
  `SKILL.md`, `AGENTS.md`, and the Cursor rule (previously only linked from
  `overview.md`/`endpoints.md`).

## [1.1.1] - 2026-06-16

### Fixed
- `webhooks.md`: re-verified against the now-local `webhook.qapla.dev` source and
  aligned field types to it — `qaplaStatusID` is a **string** (`"99"`, coerce with
  `Number()` before comparing), `rows[]` numeric fields are strings, and the
  return-webhook example uses the real envelope values. Retry behavior (2 more
  attempts) and the 100-failure auto-disable confirmed verbatim.
- `statuses.md`: noted that the webhook `qaplaStatusID` is a string.

## [1.1.0] - 2026-06-16

Content expansion merged from a comparison with a sibling integration skill, with
every imported fact verified against the authoritative sources (the live
`webhook.qapla.dev` and the `api.qapla.dev` per-version sources) and validated by
a fresh-context eval (12/12). Highlights: Pillar 2 (webhooks) is now covered, the
canonical status model is documented from the real `getQaplaStatus` output, and
the version policy (incl. v2) and a legacy-migration guide are added.

### Added
- **Webhooks reference (Pillar 2)** — `references/webhooks.md` documents the
  outbound event callbacks (Shipments / Shipments Return / Orders), the verified
  payload fields (v1.2 core + v1.3 enhanced `rows`/`parcels`/`consignee`), the
  `{"result":"OK"}`/`{"result":"KO"}` response contract, retry/auto-disable
  behavior, and security guidance. Verified against the live docs at
  <https://webhook.qapla.dev>.
- `references/examples/webhookReceiver.md` — minimal Node (Express) and PHP
  receivers that verify `apiKey`, return the contract body, and branch on the
  canonical `qaplaStatusID`.
- Wired `webhooks.md` into `overview.md`, `endpoints.md`, `SKILL.md`,
  `AGENTS.md`, and the Cursor rule; added webhooks to the skill trigger
  descriptions.
- **Status model reference** — `references/statuses.md` documents the canonical
  Qapla' status table (ids, IT labels, colors, and the ECCEZIONE sub-states),
  verified against the live `getQaplaStatus` endpoint, plus the three
  context-dependent field namings (`statusID` in the list vs `id` in embedded
  `qaplaStatus` objects vs `qaplaStatusID` in webhooks) and the "branch on the
  canonical integer id, never the label" rule. Wired into all entrypoints.
- **Versioning reference** — `references/versioning.md` documents the API version
  policy verified against the live docs and per-version sources: `1.3` current,
  `1.1`/`1.2` deprecated-but-active (with `1.2` still hosting many not-yet-migrated
  endpoints), `1.4` as a `createLabel`-only extension (`parcelsTracking`), and the
  separate **v2** generation (Bearer/JWT auth via `/v2/auth/token`, UTC + ISO-8601,
  HTTP-status errors, scopes; current surface `auth`/`parcels`/`sandbox`). Lists
  which endpoints are 1.3 vs 1.2-only. Wired into all entrypoints.

- **Migration guide** — `references/migration.md` covers upgrading a legacy
  integration: v1.0/1.1 → v1.2/1.3 checklist (URL segment, auth placement,
  payload diffing, the real `pushShipment` envelope, rate limiting, sandbox) and
  the v1.x → v2 differences (Bearer/JWT + scopes, HTTP-status errors, UTC/ISO-8601,
  parcels as a first-class CRUD resource, async bulk create via
  `AsyncJobResponse`, sandbox-as-resource), all verified against the per-version
  sources. Wired into all entrypoints.

- **`trackingByTimeFrame` deep-dive** — `references/trackingbytimeframe.md`: the
  pull/polling alternative to webhooks (GET window query, `qaplaStatus`-object
  response, polling-cadence and dedup guidance).
- **Virtual courier deep-dive** — `references/apivirtual.md`: `POST /virtual/`
  (note: non-versioned path), the `virtual[]` update array (≤100, `statusID`
  driven), and how it pairs with `pushShipment`.
- `createlabel.md`: added a **`confirmLabel`** section documenting the two-step
  generate→transmit flow (`labelCreationDate` vs `labelID`, per-courier
  `pickupDate`/`pickupTime`, the base64 manifest/borderò response, Customer Care
  activation). Verified against the per-version sources.

### Fixed
- `endpoints.md`: corrected the `getQaplaStatus` description — it returns the
  canonical status list (id/label/color/sub-states), not generic "service info".
- `overview.md` / `AGENTS.md`: clarified the version row — `1.2` is deprecated but
  still required for un-migrated endpoints (previously implied `1.3`-only).

## [1.0.0] - 2026-06-15

First stable release. A portable, multi-agent knowledge pack for the Qapla'
public REST API (v1.3), validated end-to-end (eval 7/7 with fresh-context
agents).

### Added
- **Multi-agent support** via thin entrypoints over a single source of truth:
  - `AGENTS.md` — universal entrypoint (read by Codex, Gemini CLI, Cursor,
    Copilot, Windsurf, Aider, Zed, Jules and 20+ tools), with a
    marker-delimited snippet to merge into an existing `AGENTS.md` plus inline
    core facts.
  - `.cursor/rules/qapla-api.mdc` — Cursor *agent-requested* rule, loaded
    on-demand by its `description` (same trigger as the Claude skill).
  - `references/overview.md` — canonical orientation (core facts, domain model,
    "which endpoint do I need?" decision rule, guardrails) that every entrypoint
    points to, so a fix lands in one place.
- Claude skill entrypoint `SKILL.md` (YAML frontmatter: `name`, `description`).
- Endpoint references: `conventions.md`, `authentication.md`, `endpoints.md`,
  and per-endpoint deep-dives (`pushshipment.md`, `pushorder.md`,
  `createlabel.md`, `getquotes.md`, `getpudos.md`).
- Real request/response sample payloads under `references/examples/`.
- Dependency-free reference Python client `scripts/qapla_client.py` (injects
  `apiKey`, parses the two-level envelope, retries `429` with backoff).
- Evaluation scenarios and run logs in `evaluation/scenarios.md` (7/7 passing,
  including the critical `getQuotes` header-auth and anti-hallucination cases).

### Changed
- `SKILL.md` reduced to a thin entrypoint that points to
  `references/overview.md` (no behavior change; content relocated to the single
  source of truth).
- `README.md` reframed from "Claude Skill" to a multi-agent knowledge pack, with
  per-agent install instructions (Claude / AGENTS.md / Cursor).
- API accuracy corrected against the authoritative 1.3 docs (e.g. `getQuotes`
  authenticates via the `x-api-key` header, not `apiKey` in the body).

[Unreleased]: https://github.com/Qapla/qapla-api-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Qapla/qapla-api-skill/releases/tag/v1.0.0
