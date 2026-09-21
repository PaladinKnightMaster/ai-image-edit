# Documentation Realignment Audit

Status: Completed for the 2026-07-16 checkpoint
Last updated: 2026-07-16
Owner: Docs Architect + Reviewer

## Objective

Align the documentation with current code, the CPU-only operating constraint, the unavailable fresh-machine
constraint, and the durable-workflow strategy without deleting historical evidence.

## Findings And Disposition

| Finding | Severity | Disposition |
| --- | --- | --- |
| Frontend architecture said product mode was inferred, but explicit edit/create mode exists | High | Rewrite current frontend architecture. |
| Backend architecture said startup was blocked, but startup and smoke are fixed | High | Rewrite current backend architecture. |
| Roadmap immediate actions still pointed to Sprint 1 and Sprint 2 work | High | Replace with current phase and Sprint 5 direction. |
| `session-handoff.md` was a 272-line activity history | Medium | Replace with concise recovery context and links. |
| `current-state.md` repeated detailed closed Sprint 1-3 work | Medium | Reduce to current truth, evidence, blockers, and next action. |
| Test strategy understated existing backend job/reveal/recovery tests | Medium | Update implemented coverage and current gaps. |
| Clean-machine gate assumed a separate physical machine | High | Permit Windows Sandbox surrogate evidence while retaining physical-machine residual risk. |
| No durable decision covered CPU-only roadmap or Temporal/Saga use | High | Add ADR 0005 and ADR 0006. |
| Closed sprint outlines were mixed into active planning lists | Medium | Reclassify them as historical in the index and live context. |
| Documentation had no lifecycle or ownership policy | Medium | Add `docs/documentation-governance.md`. |
| Model license was being treated as a major selection constraint | Low | Record that private non-commercial use removes the commercial-selection gate while provenance remains required. |

## Structural Decision

Keep the existing domain folders. They already separate context, decisions, architecture, design, workflows,
models, planning, setup, testing, and engine reference effectively.

Do not move or delete closed sprint documents in this checkpoint. The higher-value correction is to make active
authority explicit and remove stale claims. Superseded live context, architecture, roadmap, design, workflow, and
test-strategy snapshots were moved under `docs/archive/` while their canonical paths were recreated. A future
archive migration may move closed sprint records after a link-safe mechanical plan exists.

## Authoritative Live Set After Realignment

- `docs/index.md`
- `docs/context/project-brief.md`
- `docs/context/current-state.md`
- `docs/context/session-handoff.md`
- `docs/planning/strategy-checkpoint.md`
- `docs/planning/sprint-4-outline.md` until isolated smoke evidence closes it
- `docs/planning/sprint-5-outline.md` as the planned next sprint
- `docs/planning/sprint-4-release-checklist-and-risk-register.md`
- ADRs 0001 through 0006

## Deferred Cleanup

- physical archive migration for closed sprint documents
- automated Markdown link and metadata linting
- README reduction after installation and contributor paths are consolidated
- removal of obsolete environment examples only after code-reference checks

These items are deferred because they do not block the CPU-first reliability plan and should not be mixed with
runtime implementation.
