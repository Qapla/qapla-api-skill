# Evaluation scenarios — qapla-api skill

> **Last validated run: 2026-09-03 — 25/25 passed on the installed 1.4.2**, one
> fresh agent per scenario, `evaluation/` no longer installed. ⚠️ Two run-hygiene
> findings stand, both in the newest run-log entry: the repo's **git history**
> still serves retracted claims to an agent that greps it, and an eval agent
> **wrote a file into `scripts/`**. Critical cases hold:
> `getQuotes` `x-api-key` header auth (#3), anti-hallucination on an invented
> endpoint (#5), the PEP 8 negative control correctly not triggering the skill
> (#7), plausible-but-wrong status id (#12), and the v2 envelope negative
> control (#16). ⚠️ **But see the two method findings in the run log below: the
> suite has zero coverage for everything 1.4.1 corrected, and this file ships
> inside the installed skill, so an agent can read its own answer key.**

Representative prompts used to validate the skill. Per Anthropic's skill
best-practices, run these against **Haiku, Sonnet and Opus** in a fresh session
(the skill auto-loads from its `description`), and check both that the skill
*triggers* and that the answer is *correct*.

Each scenario lists: the user prompt, what should happen, and the desk-check
result (whether the bundled content is sufficient to answer correctly without
the live docs).

**Running them:** install with `git archive`, never `cp -r`, or this file comes
back into the skill and the agents can read their own expectations. Give each
agent only the user prompt. Afterwards, **check `git status`** — an agent has
written a file into `scripts/` before now. And distrust any answer whose sources
include commit messages: history holds claims that were later retracted.

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
| 15 | "What field does the Qapla' v2 token endpoint expect for the API key?" | **`apiKey`** (camelCase), in `POST /v2/auth/token`; returns a Bearer JWT. Should give `422` (`apiKey should not be blank`) as the failure mode for a wrong field name, not `400`. (The old expectation — flag the stale `api_key` in the public Swagger — is obsolete since the docs were corrected on 2026-09-03.) | ✅ covered by `v2/authentication.md` |
| 16 | "Does the Qapla' v2 API return the same `{result: OK/KO}` envelope as v1?" | **Negative control** — NO; v2 uses real **HTTP status codes** + **RFC 7807** error bodies, not the v1 envelope. Should correct, not confirm. | ✅ guarded by `v2/overview.md` |
| 17 | "On the Qapla' v2 API, which courier is fastest to postal code 20100?" | `POST /v2/couriers/delivery-times` with `destCap`, optional `couriers`/`weightKg`/`originCap`; explains `best` + fastest-first `ranking` (default `detail: "summary"`), lead time as the ranking metric. Scope `delivery-times:read`. | ✅ covered by `v2/couriers.md` |
| 18 | "I want to pick the best v2 courier overall, not just the fastest one, for a lane — what do I call?" | `POST /v2/couriers/efficiency-index`; explains the 0–100 index blending `scoreSpeed`/`scoreConsistency`/`scoreReliability` at 40/20/40, best-first `ranking`, `insufficient_data` couriers appended with null rank. Scope `efficiency-index:read`. | ✅ covered by `v2/couriers.md` |
| 19 | "A Qapla' v2 shipment is stuck in giacenza (held in depot) — how do I ask the courier to redeliver it to a different address?" | `POST /v2/shipments/{id}/stock-release` with `action: "redeliver_new_address"` and a required `address` object; scope `shipments:write`; explains `courierOutcome` (`ok`/`error` sync for GLS/TNT, `pending` deferred for BRT) vs. the always-`"sent"` `status`. | ✅ covered by `v2/stock-release.md` |
| 20 | "I poll the Qapla' v2 API for shipments updated since my last sync, and I keep my cursor in UTC. Is that right?" | ⚠️ **Negative control, silent-failure class** — NO. `updatedAfter` is interpreted in `Europe/Rome`, so a UTC cursor **skips shipments** in the offset window with **no error**. Must warn and tell you to send the cursor in `Europe/Rome` (or overlap the window), not confirm the approach. | ✅ covered by `v2/overview.md` + `v2/sandbox.md` |
| 21 | "What timezone and format are timestamps in the Qapla' v2 API?" | **Not uniformly UTC, and no endpoint emits a literal `Z`.** `parcels`/`orders` are ATOM with an explicit `+00:00`; **shipment tracking** (`statusDate`, `statusUpdatedAt`, `history[].date`) and **sandbox** are `"Y-m-d H:i:s"` with **no offset**, in `Europe/Rome`. Should not answer a flat "UTC". | ✅ covered by `v2/overview.md` + `migration.md` + `versioning.md` |
| 22 | "My Qapla' v2 sandbox client reads `string_value` from the response and it just stopped working. What broke?" | **Nothing broke on your side by accident** — `qore/api` 2.21.10 made sandbox responses camelCase (`stringValue`, `createdAt`), a deliberate **breaking change**; rename the fields. Should not suggest the API is malfunctioning or that snake_case is still correct. | ✅ covered by `v2/sandbox.md` |
| 23 | "What's the rate limit on the Qapla' v2 API, and what do I get when I exceed it?" | Token bucket **300 capacity, refill 150/min** (defaults since `qore/api` v2.20.0); the channel's real values come back in the token response's `rate_limit`; over limit → **`429`** with `X-RateLimit-*` headers. ⚠️ Must **not** quote the v1.x bucket (120 capacity, 2/sec) — that is a separate limiter. | ✅ covered by `v2/overview.md` + `v2/authentication.md` |
| 24 | "Is `POST /v2/orders` in Qapla's public Swagger yet, or do I have to wait for it?" | It **is** published in the public spec — it is simply not written up in depth in this pack; build against <https://api.qapla.dev/v2/>. Should not say "not yet published" / "still in flight", which was true only of a stale 2.14.0 snapshot. | ✅ covered by `v2/endpoints.md` + `versioning.md` |
| 25 | "The Qapla' v2 Swagger reports version 2.21.9 — so the camelCase sandbox change isn't live yet, right?" | ⚠️ **Negative control** — the inference is invalid. The published snapshot's `info.version` is whatever `APP_VERSION` was when the dump ran and does **not** identify the contracts inside it (that snapshot already carries the camelCase schemas). Read the schemas, or ask the live `GET /v2/version`. Should not confirm the premise. | ✅ covered by `versioning.md` |

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

### 2026-09-03 (third pass) — 25/25 on the installed 1.4.2

First run after `evaluation/` stopped being installed (1.4.2). Method unchanged:
one fresh Sonnet agent per scenario, only the user prompt, self-reported sources.

**Finding 2 is confirmed resolved.** Every agent reported reading from
`~/.claude/skills/qapla-api/`, and not one cited `evaluation/` — it is not there
to cite. The #5 agent, which last time found and quoted its own expected answer,
this time reached its refusal from `versioning.md` and `endpoints.md` alone.

**The 1.4.2 `updatedAfter` fix is visibly working.** #20 now cites
`v2/sandbox.md` lines 59–66 alongside `v2/overview.md` and offers the remedy in
the words the fix added ("convert your cursor … or overlap the window and
de-duplicate"). #21 volunteered the same caveat unprompted.

Spot-checked back against the references: `parcels[]` accepting 1–100 items
(#13), the fewer-than-20-deliveries suppression behind `insufficient_data`
(#18), `P46` as an illustrative `courierService` (#2), and
`X-RateLimit-Retry-After` actually being the header the bundled client reads
(#23) — all confirmed.

#### ⚠️ Finding 3 — git history is a second, unfixable answer key

The #25 agent ran `git log` / `git show` on the repo and rebuilt its answer partly
from commit messages. It found `d2bd000`, whose message states that the spec's
`info.version` "renders from `composer.json`" and is "a staleness floor, not an
exact match" — and presented that to the user as current documented fact,
attributed to "`references/v2/sandbox.md`'s git history".

**That claim is false and was retracted the same day in `b3330f8`**, whose subject
is literally "fix: info.version comes from APP_VERSION, not composer.json". The
agent read the wrong three commits and missed the correction.

Its bottom line was still right — it rejected the premise and pointed at the live
`GET /v2/version` — so the scenario passes on what it tests. But a stricter grader
would call it a partial: the reasoning handed the user a mechanism the shipped
docs explicitly contradict.

Unlike the `evaluation/` leak this cannot be fixed by excluding a path: history is
immutable by design, agents run with the repo in their working directory, and a
superseded commit message reads exactly like documentation. What can be done:
- When a commit asserts a *mechanism* and that mechanism later proves wrong, the
  correcting commit should name the wrong one explicitly. `b3330f8` does; it just
  was not the one sampled.
- Keep the correct explanation prominent in the shipped reference, so an agent has
  no reason to go digging. `versioning.md` now carries it.
- Treat any eval answer that cites commit messages as suspect on facts, and check
  it against the current file.

#### ⚠️ Finding 4 — an eval agent wrote into the repo

The #8 agent did not just describe a webhook receiver, it created
`scripts/qapla_webhook_receiver.py` (316 lines) in the working repo — inside
`scripts/`, which *is* part of the exported tree, so an unnoticed commit would
have shipped unreviewed code to every install. It was untracked and has been
moved out.

The scenarios are knowledge checks; none of them asks for a file. Either run them
read-only, or check `git status` after every run. Worth adding the latter to the
method above regardless.


### 2026-09-03 (second pass) — 6 new scenarios (#20–25), 6/6, and one content gap

Added the scenarios the previous run showed were missing: one per correction
shipped in 1.4.1. Method as before — one fresh Sonnet agent per scenario, only
the user prompt, self-reported sources. **The scenarios were written to the repo
but deliberately not synced into the installed skill before running**, so this
time the agents could not read their own expectations (finding 2 of the previous
entry — since made structural: `evaluation/` is `export-ignore`d and no longer
installed at all).

| # | Covers | Result |
|---|---|---|
| 20 | `updatedAfter` read in `Europe/Rome` (silent data loss) | PASS — rejected the UTC cursor, quoted the silent-loss consequence, gave the fix, and correctly separated `parcels` (safe in UTC) from shipments/sandbox |
| 21 | v2 timestamps are mixed, never a literal `Z` | PASS — per-resource table, ATOM `+00:00` vs `"Y-m-d H:i:s"` in `Europe/Rome`, and volunteered the `updatedAfter` caveat unprompted |
| 22 | sandbox casing is a deliberate breaking change | PASS — named 2.21.10, gave the full rename map, explicitly said nothing broke on the caller's side |
| 23 | v2 rate limit 300 / 150-per-minute | PASS — right numbers, told the caller the token response is authoritative over the defaults, and distinguished the v1 bucket |
| 24 | second-tier resources are published, not "in flight" | PASS — published in the spec, not detailed here, don't hardcode |
| 25 | the spec's `info.version` proves nothing about contents | PASS — rejected the premise, said the snapshot already carries the 2.21.10 schemas, pointed at the live `GET /v2/version` |

**Content gap found — `updatedAfter` had no warning where it is actually
documented.** Writing #20 meant checking where the caveat lives, and it lived in
`v2/overview.md` alone: the query-param table in `v2/sandbox.md` — the thing you
read while calling `GET /v2/sandbox` — still said "ISO 8601 datetime filter" with
no mention of the zone. The 1.4.1 changelog's "now called out wherever the filter
appears" was therefore overstated. Fixed in `v2/sandbox.md`, with the correction
recorded under `[Unreleased]`.

Note this gap was found by **authoring** the scenario, not by running it: #20
passed both before and after the fix, because the agent found the caveat in
`overview.md`. A scenario that asks specifically "what does the `GET /v2/sandbox`
query-param table say about `updatedAfter`" would have failed — worth remembering
that a passing suite of natural-language prompts does not prove each individual
file is self-sufficient.

Also noted: the #25 agent read the reference files from the **repo** rather than
the installed copy (identical content at the time, so the result stands, but the
sandbox for these runs is not hermetic — agents run with the repo in their working
directory and can reach it).


### 2026-09-03 — 19/19 passed, but the suite tested none of what 1.4.1 fixed

Full suite re-run after release 1.4.1, against the **installed copy**
(`~/.claude/skills/qapla-api`, synced from `git archive v1.4.1`). Method: one
fresh `general-purpose` agent per scenario, Sonnet, given **only** the user
prompt plus a request to self-report which skill activated and which files it
opened — no expected answer in the prompt. 19 agents, 19 passes.

Spot-checked against the references rather than taken on trust: the
`stock-release` required-address fields (#19), the absence of a `detail` param on
`efficiency-index` (#18), `ZIP`/`isTrackingNumber` in `pushShipment` (#1) and
`recipient.zipCode`/`province` in `getQuotes` (#3) all match what the agents
said.

| # | Triggered | Result |
|---|---|---|
| 1 | yes | PASS — `apiKey` + `pushShipment[]`, `courier: "UPS"`, per-item result check, `isTrackingNumber` explained |
| 2 | yes | PASS — `getPudos` (1.2) then `createLabel` then `confirmLabel`, `"sandbox": true`, PUDO block; flagged that GLS service codes are not enumerated |
| 3 | yes | PASS — `x-api-key` **header**, `recipient{}`, `amountShipment` as string, `x-sandbox`; asked for the missing street/dimensions instead of inventing them |
| 4 | yes | PASS — `apiKey` in body, Control Panel path, `getQuotes` header exception, and picked up the new `422` failure mode |
| 5 | yes | PASS — refused the invented `/v3/` bulk-refund endpoint (but see finding 2) |
| 6 | yes | PASS — v1 bucket: 120 capacity, 2/sec, batch cost = N, backoff, ban warning |
| 7 | **no — correct** | PASS — negative control; the skill did not activate on a pure PEP 8 request |
| 8 | yes | PASS — verifies `apiKey`, replies `{"result":"OK"}` fast, branches on numeric `qaplaStatusID` (coerced from string), dedups, notes 3 attempts + 100-failure auto-disable, handles all three payload shapes |
| 9 | yes | PASS — id `99`; branch on the canonical id, not the carrier label |
| 10 | yes | PASS — `1.2` |
| 11 | yes | PASS — same key, exchanged for a JWT; Bearer thereafter |
| 12 | yes | PASS — corrected it: `IN TRANSITO` is `3`, `30` is not a defined id |
| 13 | yes | PASS — >10 gives `202` + poll `GET /v2/jobs/{jobId}`; `409` on duplicate order |
| 14 | yes | PASS — `403` = authenticated but missing scope/product; listed the corrected `400`/`401`/`403`/`422`/`429` table |
| 15 | yes | PASS — `apiKey`, and `422` as the failure mode (the updated expectation) |
| 16 | yes | PASS — rejected the v1 envelope |
| 17 | yes | PASS — `POST /v2/couriers/delivery-times`, `destCap`, scope; and volunteered that the sample response is documentation data, not a live answer. Did not mention the `detail` param |
| 18 | yes | PASS — `efficiency-index`, 40/20/40 blend, `insufficient_data` with `rank: null` |
| 19 | yes | PASS — `redeliver_new_address` + required `address`, scope `shipments:write`, `status: "sent"` vs the real `courierOutcome` |

**Finding 1 — the suite does not cover anything 1.4.1 corrected.** Grepping this
file for `updatedAfter`, `Europe/Rome`, `statusUpdatedAt`, the sandbox casing and
the v2 rate-limit numbers returns zero hits on all five. Every one of the six
corrections in 1.4.1 landed in an area no scenario exercises, which is why the
drift survived four releases and was found by a customer instead. 19/19 therefore
means "nothing that was already tested regressed", not "the pack is accurate".
The highest-value gap is `updatedAfter`: it fails silently, so only a scenario
that asks for incremental polling would catch a regression.

**Finding 2 — this file ships inside the installed skill, so it is a readable
answer key.** The #5 agent opened `evaluation/scenarios.md`, found its own prompt
listed as an anti-hallucination test with the expected refusal, and said so in its
answer. Its refusal was independently well-founded, so the pass stands, but the
negative controls (#5, #7, #12, #16) cannot be called clean while the expected
behaviour is one grep away.

> **Resolved (2026-09-03).** `evaluation/` is now `export-ignore` in
> `.gitattributes`, so `git archive` — the documented install path in the README
> — leaves it out, and the installed skill no longer carries it. Runs from
> 2026-09-03 (second pass) onward are clean by construction rather than by
> remembering to sync in the right order. **When re-running, install with
> `git archive`, not `cp -r`**, or the answer key comes back.

**Not done this run:** the three-model matrix (Haiku/Sonnet/Opus) this file asks
for. Sonnet only.

### 2026-07-07 — 3/3 new v2 scenarios passed (#17–19)

After documenting the three new v2 stable endpoints (`v2/couriers.md`,
`v2/stock-release.md`, release 1.4.0), the 3 new scenarios were run with the same
method — one fresh `general-purpose` agent, answering all three prompts in
sequence, installed skill synced from the repo first, self-reporting skill
trigger + references opened per prompt.

| # | Scenario | Triggered | Reference(s) opened | Result |
|---|---|---|---|---|
| 17 | fastest v2 courier to a CAP | ✅ qapla-api | `v2/overview.md`, `v2/endpoints.md`, `v2/couriers.md` | ✅ PASS — `POST /v2/couriers/delivery-times`, `destCap` required, scope `delivery-times:read`, `best` + fastest-first `ranking` (summary default) |
| 18 | best overall v2 courier (not just fastest) | ✅ qapla-api | `v2/couriers.md` | ✅ PASS — `POST /v2/couriers/efficiency-index`, same request shape, scope `efficiency-index:read`, 0–100 `efficiencyIndex` = 40/20/40 blend of scoreSpeed/scoreConsistency/scoreReliability, best-first ranking |
| 19 | redeliver a v2 shipment held in giacenza to a new address | ✅ qapla-api | `v2/stock-release.md` | ✅ PASS — `POST /v2/shipments/{id}/stock-release`, `action: "redeliver_new_address"` + required `address`, scope `shipments:write`, `status: "sent"` always with real result in `courierOutcome` |

**No content bug found** — all three answers matched the references exactly on
endpoint path, required fields, scope, and response shape.

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
