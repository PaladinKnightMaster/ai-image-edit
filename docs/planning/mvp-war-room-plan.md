# MVP War Room Plan And Roadmap

Status: Active living roadmap
Last updated: 2026-09-22
Owner: Tech Lead
Strategy source: `docs/planning/strategy-checkpoint.md`

## 1. North Star

Build a privacy-first local portrait editor that is useful and developable on a CPU-only Windows machine. Keep
text-to-image as a supporting workflow and preserve offline-after-setup operation.

## 2. Hard Constraints

- no current GPU budget, purchase plan, or hosted-GPU dependency
- daily work must complete without model execution
- heavy CPU model runs require explicit approval
- no fresh physical tester machine is currently available
- final model-quality claims require lane-specific benchmark evidence
- reliability and workflow quality take priority over a larger model catalog

## 3. Product Scope

In scope:

- edit-first workflow
- supporting create-from-scratch workflow
- one base image plus one optional reference image
- portrait presets
- reveal, compare, refine, download, history, and reuse
- local job reliability and recovery
- reproducible Windows setup

Out of scope for the active roadmap:

- GPU-required operation
- hosted inference
- brush masking or layer editing
- batch processing
- mobile
- team collaboration or cloud sync
- broad engine expansion

## 4. Runtime Strategy

| Lane | Role | Current evidence |
| --- | --- | --- |
| `flux2-klein-9b-gguf` | local CPU draft edit and T2I | one approved edit reached `pending_review` in 2387 seconds |
| `qwen-image-edit-2511` | intended edit acceptance | locally blocked by native crash; off-box packet prepared |
| `qwen-image-2512` | supporting T2I and smoke lane | registered and used by fast-check profile |
| `sdxl-openvino` | CPU acceleration research | not MVP-core and not an edit replacement |

Model replacement is a later benchmark decision. Private non-commercial use means commercial licensing is not a
current selection gate, but model provenance remains documented.

## 5. Architecture Strategy

- keep the FastAPI, Next.js, SQLite, filesystem, and runner foundation
- make SQLite-backed durable orchestration the default local path
- add attempt history, leases, heartbeat, cancellation, bounded retry, and recovery
- isolate non-cooperative native inference in child processes
- keep Temporal optional and non-model until a local contract and evidence justify adoption
- use Saga compensation only for partial side effects
- keep browser Service Workers outside durable job ownership

## 6. Validation Strategy

1. static and unit checks
2. temporary-database API/state tests
3. deterministic browser-flow tests
4. current-workstation release smoke
5. Windows Sandbox clean-Windows surrogate smoke
6. Docker/WSL2 reproducibility smoke
7. approval-gated local draft run
8. optional off-box acceptance run

Docker does not prove Windows launch or native runtime behavior. Windows Sandbox does not prove independent
physical-machine compatibility. Evidence labels must retain those boundaries.

## 7. Delivery History

### Sprint 1 - Stabilization And Dev Loop

Closed. Startup, fast-check profiles, launch scripts, model registration, frontend static validation, and benchmark
fixture foundations were established.

### Sprint 2 - Edit-First Product Surface

Closed. Explicit modes, edit-first landing, presets, base/reference roles, generated-image handoff, compare, and
component extraction were delivered. See `docs/planning/sprint-2-closeout-audit.md`.

### Sprint 3 - Reliability And Beta Readiness

Closed. Reveal/reuse, recovery checks, status communication, preset review, and draft-lane evidence were hardened.
See `docs/planning/sprint-3-closeout-audit.md`.

### Sprint 4 - Beta Scope And Acceptance Preparation

Residual open. Scope, packets, handoff, runbooks, Sandbox harness, and `e829507` package are prepared. Isolated
clean-Windows smoke is **not** recorded (host `WinRT.Runtime` blocker). Product mainline work continued without
claiming that pass.

### Sprint 5 - CPU Reliability And Durable Workflows

**Active.** Reproducibility, automated frontend flows, stream reconciliation, attempts, cancellation, retry,
restart recovery, performance measurement, and optional Temporal learning are sequenced in
`docs/planning/sprint-5-outline.md`. OpenVINO is the local CPU mainline; Qwen-Image-2.1 is a catalogued
frontier candidate only.

## 8. Current Phase Gate

Sprint 4 clean-env gate remains open as residual risk. Sprint 5 reliability work proceeds in parallel:

- do not claim independent-machine compatibility from Sandbox or Docker
- record owner disposition on the Sandbox host blocker when available
- keep WR5-001 visible until pass or accepted blocker is written into the result log

Runtime lane amendment (2026-09): local default model is `sdxl-openvino` (t2i + edit), not FLUX or Qwen.

## 9. Success Measures

Product:

- edit flow completion without hidden state
- reveal, compare, download, and reuse success
- understandable cancellation and retry behavior

Engineering:

- reproducible dependency resolution
- clean smoke pass rate
- false-failure rate after stream disconnect
- cancellation completion time
- recovery correctness after restart
- queue wait, execution latency, peak RAM, and output-commit time

Quality:

- identity preservation
- instruction adherence
- artifact absence
- lane-specific benchmark pass rate

## 10. Change Control

Update this roadmap when product scope, hardware assumptions, runtime lanes, or active sprint sequence changes.
Use ADRs for durable decisions and closeout audits for historical evidence.
