# MVP War Room Plan and Roadmap

Status: Draft / Living document
Last updated: 2026-04-17
Primary owner: Tech Lead
Audience: Product, Engineering, Design, AI/ML, DevOps, GTM
Planning horizon: MVP through first public beta

## 1. Executive Summary

This project should not ship as a generic AI image playground.

The strongest MVP is a local, offline-after-setup portrait editing studio for Intel Windows desktops and laptops. The public product should be edit-first. Text-to-image remains important, but it should serve as a supporting workflow and infrastructure base, not the primary market identity.

The development sequence is different from the product message:

- Engineering sequence: stabilize the current text-to-image path first.
- Product sequence: launch the public MVP as an edit-first experience.
- Runtime strategy: use fast local draft settings for daily development, and reserve slow, higher-quality Qwen runs for milestone validation only.

## 2. Current State Assessment

### 2.1 Strengths

- Backend foundation is viable: FastAPI + worker + SQLite + SSE progress + runner abstraction.
- Current text-to-image path already shows practical progress with `qwen-image-2512` and `flux2-klein-9b-gguf`.
- Edit plumbing already exists with `qwen-image-edit-2511`.
- Local/offline model mirroring pattern already exists.
- The frontend already has history, replay, and "use as input" style primitives that are useful for an editor flow.

### 2.2 Current Blockers

- Windows launcher and smoke entrypoints must stay aligned with a working project Python path.
- OpenVINO is partially integrated but not first-class across docs, registry, and bootstrap flow.
- Job execution and recovery are too fragile for long CPU runs.
- The main frontend surface is still chat/arena shaped, not editor shaped.
- Test and release gates are still thin beyond startup and model-availability smoke coverage.

### 2.3 Hard Constraints

- Primary development machine is CPU-only, with no dedicated GPU.
- Full Qwen runs can take multiple hours on the development machine.
- The normal development loop cannot depend on full local inference runs.
- MVP should remain offline after setup.

## 3. Product Thesis

### 3.1 Positioning

The product is a privacy-first local portrait editor, not a model showcase.

### 3.2 Target User

- Portrait photographers
- Solo creators
- Privacy-sensitive prosumers
- Intel Windows desktop/laptop users who want local image enhancement and guided portrait edits

### 3.3 Core Value Proposition

- Local and offline-after-setup
- Predictable portrait-oriented editing workflows
- Reusable presets and references
- No forced cloud upload for sensitive photos

## 4. MVP Goals and Non-Goals

### 4.1 MVP Goals

- Deliver a reliable local portrait editing flow
- Keep a usable secondary create-from-scratch flow
- Support generated-image-to-edit and reference-guided editing
- Make the CPU-only developer workflow practical
- Ship a narrow, clear product surface

### 4.2 Non-Goals

- Android native app
- Hosted GPU service
- Broad model zoo
- Full Photoshop-style masking and layer editing
- ComfyUI-style workflow graph builder
- Team collaboration or cloud sync

## 5. MVP User Flows

### 5.1 Primary Flow: Edit Photo

1. Upload a portrait
2. Choose a preset or write an edit instruction
3. Run a fast preview
4. Compare before and after
5. Re-run with tuned instruction or render a higher-quality final
6. Save the result

### 5.2 Secondary Flow: Create from Scratch

1. Write a prompt
2. Generate draft image
3. Select result
4. Use generated result as edit input
5. Refine with prompt and optional reference image

### 5.3 Guided Flow: Reference-Based Edit

1. Upload base image
2. Optionally upload one reference image
3. Provide instruction
4. Run portrait-guided edit
5. Compare and save

## 6. Product Scope

### 6.1 In Scope for Public MVP

- Single-image portrait editing
- Optional second reference image
- Generated image can be reused as edit input
- Curated portrait presets
- Before/after comparison
- Result history and replay
- Local/offline operation after model setup

### 6.2 Out of Scope for Public MVP

- Brush masking
- Region selection tools
- Face swap
- Batch processing
- Cloud sync
- Android on-device generation
- Premium hosted GPU lanes

## 7. Technical Strategy

### 7.1 Runtime Lanes

