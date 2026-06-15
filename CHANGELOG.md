# Changelog

All notable changes to this package are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note:** this version number is the **package** version (the agent knowledge
> pack), which is independent from the Qapla' **API** version it documents
> (currently public API `1.3`).

## [Unreleased]

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
