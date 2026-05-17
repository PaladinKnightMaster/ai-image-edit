# Sprint 2 Outline

Status: Active with local-runtime constraint
Sprint name: Sprint 2 - Editor-First UX and Core Editing Flow
Duration: 2 weeks
Last updated: 2026-05-17
Parent plan: `docs/planning/mvp-war-room-plan.md`
Depends on: `docs/planning/sprint-1-backlog.md`
Sprint owner: Tech Lead

## 1. Sprint Goal

Transform the current chat/generation-oriented product shell into the first real version of the edit-first MVP.

Sprint 2 should make the product feel like a local portrait editing studio rather than a general image-generation interface. The focus is not on broadening model support. The focus is on information architecture, user flow, and making existing edit capabilities usable as a product.

## 2. Definition of Done for Sprint 2

Sprint 2 is complete only when all of the following are true:

- the primary entry experience is explicitly edit-first
- the user can move through a clean `upload -> edit -> compare -> save` flow
- `Create from Scratch` remains available as a secondary mode
- generated images can be turned into edit inputs in one click
- the frontend structure is materially more maintainable than the current single-file implementation
- preset-driven editing exists in a usable first version

## 2.1 Current Runtime Constraint

The local development machine can no longer be treated as a reliable benchmark/signoff environment for
`qwen-image-edit-2511`.

Current known constraint:

- local benchmark execution for `qwen-image-edit-2511` is blocked on this machine by a reproducible native
  process exit (`0xC0000005`) during `Headshot Cleanup`

Operational decision for the remainder of Sprint 2:

- continue Sprint 2 product work using the existing `flux2-klein-9b-gguf` lane as the local draft edit
  runtime
- do not broaden scope into a new engine family; this is an operational use of an already-supported lane
- keep `qwen-image-edit-2511` benchmark/signoff as an off-box validation lane for a stronger machine
- treat long local model runtime as an observability problem: jobs should surface persisted stage,
  progress, and last-activity state, while benchmark observer timeouts must not rewrite active work as
  model failure
- the local FLUX smoke lane has now produced a completed `pending_review` output, so Sprint 2 can use it
  as draft-lane evidence while keeping Qwen edit signoff off-box
- pending-review outputs must remain gated until reveal; the product should make that state recoverable
  from Recent runs without treating the pending image as a normal reusable output

## 3. Scope Summary

### In Scope

- explicit mode split between editing and generation
- editor-first shell and navigation
- generated-image-to-edit handoff
- portrait preset system v1
- optional second reference image workflow
- before/after comparison
- frontend restructuring around product workflows

### Out of Scope

- brush masking or region editing
- batch editing
- Android implementation
- hosted GPU work
- new engine families
- full preset intelligence or auto-prompting

## 4. Product Outcomes

By the end of Sprint 2, a user should be able to:

1. open the app and understand that editing is the primary use case
2. upload a portrait
3. apply a portrait preset or typed instruction
4. run an edit preview
5. compare input and result
6. save the output or reuse it for another round
7. optionally create an image from scratch and immediately convert it into an edit input

## 5. Workstreams

### Workstream A: Product Information Architecture

Objective: shift the product from chat-centric to editor-centric.

### Workstream B: Frontend Restructure

Objective: break the large chat page into maintainable product-oriented components.

### Workstream C: Editing Workflow

Objective: make the edit flow explicit, guided, and reliable.

### Workstream D: Preset System v1

Objective: make editing approachable without exposing too many raw model controls.

### Workstream E: Compare and Save

Objective: make result inspection and iteration feel like a real editing product.

## 6. Proposed UX Structure

### Primary Modes

- `Edit Photo`
- `Create from Scratch`

### Recommended Screen Structure

- Header / app shell
- Mode switch
- Left panel:
  - image input section
  - preset picker
  - prompt/instruction composer
  - advanced controls drawer
- Right panel:
  - result viewer
  - before/after compare
  - recent result actions

### Product Rule

The user should not need to understand model capabilities to use the MVP.

Presets and mode selection should drive the majority of decisions.

## 7. Preset System v1

### Goals

- reduce cognitive load
- express value in photography language, not model language
- make outputs more predictable

