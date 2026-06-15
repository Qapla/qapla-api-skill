<!-- BEGIN qapla-api -->
## Qapla' Public API (v1.3)

When the task involves integrating with or answering questions about the
**Qapla' shipping & tracking REST API** (push shipments or raw orders, generate
and confirm carrier labels, track parcels, get multi-carrier quotes, look up
pickup points/PUDO, verify addresses, list couriers and channels), use the
knowledge in this repo's `references/` directory.

**Start here:** read [`references/overview.md`](references/overview.md) — it is
the canonical orientation (domain model + "which endpoint do I need?" decision
rule). Then `references/conventions.md` and `references/authentication.md` apply
to every call, and the per-endpoint deep-dives live in
`references/{pushshipment,pushorder,createlabel,getquotes,getpudos}.md` with the
full catalog in `references/endpoints.md`. Runnable sample payloads are in
`references/examples/`; a dependency-free reference client is
`scripts/qapla_client.py`.

Core facts (the rest is in `references/overview.md`):

| Topic | Value |
|---|---|
| **Base URL** | `https://api.qapla.it/<version>/<endpoint>` (e.g. `https://api.qapla.it/1.3/pushShipment`) |
| **Auth** | Per-**channel** API Key, sent as `apiKey` in the JSON body. Treat it as a secret; never hard-code it. |
| **Response envelope** | `{"<endpointName>": {"result": "OK"\|"KO", "error": null\|"<message>"}}`. For batch endpoints also check the per-item `result`. |
| **Rate limit** | Token bucket: 120 capacity, +2/sec. A batch of N items costs N tokens. Over limit → HTTP `429` (back off and retry). |
| **Sandbox** | Pass `"sandbox": true` in the body where supported (e.g. `createLabel`). Exception: `getQuotes` uses an `x-sandbox` header. |
| **Versions** | `1.3` is production. `getPudos` lives under `/1.2/`. A newer **v2** (different auth) at `/v2/` is out of scope. |

**Guardrails:** this documents the **public** API only — do not invent
endpoints, parameters, or fields. The live docs at <https://api.qapla.dev/1.3/>
are the source of truth; if anything here drifts, trust them.
<!-- END qapla-api -->
