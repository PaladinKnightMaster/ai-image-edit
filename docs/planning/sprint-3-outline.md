# Sprint 3 Outline

Status: Draft
Sprint name: Sprint 3 - Editing Quality, Reliability, and Beta Readiness
Duration: 2 weeks
Last updated: 2026-04-17
Parent plan: `docs/planning/mvp-war-room-plan.md`
Depends on:

- `docs/planning/sprint-1-backlog.md`
- `docs/planning/sprint-2-outline.md`

Sprint owner: Tech Lead

## 1. Sprint Goal

Harden the edit-first MVP so it is credible for external beta use.

Sprint 3 is where the team stops proving workflow shape and starts proving product quality, reliability, and consistency. The goal is not broad new feature work. The goal is to make the current edit-first experience dependable enough for real users.

## 2. Definition of Done for Sprint 3

Sprint 3 is complete only when all of the following are true:

- portrait editing quality is directionally consistent across the benchmark pack
- reference-guided editing is understandable and usable
- key job/recovery flows are trustworthy enough for beta
- benchmark-driven preset tuning has been completed for the initial preset set
- beta readiness criteria are documented and reviewable

## 3. Scope Summary

### In Scope

- preset quality tuning
- reference-guided editing polish
- result iteration improvements
- backend reliability improvements that block beta confidence
- benchmark and acceptance review process
- beta readiness checklist

### Out of Scope

- new engine families
- Android/browser companion implementation
- hosted GPU implementation
- masking/editor tool expansion
- broad design-system or navigation rewrite

## 4. Product Outcomes

By the end of Sprint 3, a beta user should be able to:

1. upload a portrait
2. apply a preset or type an edit instruction
3. optionally add a reference image
4. run a draft edit
5. evaluate the result with compare tools
6. rerun or refine with confidence
7. save a result that is consistently useful

## 5. Workstreams

### Workstream A: Editing Quality Tuning

Objective: make the existing preset system produce stable, believable portrait results.

### Workstream B: Reference-Guided Editing Polish

Objective: make the optional second-image workflow understandable and predictable.

### Workstream C: Reliability and Recovery

Objective: reduce the risk of long CPU runs feeling untrustworthy.

### Workstream D: Beta Readiness

Objective: define and satisfy external beta entry criteria.

## 6. Editing Quality Tuning

### Goals

- improve consistency of portrait presets
- reduce surprising or low-value outputs
- tune for identity preservation and naturalism

### Review Dimensions

- identity retention
- skin texture realism
- eye and face coherence
- lighting realism
- background cleanliness
- prompt adherence

### Tuning Policy

- use draft-tier runs for most tuning loops
- use acceptance-tier runs only at scheduled review points
- record changes to presets and outcomes against benchmark cases

## 7. Reference-Guided Editing Polish

### Goals

- clarify when and why to use a reference image
- reduce confusion between base image and reference image
- improve expected behavior on style, lighting, and angle use cases

### UX Requirements

- clear labels for base vs reference image
- concise helper text
- reference use remains optional
- simple failure messaging when the result diverges

### Product Rule

Reference-guided editing is a support feature, not the primary MVP path. The single-image edit flow must remain stronger and simpler.

## 8. Result Iteration Improvements

### Scope

- make it easier to rerun edits
- improve reuse of latest result as new input
- keep compare and save actions prominent

### Expected Outcomes

- lower friction between first output and second attempt
- clearer loop: `edit -> compare -> refine`

## 9. Reliability and Recovery

### Focus Areas

- long CPU-run trustworthiness
- job status visibility
- restart behavior
- storage and cleanup correctness

### Desired Improvements

- better handling for interrupted queued/running jobs
- clearer surfaced errors
- more predictable history state after failures
- confidence that beta users will not lose track of outputs

## 10. Benchmark and Acceptance Review

### Required Inputs

- benchmark fixture pack from earlier sprints
- fixed seeds
- preset list v1

### Review Cadence

- weekly draft-tier review
- milestone acceptance-tier review

### Output

- benchmark notes
- preset adjustments
- beta readiness recommendation

## 11. Ticket Outline

### WR3-001 - Tune preset pack against benchmark set

- Owner: AI/ML
- Priority: P0
- Outcome: initial presets are directionally consistent on the benchmark pack

### WR3-002 - Improve reference-guided edit UX copy and structure

- Owner: Frontend + UI/UX
- Priority: P0
- Outcome: users understand how to use an optional reference image

### WR3-003 - Improve rerun and refine loop

- Owner: Frontend
- Priority: P0
- Outcome: iteration after first output is fast and obvious

### WR3-004 - Harden job/recovery behavior for beta confidence

- Owner: Backend
- Priority: P0
- Outcome: long CPU runs feel more trustworthy

### WR3-005 - Improve error and status communication

- Owner: Backend + Frontend
- Priority: P1
- Outcome: failures are easier to understand and recover from

### WR3-006 - Add beta readiness checklist

- Owner: Tech Lead + Product
- Priority: P0
- Outcome: team has explicit entry criteria for external beta

### WR3-007 - Run acceptance review on benchmark pack

- Owner: AI/ML + Product + Domain Advisors
- Priority: P1
- Outcome: beta recommendation is based on review, not intuition

### WR3-008 - Document known limitations and beta expectations

- Owner: Product + Marketing
- Priority: P1
- Outcome: beta messaging is honest about CPU-only limits and scope

## 12. Recommended Execution Order

1. WR3-001 Tune preset pack
2. WR3-002 Improve reference-guided UX
3. WR3-003 Improve rerun/refine loop
4. WR3-004 Harden job/recovery behavior
5. WR3-005 Improve error and status communication
6. WR3-006 Add beta readiness checklist
7. WR3-007 Run acceptance review
8. WR3-008 Document known limitations

## 13. Risks

### Risk 1: Team tries to solve too many quality issues at once

Mitigation:

- tune only the v1 preset pack
- defer broader style expansion

### Risk 2: Reference-guided edits stay inconsistent

Mitigation:

- keep the flow optional
- narrow the supported guidance use cases

### Risk 3: CPU latency remains frustrating for beta users

Mitigation:

- keep preview/final model explicit
- message CPU draft/final behavior clearly
- prefer strong draft experience over overly ambitious defaults

### Risk 4: Reliability work is postponed because it is less visible

Mitigation:

- treat recovery and trust as beta blockers
- include them in review gates

## 14. Beta Readiness Criteria

External beta should not start until:

- Sprint 1 stabilization criteria remain satisfied
- Sprint 2 edit-first workflow remains intact
- preset pack performs acceptably on the benchmark set
- rerun/refine loop is usable
- key failure states are understandable
- setup and limitations are documented

## 15. Sprint Review Checklist

- Are portrait presets actually useful on the benchmark pack?
- Is reference-guided editing understandable?
- Can users iterate without getting lost?
- Are failures and long waits communicated clearly?
- Is the team confident enough to expose the MVP to beta users?

## 16. Expected Deliverables

- tuned preset pack v1
- polished reference-guided edit UX
- better rerun/refine flow
- improved recovery and status trust
- beta readiness checklist
- documented beta limitations

## 17. Hand-off to Beta / Phase 4

After Sprint 3, the team should decide one of:

- proceed to closed beta
- run one more hardening sprint
- delay beta and narrow scope further

The decision must be based on benchmark evidence and reliability confidence, not only on feature completeness.
