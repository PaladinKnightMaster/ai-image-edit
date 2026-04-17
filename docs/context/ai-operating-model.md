# AI Operating Model

## Purpose
This repository uses a project-local war-room operating layer so different AI tools can recover the same project context and work style.

## Canonical Contract
- `AGENTS.md` is the canonical cross-tool operating contract.
- `CLAUDE.md` is a thin Claude-specific shim.
- `.codex/` contains Codex-specific agent configuration.
- `.agents/skills/` contains project-local workflow skills.

## Main Rules
- one commander voice in the main thread
- minimum useful specialist set
- quality-first, evidence-first recommendations
- repo-backed continuity

## Continuity Model
New sessions do not inherit true persistent memory.
They recover the project plot by reading:
1. `AGENTS.md`
2. tool shim/config
3. `ai/core/*`
4. `ai/war-room/*`
5. `docs/context/*`
6. active planning docs in `docs/planning/*`

## When to update docs
Update `docs/context/` when:
- product direction changes
- blockers change
- active assumptions change
- the recommended next action changes

Update `docs/planning/` when:
- sprint scope changes
- roadmap phases change
- release criteria change
