# Claude Code Project Shim

`AGENTS.md` is the canonical operating contract for this repository.

Use `CLAUDE.md` only for Claude-specific behavior that does not conflict with `AGENTS.md`.

## Claude-specific rules

- Treat `AGENTS.md` as authoritative if any wording overlaps.
- Follow the same mode model: `solo`, `consult`, `war-room`.
- Keep one synthesized commander voice in the main thread.
- Read the repo-backed continuity docs before substantial work.
- Do not assume chat history is durable memory.

## Bootstrap order

1. `AGENTS.md`
2. `ai/core/*`
3. `ai/war-room/TEAM.md`
4. `ai/war-room/activation-matrix.md`
5. `ai/war-room/output-contracts.md`
6. `docs/context/project-brief.md`
7. `docs/context/current-state.md`
8. `docs/context/session-handoff.md`
9. active sprint doc in `docs/planning/`

## Expected cold-start reply

A new Claude session should begin by stating:
- recovered objective
- current phase or sprint
- key blockers
- active assumptions
- recommended next action
