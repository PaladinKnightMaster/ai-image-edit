# Sprint 4 Outline

Status: Active
Sprint name: Sprint 4 - Beta Scope Lock and Acceptance Validation
Duration: 2 weeks
Last updated: 2026-06-11
Parent plan: `docs/planning/mvp-war-room-plan.md`
Depends on:

- `docs/planning/sprint-3-closeout-audit.md`
- `docs/planning/beta-readiness-checklist.md`
- `docs/testing/preset-quality-review-worksheet.md`

Sprint owner: Tech Lead

## 1. Sprint Goal

Turn Sprint 3 evidence into a clear beta decision.

Sprint 4 should not add new editing surfaces. It should lock the beta scope, complete or prepare the
off-box Qwen acceptance lane, verify setup/release readiness, and make the tester handoff honest enough
for a real closed beta decision.

## 2. Recommended Verdict Entering Sprint 4

The best path is not to broaden the product. The best path is to choose one of two beta tracks:

1. Draft-lane closed beta: proceed only if testers are explicitly told FLUX is local draft evidence and
   Qwen acceptance is incomplete.
2. Qwen-acceptance beta: wait for off-box `qwen-image-edit-2511` benchmark evidence before inviting testers.

Sprint 4 scope decision:

- WR4-001 is locked in `docs/planning/beta-scope-decision.md`.
- Proceed with draft-lane closed beta preparation only.
- Final Qwen-acceptance beta remains no-go until off-box `qwen-image-edit-2511` evidence exists.

## 3. In Scope

- final beta scope decision
- off-box Qwen validation packet and result logging
- clean-machine setup/run verification
- beta tester handoff finalization
- release checklist and risk register
- decision on whether the live WR3-007 pending output stays as fixture or is revealed

## 4. Out Of Scope

- new engine families
- hosted GPU implementation
- masking or region editing
- batch editing
- Android work
- broad preset expansion
- advanced reference weighting UI

## 5. Ticket Outline

### WR4-001 - Lock beta scope

- Owner: Tech Lead + Product
- Priority: P0
- Outcome: decide draft-lane beta, Qwen-acceptance beta, or another hardening sprint
- Progress: complete. Scope is locked to draft-lane beta preparation; final Qwen-acceptance beta remains no-go.

### WR4-002 - Prepare off-box Qwen acceptance packet

- Owner: AI/ML + Infra
- Priority: P0
- Outcome: exact commands, fixture paths, expected artifacts, and review worksheet are ready for stronger hardware
- Progress: complete. Packet is prepared in `docs/testing/off-box-qwen-acceptance-packet.md`; execution
  remains approval-gated and off-box.

### WR4-003 - Run or record off-box Qwen acceptance

- Owner: AI/ML
- Priority: P0 if Qwen beta is required
- Outcome: acceptance record exists, or beta explicitly excludes Qwen acceptance

### WR4-004 - Clean-machine release smoke

- Owner: DevOps + Backend + Frontend
- Priority: P0
- Outcome: startup, `/health`, `/api/models`, frontend build, and launch instructions pass on the target beta environment
- Progress: prepared and locally validated. Non-model release smoke runbook is in
  `docs/testing/clean-machine-release-smoke.md` and aggregate command is `scripts/release_smoke.ps1`.
  Clean-machine installation guide is in `docs/setup/windows-draft-lane-beta-install.md`.
  Target clean-machine installation and smoke are still required before tester handoff.

### WR4-005 - Finalize beta tester handoff

- Owner: Product + Tech Lead
- Priority: P0
- Outcome: tester-facing limitations and feedback prompts are ready and aligned with the chosen beta scope
- Progress: complete. Tester-facing handoff is owner-reviewed in
  `docs/testing/draft-lane-beta-tester-handoff.md`, backed by
  `docs/testing/beta-tester-limitations-handoff.md`. Tester invite remains gated by target clean-machine smoke.

### WR4-006 - Decide WR3-007 pending fixture handling

- Owner: Tech Lead
- Priority: P1
- Outcome: keep job `dfc36b9bde8d4ee7b111c5196d8ecb24` pending as a fixture, or reveal it intentionally for live reuse
- Progress: complete. Decision is locked in `docs/planning/wr3-007-fixture-decision.md`: keep the live
  job pending as a benchmark fixture and use scratch DB copies for routine reveal/reuse validation.

### WR4-007 - Release checklist and risk register

- Owner: Tech Lead + DevOps
- Priority: P1
- Outcome: release gate checklist includes known blockers, test commands, evidence artifacts, and owner assignments
- Progress: complete and reviewable in `docs/planning/sprint-4-release-checklist-and-risk-register.md`.
  Draft-lane beta preparation remains conditional on target clean-machine smoke and owner-reviewed tester copy.

## 6. Recommended Execution Order

1. Run or schedule target clean-machine release smoke before any tester handoff
2. Owner-review the draft-lane tester handoff copy
3. Run or record off-box Qwen acceptance only if Qwen-acceptance beta becomes required

## 7. Exit Criteria

Sprint 4 is complete when:

- the beta scope is explicit
- Qwen acceptance is either recorded off-box or excluded from the beta scope in writing
- clean-machine setup/run checks pass or have owner-assigned blockers
- tester limitations are ready for use
- release checklist and risk register are reviewable
- no Sprint 4 work depends on a new engine or new editing surface

## 8. War Room Recommendation

Run Sprint 4 as a beta-decision sprint, not a feature sprint.

If the user wants speed, choose draft-lane closed beta prep and disclose the Qwen blocker.
If the user wants credibility, prioritize off-box Qwen acceptance before beta.