### Proposed Presets

- Headshot Cleanup
- Natural Skin Retouch
- Studio Relight
- Background Simplify
- Fashion Portrait
- Multi-Angle Portrait

### Preset Behavior

Each preset should define:

- user-facing name
- short description
- prompt template or prompt hint
- compatible mode(s)
- default settings for draft runs
- optional safe advanced settings

### Implementation Principle

Preset metadata should live in a structured config source, not inlined deeply inside JSX.

## 8. Reference-Guided Edit Workflow

### Scope

Support:

- one base image
- optional one reference image
- prompt text

### Intended Use Cases

- style inspiration
- lighting reference
- angle reference
- portrait look transfer while preserving identity

### Product Constraints

- maximum two inputs
- no masking in Sprint 2
- no advanced reference weighting UI in Sprint 2

## 9. Generated-Image-to-Edit Handoff

### Goal

Turn the current T2I capability into a supporting bridge for the edit-first product.

### Requirements

- every successful generated image should expose a clear `Edit this` action
- action should populate the edit flow with the generated result as the base input
- user should not need to re-upload or manually hunt through history

### Value

This allows the product to keep the current T2I maturity while making editing the visible endpoint.

## 10. Before/After Compare

### Requirements

- show input and output clearly
- support quick toggle or split comparison
- keep the comparison lightweight enough for local performance

### Rule

This is a core MVP feature, not a stretch feature.

## 11. Frontend Refactor Plan

Current state:

- `frontend/app/chat/page.tsx` is too large and owns too many concerns.

Target state:

- page-level shell component
- extracted mode switch component
- extracted input/source panel
- extracted preset picker
- extracted prompt composer
- extracted result viewer
- extracted history/reuse component
- hooks/utilities for job submission and SSE state

### Refactor Constraint

Do not attempt a design-system rewrite in Sprint 2.

Refactor only enough to support the new workflow safely.

## 12. Backend / API Expectations

Sprint 2 backend changes should stay scoped.

Expected work:

- ensure edit jobs remain reliable under the new UX
- make generated-image-to-edit handoff clean
- keep API contracts stable while frontend is being restructured
- support preset-driven request composition if useful
- expose model-specific capability constraints cleanly when local draft lanes differ from the intended
  signoff lane
- expose enough job activity state for slow local inference to remain trustworthy in the UI and review
  harness

Avoid:

- major engine additions
- new runtime lanes
- heavy OpenVINO work

Allowed operational fallback:

- use the existing `flux2-klein-9b-gguf` runner as the local Sprint 2 draft lane while
  `qwen-image-edit-2511` remains blocked on this machine

## 13. AI/ML Work

### Primary Goals

- define preset prompt patterns
- define draft defaults for edit flows
- define reference-guided examples
- validate outputs on the benchmark pack defined in `docs/testing/benchmark-pack.md` where runtime permits

### Current Local Validation Rule

- use `flux2-klein-9b-gguf` for local draft edit iteration on this machine
- keep `qwen-image-edit-2511` benchmark/signoff validation on a stronger machine
- do not treat local FLUX draft results as final acceptance evidence for the Qwen edit lane

### Quality Review Criteria

- identity preservation
- natural skin texture
- eye detail and face coherence
- lighting consistency
- prompt adherence

### Output Policy

Use draft-tier settings for normal tuning and acceptance-tier settings only at milestone review points.

On the current development machine:

- local draft checks may use `flux2-klein-9b-gguf`
- benchmark/signoff for the Qwen edit lane remains deferred to stronger hardware

## 14. Ticket Outline

### WR2-001 - Introduce explicit product mode switch

- Owner: Frontend
- Priority: P0
- Outcome: user can clearly choose `Edit Photo` or `Create from Scratch`

### WR2-002 - Reframe landing experience around editing

- Owner: Frontend + Product
- Priority: P0
- Outcome: editing becomes the obvious primary action

### WR2-003 - Split main chat page into maintainable components

- Owner: Frontend
- Priority: P0
- Outcome: workflow logic is no longer trapped in one giant page file

### WR2-004 - Implement generated-image-to-edit handoff

