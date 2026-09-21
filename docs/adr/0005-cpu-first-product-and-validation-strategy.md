# ADR 0005: CPU-First Product And Validation Strategy

- Status: Accepted
- Date: 2026-07-16
- Owners: Tech Lead + AI/ML + DevOps

## Context

The project is developed on a CPU-only Windows desktop. There is no current budget or plan for a GPU,
and the product must remain useful and testable without making GPU hardware a development or release
dependency.

The project also has no separate clean tester machine. Docker Desktop and WSL2 are available, and the
host Windows edition supports Windows Sandbox when the optional feature and virtualization are enabled.

Local evidence currently shows:

- `flux2-klein-9b-gguf` can complete a draft edit on CPU, but one 512px smoke took about 40 minutes
- `qwen-image-edit-2511` remains the intended quality-acceptance lane but crashes locally in its current
  Windows CPU path
- fast non-model checks are effective for API, state, build, and workflow validation

This is a private, non-commercial learning project. A non-commercial model license is not, by itself, a
selection blocker for private use. Model provenance and terms must still be recorded so future sharing,
distribution, or commercialization can be reviewed deliberately.

## Decision

Adopt CPU-first operation as a hard project constraint for the current roadmap.

1. No feature, sprint, or release gate may require a local GPU.
2. Daily work uses non-model checks and the smoke/draft/acceptance ladder.
3. Local CPU model runs remain approval-gated because they can occupy the machine for tens of minutes or
   longer.
4. `flux2-klein-9b-gguf` remains the local draft edit lane.
5. `qwen-image-edit-2511` remains the intended acceptance target, but its evidence stays off-box and is not
   required for the private CPU workflow.
6. Model replacement is benchmark-driven. A candidate must improve a defined combination of portrait
   quality, instruction adherence, peak RAM, latency, stability, and integration cost.
7. Windows Sandbox is the preferred clean-Windows surrogate for installation and non-model release smoke.
8. Docker/WSL2 is a reproducibility and CI-style validation lane, not proof of Windows launch or native
   runtime behavior.
9. Absence of an independent physical tester machine remains a recorded residual risk.

## Validation Ladder

### Smoke

- backend imports, startup, API, job-state, and recovery tests
- frontend lint, typecheck, build, and automated browser flows
- no model load

### Draft

- one explicitly approved local CPU run
- bounded resolution and steps
- records latency, peak RAM, exit status, and output state
- evidence applies only to the executed runtime lane

### Acceptance

- fixed benchmark fixtures and review worksheet
- stronger hardware may be used off-box
- evidence is required before making final model-quality claims, not before ordinary CPU-first coding

## Clean Environment Policy

Windows Sandbox evidence must:

- start from an exported clean commit rather than the host `.venv` or `node_modules`
- install dependencies inside the sandbox
- exclude model execution unless separately approved
- record the environment as `Windows Sandbox surrogate`, not as an independent tester machine

Docker evidence must:

- use pinned base and application dependencies
- exclude model assets, generated data, local environments, and caches from build context
- run only repeatable non-model checks by default

## Consequences

### Positive

- the roadmap matches the hardware that actually exists
- normal development remains inexpensive and repeatable
- model hype cannot bypass product and benchmark evidence
- clean-environment testing can proceed without buying another machine

### Negative

- full local inference remains slow
- Windows Sandbox setup is disposable and can be time-consuming
- Docker cannot prove Windows-specific behavior
- final Qwen acceptance remains external until the local runtime changes or stronger hardware is available

## Rejected Alternatives

### Make GPU access a roadmap dependency

Rejected because it conflicts with the project budget and current operating goal.

### Replace the model before improving reliability

Rejected because a new model would inherit the same dependency, orchestration, testing, and UX weaknesses.

### Treat Docker as a fresh Windows tester machine

Rejected because the WSL2 Linux runtime does not validate Windows launchers, paths, or native executables.
