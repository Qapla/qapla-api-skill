# Evaluation scenarios — qapla-api skill

> **Last validated run: 2026-06-22 — 16/16 passed** (12 v1.x + 4 new v2 scenarios
> for the `references/v2/` content). All answers accurate per the references; the
> v2 docs held up with no content bug found. Critical cases hold: `getQuotes`
> `x-api-key` header auth (#3), anti-hallucination on an invented endpoint (#5),
> plausible-but-wrong status id (#12), and the v2 envelope negative control (#16).
> The #8 run earlier caught a real content bug (wrong status ids in the receiver
> example), since fixed.

Representative prompts used to validate the skill. Per Anthropic's skill
best-practices, run these against **Haiku, Sonnet and Opus** in a fresh session
(the skill auto-loads from its `description`), and check both that the skill
*triggers* and that the answer is *correct*.

Each scenario lists: the user prompt, what should happen, and the desk-check
result (whether the bundled content is sufficient to answer correctly without
the live docs).

| # | Prompt | Expected behavior | Desk-check |
|---|---|---|---|
| 1 | "Using the Qapla' API, build me a pushShipment call for a UPS parcel with a tracking number." | Triggers skill; produces JSON with `apiKey` + `pushShipment: [{trackingNumber, courier: "UPS", ...}]`; notes per-item result checking. | ✅ covered by `references/pushshipment.md` + example |
| 2 | "I need Qapla' to generate a GLS label in sandbox and ship to a pickup point." | Explains the `pushOrder → createLabel → confirmLabel` flow; uses `"sandbox": true`; points to `getPudos` for the PUDO block. | ✅ covered by createlabel.md + getpudos.md |
| 3 | "Get me real-time shipping quotes for a 109€ parcel to Padova (35010)." | Builds a `getQuotes` body with address/postCode/city/state/country/value; explains `couriers[].quotes[]` response. | ✅ covered by getquotes.md + examples |
| 4 | "How do I authenticate to the Qapla' API and where does the key go?" | Per-channel API Key in the JSON body as `apiKey`; from Control Panel; treat as secret. | ✅ covered by authentication.md |
| 5 | "Does Qapla' have a /v3/ endpoint for bulk refunds?" | Should REFUSE to invent it — say it's not in the public docs and defer to api.qapla.dev. | ✅ guardrail in SKILL.md |
| 6 | "I'm getting HTTP 429 from pushShipment, what do I do?" | Explains token bucket (120 cap, 2/sec), exponential backoff, batch cost = N tokens. | ✅ covered by conventions.md |
| 7 | "Reformat this file to follow PEP 8" (on `qapla_client.py`) | **Negative control** — pure Python style; skill must NOT trigger. | ✅ correct discrimination |
| 8 | "Write a webhook receiver for Qapla' tracking updates." | Triggers; produces a receiver that **verifies `apiKey`**, returns `{"result":"OK"}` fast, branches on **`qaplaStatusID`**, dedups; mentions retry/auto-disable. | ✅ covered by `webhooks.md` + `examples/webhookReceiver.md` |
| 9 | "How do I detect that a Qapla' shipment was delivered?" | Branch on the **canonical id** (`CONSEGNATO = 99`), never the raw courier label; mentions `getQaplaStatus` / the id table. | ✅ covered by `statuses.md` |
| 10 | "Which API version do I call `trackingByTimeFrame` on?" | `1.2` (not migrated to 1.3); explains 1.2 is deprecated-but-active and still hosts many endpoints. | ✅ covered by `versioning.md` + `trackingbytimeframe.md` |
| 11 | "We're on API v1.1 — does v2 use the same API key?" | Same channel key, but **exchanged for a JWT** at `POST /v2/auth/token`; Bearer header; v1-style auth won't work on v2. | ✅ covered by `migration.md` + `versioning.md` |
| 12 | "Is `qaplaStatusID` 30 the in-transit status?" | **Negative control / anti-hallucination** — NO; `IN TRANSITO` is id **3** (30 is not a status); should correct, not confirm. | ✅ guarded by the verified `statuses.md` table |
| 13 | "On the Qapla' v2 API, how do I create 25 parcels for an order and get the result back?" | `POST /v2/parcels` with Bearer JWT; >10 parcels → **`202` async**, returns a job → poll `GET /v2/jobs/{jobId}` (or `webhookUrl`); ≤10 would be sync `201`. | ✅ covered by `v2/parcels.md` + `v2/overview.md` |
| 14 | "I'm calling the Qapla' v2 API and getting a `403` — what does it mean?" | v2 enforces **granular scopes** (and product ownership); `403` = authenticated but missing the required scope/product; error body is RFC 7807 (`application/problem+json`). | ✅ covered by `v2/authentication.md` + `v2/overview.md` |
| 15 | "What field does the Qapla' v2 token endpoint expect for the API key?" | **`apiKey`** (camelCase), in `POST /v2/auth/token`; returns a Bearer JWT. Should flag that public Swagger may still show `api_key` but the deployed API uses `apiKey`. | ✅ covered by `v2/authentication.md` |
| 16 | "Does the Qapla' v2 API return the same `{result: OK/KO}` envelope as v1?" | **Negative control** — NO; v2 uses real **HTTP status codes** + **RFC 7807** error bodies, not the v1 envelope. Should correct, not confirm. | ✅ guarded by `v2/overview.md` |

## Negative / edge checks
- Scenario 5 verifies the **anti-hallucination guardrail** (invented endpoint).
- Scenario 12 verifies the skill corrects a **plausible-but-wrong status id**
  (a non-existent id that earlier draft content had wrongly listed) instead of
  confirming it.
- Confirm the skill does NOT trigger on unrelated prompts (#7) — over-triggering is a failure too.

## How to run a quick live connectivity smoke test
With a real channel key:

```bash
QAPLA_API_KEY=xxxxx python3 scripts/qapla_client.py   # calls getChannel
```

## Run log

### 2026-06-22 — 4/4 new v2 scenarios passed (#13–16)

After documenting the v2 stable core (`references/v2/`, release 1.2.0), the 4 new
v2 scenarios were run with the same honest method — one fresh `general-purpose`
agent per verbatim prompt, no priming, installed skill synced from the repo first.
Each was asked to self-report skill trigger + references opened.

| # | Scenario | Triggered | Reference(s) opened | Result |
|---|---|---|---|---|
| 13 | create 25 parcels (async) | ✅ qapla-api | `v2/parcels.md`, `v2/overview.md`, `v2/authentication.md` | ✅ PASS — >10 → `202` + poll `GET /v2/jobs/{jobId}`; full token→create→poll flow; `x-label-format`, `409`, camelCase, `(reference, origin)` order key |
| 14 | v2 `403` meaning | ✅ qapla-api | `v2/authentication.md` | ✅ PASS — 401 (identity) vs 403 (missing scope/product); scopes enforced & listed in token; RFC 7807 body; ruled out expired-token |
| 15 | v2 token auth field | ⚠️ read repo files directly (no auto-trigger) | `v2/authentication.md` | ✅ PASS (content) — `apiKey` camelCase; flagged stale Swagger `api_key` |
| 16 | same envelope as v1? (negative) | ✅ qapla-api | `v2/overview.md`, `conventions.md` | ✅ PASS — correctly rejected; v2 uses HTTP status codes + RFC 7807, not the `{result}` envelope |

**No content bug found** — all four answers were accurate against the v2
references. The async threshold (`≤10` sync / `>10` async) was independently
confirmed against the `qore/api` `ParcelsController` (`if ($parcelCount <= 10)`)
before the run.

**Method note:** scenario #15's agent answered correctly but reported it did **not**
auto-trigger the skill — it located and read the reference files directly from the
repo (the eval runs with the repo as cwd, so the files are reachable via the
filesystem without the Skill tool). Content is validated either way; the
auto-trigger signal is weaker in this in-repo setup. The other three did invoke
`qapla-api` explicitly.

### 2026-06-16 — 5/5 new scenarios passed (webhooks/status/versioning/migration)

After the content merge (added `webhooks.md`, `statuses.md`, `versioning.md`,
`migration.md`, `trackingbytimeframe.md`, `apivirtual.md`), the 5 new scenarios
(#8–#12) were run with the same honest method — one fresh `general-purpose` agent
per verbatim prompt, no priming, installed skill synced from the repo first.

| # | Scenario | Triggered | Reference(s) opened | Result |
|---|---|---|---|---|
| 8 | webhook receiver | ✅ qapla-api | `webhooks.md`, `examples/webhookReceiver.md`, `statuses.md` | ✅ PASS — verifies `apiKey`, returns `{"result":"OK"}`, branches on `qaplaStatusID`, idempotent, handles all 3 event shapes |
| 9 | detect delivered | ✅ qapla-api | `statuses.md`, `webhooks.md` | ✅ PASS — `id 99` (CONSEGNATO); branch on canonical id; noted the field-naming-by-context nuance |
| 10 | trackingByTimeFrame version | ✅ qapla-api | `versioning.md` | ✅ PASS — `1.2` (not migrated to 1.3); mixing versions is expected |
| 11 | v2 same API key? | ✅ qapla-api | `versioning.md`, `authentication.md` | ✅ PASS — same source key, exchanged for a JWT at `/v2/auth/token`; Bearer header |
| 12 | `qaplaStatusID 30`? (negative) | ✅ qapla-api | `statuses.md` | ✅ PASS — correctly rejected; `IN TRANSITO` is id `3`, 30 is not a defined id |

**Bug caught and fixed by the eval:** scenario #8's agent flagged that
`examples/webhookReceiver.md` branched on `60`/`70` — ids that **don't exist** in
the canonical table (incorrect values from earlier draft content, written before
the status table was verified against the live `getQaplaStatus`). Corrected to `5`
(TENTATIVO DI CONSEGNA FALLITO) and `6` (ECCEZIONE) and re-synced. A repo-wide
grep confirms no other invented status-id literals remain.

### 2026-06-15 — 7/7 passed (post multi-agent refactor, fresh-context agents)

After splitting the skill into thin entrypoints (`SKILL.md`, `AGENTS.md`,
`.cursor/rules/qapla-api.mdc`) all pointing to a new canonical
`references/overview.md` (single source of truth), the 7 scenarios were re-run
with the same method (one fresh `general-purpose` agent per verbatim prompt).
The installed skill at `~/.claude/skills/qapla-api/` was synced from the repo
first — it is a *copy*, not a symlink, so edits to the repo must be deployed
before evaluating via auto-trigger.

| # | Scenario | Triggered | Read overview.md? | Result |
|---|---|---|---|---|
| 1 | pushShipment | ✅ qapla-api | ✅ | ✅ PASS — `apiKey` + array; `trackingNumber`/`courier:"UPS"`/`shipDate`; per-item result check |
| 2 | label + PUDO | ✅ qapla-api | ✅ | ✅ PASS — `getPudos → createLabel → confirmLabel`; `"sandbox": true`; PUDO fields vary per courier |
| 3 | getQuotes (critical) | ✅ qapla-api | ✅ | ✅ PASS — `x-api-key` header (not body); `recipient{}`; `amountShipment` string; `x-sandbox` header |
| 4 | authentication | ✅ qapla-api | ✅ | ✅ PASS — `apiKey` in body; Control Panel path; getQuotes header exception |
| 5 | anti-hallucination (critical) | ✅ qapla-api | ✅ | ✅ PASS — refused `/v3/bulkRefund`; version info reached *via the overview.md pointer* (no longer inline in SKILL.md) |
| 6 | rate limit 429 | ✅ qapla-api | ✅ | ✅ PASS — token bucket (120 cap, 2/sec); batch cost = N; backoff; ban warning |
| 7 | PEP 8 (negative) | ✅ did NOT trigger | n/a | ✅ PASS — pure Python style; no qapla-api activation; no file modified |

Key finding: 6/7 agents explicitly opened `references/overview.md`, confirming
the `SKILL.md → overview.md` indirection holds in a fresh context — the
orientation that used to be inline in `SKILL.md` is still reached. The critical
cases (#3 getQuotes header auth, #5 anti-hallucination) survive the refactor.

### 2026-06-15 — 7/7 passed (fresh-context agents)

Method: each of the 7 prompts was run in a separate fresh `general-purpose`
agent given only the verbatim prompt (no priming, no mention of Qapla' or that
it was a test). This is the honest measure of auto-trigger — an already-primed
session would trigger regardless. Each agent self-reported which skill/references
it used; answers were checked against the bundled references.

| # | Scenario | Triggered | Correctness check | Result |
|---|---|---|---|---|
| 1 | pushShipment | ✅ qapla-api | `apiKey` + array; `trackingNumber`/`courier:"UPS"`/**`shipDate`**; per-item result check explained | ✅ PASS |
| 2 | label + PUDO | ✅ qapla-api | `getPudos → pushOrder → createLabel → confirmLabel`; `"sandbox": true`; flagged PUDO fields vary per courier | ✅ PASS |
| 3 | getQuotes (critical) | ✅ qapla-api | **`x-api-key` header, NOT `apiKey` in body**; nested `recipient{}`; `amountShipment`; `parcels[]`; `x-sandbox` header | ✅ PASS |
| 4 | authentication | ✅ qapla-api | `apiKey` in body; Control Panel path; getQuotes header exception | ✅ PASS |
| 5 | anti-hallucination | ✅ qapla-api | refused to invent `/v3/bulkRefund`; noted no v3 / no refund endpoints; deferred to api.qapla.dev | ✅ PASS |
| 6 | rate limit 429 | ✅ qapla-api | token bucket (120 cap, 2/sec); batch cost = N tokens; exponential backoff; ban warning | ✅ PASS |
| 7 | PEP 8 (negative) | ✅ did NOT trigger | treated as pure Python style; no qapla-api / claude-api activation | ✅ PASS |

Notes:
- The critical `getQuotes` case (auth via `x-api-key` header) holds in a fresh
  context — the previously-failing behavior is fixed.
- No over-triggering: #7 stayed silent even though the target file was the Qapla'
  API client (correct discrimination: API contract vs. Python style).
- Side-effect of #7: the agent edited `scripts/qapla_client.py` (PEP 8 reformat);
  reverted afterward — a test artifact, not a real change.