- Primary edit lane: `qwen-image-edit-2511`
- Secondary generation lane: `qwen-image-2512`
- Optional advanced lane: `flux2-klein-9b-gguf`
- Research lane only: `sdxl-openvino`

### 7.2 Runtime Policy

- One active heavy model at a time on CPU-only development machines
- Fast-check env for daily work
- Full-quality validation only at milestone checkpoints

### 7.3 Development Environment Profiles

- Main profile: quality-leaning CPU validation
- Fast-check profile: `backend/.env.fast-check`
- Frontend fast-check profile: `frontend/.env.fast-check`

### 7.4 Test Ladder

- Smoke
  - Purpose: crash detection, API/SSE/job correctness
  - Settings: 384-512px, 4-8 steps
- Draft
  - Purpose: preset tuning, UI review, prompt iteration
  - Settings: 512-640px, 8-12 steps
- Acceptance
  - Purpose: milestone quality validation
  - Settings: 768px, 16-24 steps

### 7.5 Quality Evaluation Set

Create a fixed benchmark pack with:

- 3 text-to-image prompts
- 3 portrait edit prompts
- 3 reference-guided edit prompts
- Fixed seeds for comparison

Evaluation dimensions:

- Identity preservation
- Skin realism
- Eye detail
- Hair detail
- Lighting coherence
- Background cleanliness
- Prompt adherence

## 8. Architecture Principles

- Keep the current backend foundation
- Keep runner abstractions and avoid hard-coding product logic into one model path
- Separate development feedback loops from slow model validation loops
- Prefer presets over exposing raw model complexity
- Keep data local by default
- Avoid introducing new engine families before benchmark discipline exists

## 9. Roadmap and Phases

Assumption: 2-week sprints. Adjust dates after Phase 0 stabilization is complete.

### Phase 0: Stabilization

Objective: make the repo runnable and safe to iterate on.

Key work:

- Fix `backend/app/config.py` startup blocker
- Align registry, docs, mirror script, and runner availability
- Add minimum backend and frontend smoke gates
- Reduce main-screen clutter
- Establish fast-check launch path

Exit criteria:

- Backend imports and starts cleanly
- Frontend builds cleanly
- Fast-check flow works end to end
- One-engine local smoke validation is reliable

### Phase 1: Internal Alpha

Objective: stabilize the current generation path and convert it into a usable local product shell.

Key work:

- Keep `Create from Scratch` functional and reliable
- Make mode switching explicit in the UI
- Rebrand away from arena/chat positioning
- Keep history/replay/use-as-input strong
- Build the benchmark fixture pack

Exit criteria:

- Internal team can use the app without touching raw env variables
- CPU draft runs are predictable enough for product iteration
- The app supports clean generate-to-edit handoff

### Phase 2: Edit-First MVP Beta

Objective: make portrait editing the main product flow.

Key work:

- Promote `Edit Photo` to the default landing mode
- Add curated portrait presets
- Support one base image plus optional one reference image
- Add before/after compare
- Keep `Create from Scratch` as a secondary tab

Exit criteria:

- User can complete `upload -> edit -> compare -> save`
- Presets produce directionally consistent portrait results
- Generated image can be turned into edit input in one click

### Phase 3: Release Candidate

Objective: harden the MVP for real users.

Key work:

- Improve restart and recovery behavior
- Add storage hygiene and cleanup rules
- Improve readiness/status visibility
- Add setup/run documentation for clean machines
- Run acceptance-quality benchmarks

Exit criteria:

- Fresh clone setup is documented and repeatable
- Slow acceptance runs pass the benchmark pack
- No high-severity startup, dispatch, or recovery defects remain

### Phase 4: Post-MVP Expansion

Priority order:

1. Stronger reference-guided editing
2. More portrait preset packs
3. Better edit-capable CPU acceleration lane
4. Hosted GPU service
5. Browser/mobile companion
6. On-device assistant or critique features

## 10. Sprint Plan

### Sprint 1: Stabilization and Dev Loop

- Fix config import blocker
- Add launcher commands for main vs fast-check profiles
- Add backend smoke checks
- Add frontend build/lint/type discipline
- Remove arena/debug clutter from primary workflow

