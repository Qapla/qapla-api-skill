# Qapla' API — AI Agent Knowledge Pack

A portable **knowledge pack** that teaches an AI coding agent how to integrate
with and answer questions about the **Qapla' public REST API (v1.3)** —
shipments, raw orders, carrier labels, tracking, real-time quotes, pickup points
(PUDO), address checks, couriers, and channels.

It mirrors the official, public documentation at
<https://api.qapla.dev/1.3/> so the agent can work without network access, and
links back to the live docs as the source of truth.

The same content is exposed through several agent entrypoints — a Claude
**skill** (`SKILL.md`), a universal **`AGENTS.md`** (read by Codex, Gemini CLI,
Cursor, Copilot, Windsurf, Aider, Zed, Jules and 20+ tools), and a **Cursor
rule** (`.cursor/rules/qapla-api.mdc`). All of them point back to a single
source of truth in `references/overview.md`, so there is no duplicated content
to drift.

## What's inside

```
SKILL.md                     # Claude entrypoint (skill, with YAML frontmatter)
AGENTS.md                    # universal entrypoint (Codex, Gemini, Cursor, Copilot, …)
.cursor/rules/qapla-api.mdc  # Cursor entrypoint (agent-requested rule)
references/
  overview.md                # single source of truth: core facts, domain model, decision rule
  conventions.md             # base URL, response envelope, rate limiting, sandbox, dates
  authentication.md          # per-channel API Key
  endpoints.md               # full endpoint catalog
  pushshipment.md            # deep-dives for the main endpoints
  pushorder.md
  createlabel.md
  getquotes.md
  getpudos.md
  examples/                  # real request/response JSON samples from the docs
scripts/qapla_client.py      # dependency-free reference client
```

The three entrypoints are thin: they orient the agent and point into
`references/`. All shared knowledge lives under `references/` and `scripts/`, so
a documentation fix is made once.

## Installing

Whichever agent you use, the `references/` and `scripts/` folders must travel
with the entrypoint — they hold the actual knowledge.

### Claude Code

Copy the whole folder into your skills directory:

```bash
# project-level (this repo only)
mkdir -p .claude/skills && cp -r qapla-api .claude/skills/

# or user-level (all your projects)
mkdir -p ~/.claude/skills && cp -r qapla-api ~/.claude/skills/
```

The skill loads automatically when a task matches its `description`. Keep
`SKILL.md` at the skill root (valid YAML frontmatter: `name`, `description`) with
the supporting files under `references/`.

### AGENTS.md (Codex, Gemini CLI, Cursor, Copilot, Windsurf, Aider, Zed, Jules…)

[`AGENTS.md`](AGENTS.md) is the universal entrypoint. Drop this repo's content
into the project where you integrate Qapla' and either:

- **Merge the snippet** — copy the block between the
  `<!-- BEGIN qapla-api -->` / `<!-- END qapla-api -->` markers into your
  project's existing root `AGENTS.md`, or
- **Use the file as-is** if the project has no `AGENTS.md` yet.

Keep `references/` and `scripts/` at the path the snippet references (repo root
by default) so the relative links resolve.

### Cursor

Copy the rule (and the knowledge it points to) into your project:

```bash
mkdir -p .cursor/rules && cp .cursor/rules/qapla-api.mdc .cursor/rules/
cp -r references scripts .   # the rule links into these
```

The rule is *agent-requested* (`alwaysApply: false`, no `globs`), so Cursor
pulls it in on demand when your prompt matches its `description` — the closest
analog to a Claude skill. The `.mdc` extension and frontmatter are required;
a plain `.md` in `.cursor/rules` is ignored.

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
