# ADR 0004: Repo-Backed AI Operating Model

- Status: Accepted
- Date: 2026-04-17

## Context

The project now uses a war-room operating layer with:

- `AGENTS.md`
- `CLAUDE.md`
- `.codex/`
- `.agents/skills/`
- `ai/core/`
- `ai/war-room/`

New AI sessions cannot rely on prior chat memory alone. Durable continuity must live in the repo.

## Decision

Use repo-backed continuity as the memory model. New sessions recover project state from:

- `docs/context/`
- `docs/planning/`
- ADRs
- architecture/workflow/testing docs

The main thread uses one commander voice. Specialists are activated only when they improve quality or confidence.

## Why

- It reduces context drift across sessions.
- It gives humans and tools the same source of truth.
- It keeps planning, product, and engineering context durable.
- It aligns with the quality-first war-room operating contract.

## Consequences

- Handoff docs must stay current.
- Major architectural and product decisions should be captured in ADRs.
- New sessions should bootstrap from repo docs before doing substantive work.

## Non-goals

- This does not guarantee literal zero-loss continuity.
- This does not require permanent always-on subagent fan-out.
