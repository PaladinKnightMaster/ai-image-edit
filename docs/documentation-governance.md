# Documentation Governance

Status: Active
Last updated: 2026-07-16
Owner: Docs Architect

## Purpose

Keep repository documentation authoritative, easy to recover, and small enough to maintain. This structure is
an adapted docs-as-code model: live context, decisions, architecture, plans, operational guides, and historical
evidence have different responsibilities.

## Document Classes

### Live context

Location: `docs/context/`

- `project-brief.md`: durable product and constraint summary
- `current-state.md`: current implementation truth, blockers, and active work
- `session-handoff.md`: concise next-session recovery
- `decision-log.md`: chronological index of material decisions

Live context must not become a sprint activity log.

### Decisions

Location: `docs/adr/`

Use an ADR when a choice changes architecture, product direction, validation policy, dependencies, or future
implementation constraints. Accepted ADRs are immutable except for corrections and status changes; superseding
decisions get a new ADR.

### Architecture and reference

Locations: `docs/architecture/`, `docs/models/`, `docs/design/`, and `docs/workflows/`

These documents describe current behavior first and target behavior second. Label proposed components and states
clearly so readers do not confuse plans with implemented code.

### Plans and gates

Location: `docs/planning/`

Only one sprint outline should be active. Closed sprint outlines and closeout audits are historical evidence even
when they remain in the same folder for link stability.

### Operational guides and evidence

Locations: `docs/setup/`, `docs/testing/`, and `docs/engines/`

Runbooks contain exact prerequisites, commands, pass criteria, failure handling, and evidence fields. A prepared
runbook is not execution evidence. Result logs must state the actual environment and commit.

## Required Metadata

Material Markdown documents should include, near the top where applicable:

- status
- last-updated or decision date
- owner
- related sprint, ticket, ADR, or plan

Allowed lifecycle terms:

- `Draft`
- `Active`
- `Planned`
- `Prepared`
- `Locked`
- `Accepted`
- `Blocked`
- `Closed`
- `Superseded`
- `Historical`

Use qualifiers after a semicolon when needed. Do not use `complete` when only preparation is complete.

## Source-Of-Truth Rules

- current behavior: code plus `docs/context/current-state.md`
- product constraints: `docs/context/project-brief.md` plus accepted ADRs
- current work: active sprint outline
- release gates: current release checklist and evidence logs
- architecture decisions: accepted ADRs
- historical completion: sprint closeout audits and recorded test evidence

When documents conflict, update the stale document rather than relying on an undocumented priority rule.

## Size And Duplication Rules

- keep `session-handoff.md` under 100 lines where practical
- keep `current-state.md` focused on current truth; link to closeout audits instead of repeating completed tickets
- do not copy long evidence histories into context docs
- do not repeat commands across many files; identify one canonical runbook and link to it
- preserve closed sprint evidence, but remove it from active-doc lists

## Review Cadence

Review the live set:

- at sprint start and close
- after accepted ADRs
- after release-gate changes
- when code makes an architecture statement false

The review must check:

- exactly one active sprint
- current-state and handoff agreement
- broken local links
- stale `Active`, `Draft`, or `Prepared` statuses
- architecture claims against current code
- result logs that accidentally imply unexecuted validation

## Archive Policy

Historical sprint files remain in `docs/planning/` for now to preserve stable links. Superseded live context,
architecture, design, workflow, roadmap, and testing snapshots may move to `docs/archive/` when the canonical path
is recreated in the same change. Archived files are evidence only and must not be linked as current authority.

A broader physical migration of closed sprint documents should happen only as a dedicated mechanical change with
a link checker and no content rewrite.