Primary owner: Backend + DevOps + Frontend

### Sprint 2: Product Surface Restructure

- Split `frontend/app/chat/page.tsx` into smaller components
- Introduce explicit mode switch: `Edit Photo` / `Create from Scratch`
- Rebrand visible app language
- Preserve replay/history/use-as-input behavior

Primary owner: Frontend + UI/UX

### Sprint 3: Edit-First Flow

- Promote upload/edit flow
- Add preset picker
- Support base image + optional reference image flow
- Add generated-image-to-edit handoff
- Add before/after compare

Primary owner: Frontend + AI/ML + Product

### Sprint 4: Hardening and Benchmarking

- Run benchmark suite across smoke/draft/acceptance tiers
- Improve recovery/durability behavior
- Clean docs and release checklist
- Lock MVP scope for public beta

Primary owner: Backend + AI/ML + DevOps + Tech Lead

## 11. Workstreams and Ownership

### Tech Lead

- Scope control
- Phase gates
- Architecture decisions
- Release readiness

### Frontend

- Mode-first UX
- Component refactor
- Compare/save/result flows
- Remove non-MVP clutter from the main screen

### Backend

- Config and startup reliability
- Job lifecycle and recovery
- Model lifecycle consistency
- API validation and smoke coverage

### AI/ML

- Preset design
- Evaluation set
- Draft/final preset ladder
- Model parameter defaults

### UI/UX

- Edit-first information architecture
- Premium local-studio visual language
- User-flow simplification

### DevOps / Infra

- CI smoke checks
- Launch scripts
- Setup reproducibility
- Environment profile discipline

### Product / Business

- Keep the wedge narrow
- Maintain problem-solution fit
- Prevent feature drift into a generic generator

### Marketing / GTM

- Messaging: local portrait editor, private and practical
- Avoid generic "AI arena" or "image battle" positioning

### Domain Advisors

- Photographer: review real portrait usefulness
- AI image artist: review creative direction
- Art critic / design reviewer: review quality and consistency

## 12. Success Metrics

### Product Metrics

- Setup success rate on a clean machine
- Preview completion rate
- Edit completion rate
- Save/export completion rate
- Preset reuse rate

### Engineering Metrics

- Backend startup success
- Fast-check run latency
- Queue/job failure rate
- Recovery correctness after restart
- Smoke test pass rate

### Quality Metrics

- Benchmark pass rate at draft tier
- Benchmark pass rate at acceptance tier
- Identity preservation rating on portrait edits
- Prompt adherence rating

## 13. Risks and Mitigations

### Risk: CPU-only development is too slow

Mitigation:

- Use fast-check profile
- Use the smoke/draft/acceptance ladder
- Limit to one heavy model at a time

### Risk: Product scope drifts back into generic T2I

Mitigation:

- Keep edit-first IA
- Make T2I a secondary tab
- Review scope at each phase gate

### Risk: OpenVINO distracts the MVP effort

Mitigation:

- Keep OpenVINO as a research lane until edit needs are supported
- Do not make it a release dependency

### Risk: Large frontend file blocks safe iteration

Mitigation:

- Refactor the chat page early in Sprint 2
- Move presets and workflow logic into reusable modules

### Risk: Long-running jobs fail or become untrustworthy

Mitigation:

- Improve job durability before public beta
- Add restart and recovery testing

## 14. Decisions Already Made

- Public MVP is edit-first
- T2I is a secondary but important supporting workflow
- CPU-only local development requires fast-check profiles
- One heavy model at a time on development hardware
- Generated-image-to-edit is a core bridge workflow
- Offline-after-setup remains a hard product requirement

## 15. Immediate Next Actions

1. Finish Sprint 1 hardening on launcher and smoke reliability
2. Split product modes in the frontend
3. Remove implicit mode inference from the main shell
4. Use the benchmark fixture pack for Sprint 2 preset validation
5. Add one-click generated-image-to-edit handoff

## 16. Change Control

This document should be updated:

- at the end of every sprint
- whenever MVP scope changes
- whenever a new engine becomes a real release candidate
- whenever the hardware/runtime assumptions change