- Owner: Frontend + Backend
- Priority: P0
- Outcome: one-click conversion from generation result into edit input

### WR2-005 - Implement preset system v1

- Owner: AI/ML + Frontend
- Priority: P0
- Outcome: portrait presets are available and structured

### WR2-006 - Add optional reference-image workflow

- Owner: Frontend + Backend
- Priority: P1
- Outcome: one base image plus one reference image is supported clearly in the UI

### WR2-007 - Add before/after compare

- Owner: Frontend + UI/UX
- Priority: P0
- Outcome: users can evaluate edit output properly

### WR2-008 - Move advanced controls behind a drawer

- Owner: Frontend
- Priority: P1
- Outcome: primary flow is simpler, but advanced users retain control

### WR2-009 - Validate presets against benchmark pack where runtime permits

- Owner: AI/ML
- Priority: P1
- Outcome: presets are directionally consistent on `benchmark-pack-v0`, with local draft checks allowed
  on the FLUX lane and Qwen edit signoff deferred when current hardware blocks the edit runner

### WR2-010 - Update product copy and onboarding hints

- Owner: Product + Frontend
- Priority: P1
- Outcome: messaging matches the editor-first MVP

### WR2-011 - Surface manual-review outputs

- Owner: Frontend + Backend
- Priority: P0
- Outcome: local draft outputs that reach `pending_review` are visible, revealable, and only reusable after
  the reveal gate is completed

## 15. Recommended Execution Order

1. WR2-001 Introduce explicit mode switch
2. WR2-002 Reframe landing experience
3. WR2-003 Split main page into components
4. WR2-005 Implement preset system v1
5. WR2-004 Implement generated-image-to-edit handoff
6. WR2-007 Add before/after compare
7. WR2-008 Move advanced controls behind a drawer
8. WR2-006 Add optional reference-image workflow
9. WR2-010 Update copy and onboarding hints
10. WR2-011 Surface manual-review outputs
11. WR2-009 Validate presets where runtime permits; keep Qwen edit signoff off-box if local hardware remains blocked

## 16. Risks

### Risk 1: Sprint becomes a full frontend rewrite

Mitigation:

- refactor around workflow seams only
- do not chase perfection

### Risk 2: Editing UX exposes model inconsistency

Mitigation:

- keep presets narrow
- validate against benchmark pack early where runtime permits

### Risk 3: Reference-image workflow confuses users

Mitigation:

- keep it optional
- default to a single base image flow

### Risk 4: CPU performance makes compare iteration slow

Mitigation:

- keep draft defaults lean
- reuse preview outputs
- avoid unnecessary reruns
- use the existing FLUX local draft lane instead of repeatedly forcing the blocked local Qwen edit path
- distinguish observer timeout from backend failure, and surface last activity so users can decide whether
  to keep waiting or stop the run externally

### Risk 5: Local Qwen edit benchmark lane is blocked by native runtime failure

Mitigation:

- preserve the benchmark/signoff contract, but move Qwen edit validation to stronger hardware
- keep Sprint 2 product work moving on the existing FLUX local draft lane
- surface capability constraints in the UI so local draft behavior does not misrepresent final signoff behavior

## 17. Sprint Review Checklist

- Is editing now the obvious primary workflow?
- Can a generated image be edited without friction?
- Are presets understandable without model knowledge?
- Is the main frontend code materially easier to work with?
- Does compare mode help users judge results?
- Is Sprint 3 ready to focus on deeper editing quality and hardening?

## 18. Expected Deliverables

- explicit edit-first shell
- maintainable frontend structure
- generated-image-to-edit bridge
- preset system v1
- before/after comparison
- optional reference image support
- manual-review output reveal path
- updated product language

## 19. Hand-off to Sprint 3

Sprint 3 should focus on:

- stronger preset quality
- reference-guided editing polish
- result iteration flow
- recovery and reliability hardening if needed
- prep for public beta criteria

If off-box Qwen edit validation is still pending at Sprint 2 close, Sprint 3 should inherit that signoff
lane explicitly rather than pretending Sprint 2 completed local benchmark closure on blocked hardware.
