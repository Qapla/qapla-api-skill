# Qapla' API — Claude Skill

A [Claude](https://claude.com/claude-code) **skill** that teaches an AI agent
how to integrate with and answer questions about the **Qapla' public REST API
(v1.3)** — shipments, raw orders, carrier labels, tracking, real-time quotes,
pickup points (PUDO), address checks, couriers, and channels.

It mirrors the official, public documentation at
<https://api.qapla.dev/1.3/> so the agent can work without network access, and
links back to the live docs as the source of truth.

## What's inside

```
SKILL.md                     # entry point: core facts, domain model, how-to
references/
  conventions.md             # base URL, response envelope, rate limiting, sandbox, dates
  authentication.md          # per-channel API Key
  endpoints.md               # full endpoint catalog
  pushshipment.md            # deep-dives for the main endpoints
  pushorder.md
  createlabel.md
  getquotes.md
  getpudos.md
  examples/                  # real request/response JSON samples from the docs
```

## Installing the skill

**Claude Code** — copy this folder into your skills directory:

```bash
# project-level (this repo only)
mkdir -p .claude/skills && cp -r qapla-api .claude/skills/

# or user-level (all your projects)
mkdir -p ~/.claude/skills && cp -r qapla-api ~/.claude/skills/
```

Then the skill loads automatically when a task matches its `description`
(integrating with the Qapla' API). You can also invoke it explicitly.

> The folder name must contain a `SKILL.md` with valid YAML frontmatter
> (`name`, `description`). Keep `SKILL.md` at the skill root and the supporting
> files under `references/`.

## Quick start (the 30-second version)

```bash
curl -X POST https://api.qapla.it/1.3/pushShipment \
  -H 'Content-Type: application/json' \
  -d '{
    "apiKey": "YOUR_CHANNEL_API_KEY",
    "pushShipment": [
      { "trackingNumber": "1Z999AA10123456784", "courier": "UPS",
        "email": "customer@example.com", "name": "Jane Doe" }
    ]
  }'
```

- **Base URL:** `https://api.qapla.it/<version>/<endpoint>`
- **Auth:** per-channel `apiKey` in the JSON body (Control Panel → Settings →
  Channels → Configure → Private API Key)
- **Response:** `{"pushShipment": {"result": "OK", "error": null, ...}}`
- **Rate limit:** token bucket, 120 capacity, +2/sec; a batch of N costs N

See `SKILL.md` and `references/` for everything else.

## Scope & disclaimer

- Covers the **public** API **v1.3** (with notes on `1.4` and a pointer to the
  newer **v2**). It deliberately documents only what is public at
  <https://api.qapla.dev>.
- This is documentation/tooling, not an official SDK. The live docs are
  authoritative; if anything here drifts, trust <https://api.qapla.dev>.

## License

[MIT](LICENSE).

## Links

- API docs: <https://api.qapla.dev/1.3/>
- Control Panel: <https://cp.qapla.it>
- Qapla': <https://www.qapla.it>
