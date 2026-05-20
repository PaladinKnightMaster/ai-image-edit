# Sprint 3 Outline

Status: Active
Sprint name: Sprint 3 - Reliability, Iteration, Quality Review, and Beta Readiness
Duration: 2 weeks
Last updated: 2026-05-20
Parent plan: `docs/planning/mvp-war-room-plan.md`
Depends on:

- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`
- `docs/planning/sprint-2-closeout-audit.md`

Sprint owner: Tech Lead

## 1. Sprint Goal

Harden the edit-first MVP so it is credible for closed beta planning.

Sprint 2 proved the local draft-lane product flow. Sprint 3 must now make the result loop,
manual-review path, recovery behavior, and quality-review process trustworthy. The goal is not to add
new editor surfaces. The goal is to make the current product loop dependable enough that a beta
decision can be made from evidence.

## 2. Definition Of Done

Sprint 3 is complete only when all of the following are true:

- result iteration is clear: `edit -> reveal if needed -> compare -> refine -> download/reuse`
- pending-review reveal behavior has lightweight live/API validation without launching a new model
- reference-guided editing is understandable and explicitly optional
- key job/recovery states are documented and validated with cheap checks
- preset quality review has a recorded path that separates local FLUX draft evidence from Qwen signoff
- beta readiness criteria and known limitations are documented and reviewable

## 2.1 Current Progress

- WR3-001 / WR3-003 have non-model backend coverage for reveal transitions, API reveal responses,
  pending-output cleanup, and queued/running recovery.
- WR3-002 has live browser evidence on a scratch copy of `data/app.benchmark-review.db` for Recent runs
  reveal/reuse/download, composer output-library reuse, and landing-state output-library reuse.
- WR3-008 has started with `docs/planning/beta-readiness-checklist.md`, which records the current
  not-beta-ready verdict, closed-beta gates, evidence tiers, and known limitations.
- WR3-006 has started with `docs/testing/preset-quality-review-worksheet.md`, which maps all Sprint 2
  presets to evidence lanes, required cases, current statuses, watchouts, and review-log fields.
- The beta tester limitations handoff now exists at `docs/testing/beta-tester-limitations-handoff.md`
  to keep future tester messaging aligned with the readiness gate and current runtime constraints.
- No new edit job or model run was submitted for this Sprint 3 reliability and UI-hardening evidence.

## 3. Inherited Constraints

- Local `qwen-image-edit-2511` benchmark/signoff remains blocked on this machine by a reproducible native
  process exit (`0xC0000005`) during CPU-only execution.
- `flux2-klein-9b-gguf` is the local draft edit lane and can support product-flow evidence.
- FLUX draft results are not final acceptance evidence for the intended Qwen edit lane.
- Any heavy model run still requires explicit user notification and approval before execution.
- Do not broaden into new engine families, masking, batch editing, Android, or hosted GPU work in this sprint.

## 4. Workstreams

### Workstream A: Result Iteration And Reveal Hardening

Objective: make the post-output loop trustworthy without requiring users to understand backend state.

Focus:

- validate pending-review reveal from Recent runs and timeline messages
- ensure revealed outputs become reusable in edit/history flows
- keep unrevealed pending outputs out of normal reuse
- make `Edit this`, compare, and download actions remain prominent after reveal

### Workstream B: Job Reliability And Recovery

Objective: reduce beta risk from long CPU jobs, interrupted jobs, and confusing state transitions.

Focus:

- cheap checks for `/api/jobs`, `/api/runs`, reveal, deletion, and cleanup behavior
- stale `queued` / `running` recovery behavior after restart
- clearer status/error language where current copy is ambiguous
- storage cleanup expectations for output and pending-output images

### Workstream C: Preset Quality Review

Objective: create an evidence-based preset review loop without pretending local hardware can complete all signoff.

Focus:

- review six portrait presets against benchmark-pack mapping
- use FLUX draft evidence only where local runtime permits and user approves the run
- keep Qwen edit signoff as an off-box validation lane
- record preset watchouts and tuning decisions before changing defaults

### Workstream D: Reference-Guided UX Polish

Objective: make optional reference-image use clear enough for beta users.

Focus:

- clarify base vs reference expectations
- keep single-image edit path primary
- document supported reference use cases: lighting, style, angle guidance
- avoid advanced reference weighting UI in Sprint 3

### Workstream E: Beta Readiness

Objective: define the beta gate in concrete, reviewable terms.

Focus:

- closed-beta checklist
- known limitations
- local hardware/runtime expectations
- off-box validation requirement for Qwen edit signoff

## 5. Ticket Outline

### WR3-001 - Validate pending-review reveal path

- Owner: Frontend + Backend
- Priority: P0
- Outcome: existing pending-review outputs can be revealed and then reused without launching a new model

### WR3-002 - Harden result iteration loop

- Owner: Frontend
- Priority: P0
- Outcome: users can move from output to compare, refine, download, or reuse without losing context

### WR3-003 - Add cheap job/recovery API checks

- Owner: Backend
- Priority: P0
- Outcome: job/runs/reveal/delete/recovery behavior has non-model validation coverage where feasible

### WR3-004 - Improve status and error communication

- Owner: Backend + Frontend
- Priority: P1
- Outcome: long waits, observer timeouts, pending review, and failures are distinguishable to users

### WR3-005 - Polish reference-guided UX copy

- Owner: Frontend + UI/UX
- Priority: P1
- Outcome: users understand that reference images are optional guidance, not the primary identity source

### WR3-006 - Create preset quality review worksheet

- Owner: AI/ML + Product
- Priority: P0
- Outcome: preset review can proceed with clear criteria, runtime lane labels, and signoff boundaries

### WR3-007 - Run approval-gated draft preset review where feasible

- Owner: AI/ML
- Priority: P1
- Outcome: any local FLUX draft run is explicitly approved and logged as draft evidence only

### WR3-008 - Add beta readiness checklist and limitations doc

- Owner: Tech Lead + Product
- Priority: P0
- Outcome: closed-beta entry criteria, known limitations, and off-box validation needs are explicit

## 6. Recommended Execution Order

1. WR3-001 Validate pending-review reveal path
2. WR3-003 Add cheap job/recovery API checks
3. WR3-002 Harden result iteration loop
4. WR3-008 Add beta readiness checklist and limitations doc
5. WR3-006 Create preset quality review worksheet
6. WR3-005 Polish reference-guided UX copy
7. WR3-004 Improve status and error communication
8. WR3-007 Run approval-gated draft preset review where feasible

This order intentionally starts with non-heavy reliability and evidence plumbing before any model-quality
run. It keeps the machine-safe Sprint 3 path moving while preserving the heavy-run approval rule.

## 7. First Step

Start with WR3-001 and WR3-003 together as one local-only reliability slice:

- inspect the existing `pending_review` run state in `data/app.db` or available API responses
- add or update non-model tests for reveal state transitions if the current backend test harness supports it
- verify that a pending output moves to `output_image_id`, clears `pending_output_image_id`, updates job status,
  and becomes visible in reusable run history
- do not submit a new edit job or run any model

## 8. Risks

### Risk 1: Sprint 3 drifts into new features

Mitigation:

- reject masking, batch editing, new engines, and hosted GPU work for this sprint
- prioritize reliability, iteration, review, and beta gates

### Risk 2: Preset quality is judged from insufficient evidence

Mitigation:

- separate FLUX draft evidence from Qwen signoff
- label runtime lane and hardware context in every review artifact
- require off-box Qwen edit validation before final acceptance

### Risk 3: CPU latency still feels like failure

Mitigation:

- preserve persisted job activity and observer-timeout semantics
- improve user-facing status copy where needed
- avoid fixed ETA promises on CPU-only inference

### Risk 4: `page.tsx` keeps growing

Mitigation:

- do not add major orchestration directly to `page.tsx`
- extract hooks or utilities for new reliability/reveal logic when implementation grows

## 9. Beta Readiness Criteria

Closed beta should not start until:

- Sprint 1 startup/runtime checks remain green
- Sprint 2 edit-first workflow remains intact
- reveal/reuse/recovery flows have cheap validation coverage
- preset quality review is recorded with lane-specific evidence
- Qwen edit signoff is completed off-box or explicitly marked as a beta blocker
- known limitations and CPU-only runtime expectations are documented

## 10. Expected Deliverables

- pending-review reveal validation
- job/recovery non-model checks
- improved result iteration loop
- preset quality review worksheet
- reference-guided UX polish
- beta readiness checklist
- known limitations document

## 11. Hand-off To Beta / Phase 4

After Sprint 3, choose one of:

- proceed to closed beta
- run one more hardening sprint
- delay beta and narrow scope further

The decision must be based on benchmark evidence, reveal/recovery reliability, and honest runtime
limitations, not only feature completeness.
