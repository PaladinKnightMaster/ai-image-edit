# WR3-007 Draft Preset Review Approval Packet

Status: Executed once; draft evidence and scratch reveal validation recorded
Last updated: 2026-06-04
Sprint: Sprint 3
Ticket: WR3-007

## Purpose

WR3-007 is the first approval-gated model-evidence step for Sprint 3. It can collect local FLUX draft
evidence where feasible, but it cannot close Qwen acceptance signoff.

This packet records the run decision and first approved local FLUX draft result. It does not authorize
additional model runs.

## Recommended First Target

Run the smallest local draft target first:

- target: `flux-draft-smoke`
- case id: `local-flux-one-image-smoke`
- model: `flux2-klein-9b-gguf`
- lane: `flux-draft`
- tier: draft only
- expected behavior: long CPU-bound run; prior evidence reached `pending_review` after about 34.7 minutes
- acceptance boundary: workflow and draft-output evidence only, not final preset quality acceptance

Do not run `qwen-image-edit-2511` locally for WR3-007 on this machine. Local Qwen edit signoff remains
blocked by the native Windows access violation already documented in the preset review notes.

## Approval Preview Command

Use this command first. It lists the selected target and exits without model execution:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 -PresetRun flux-draft-smoke
```

Expected preview behavior:

- prints `Model run approval required.`
- prints the selected target
- prints `No model execution started.`
- exits without upload, job submission, or model load

## Execution Command After Explicit Approval

Use this command only after the user explicitly approves the heavy run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 -PresetRun flux-draft-smoke -RunApproved -SummaryPath .\data\benchmark-review-summary.json
```

The command may load the local FLUX runtime and hold CPU and memory for an extended period.

## Evidence To Record

If approved and run, record the following in `docs/testing/preset-quality-review-worksheet.md`:

- date
- preset target
- case id
- lane: `flux-draft`
- model id
- job id
- output image id or pending output image id
- final job status
- stage and progress
- elapsed time
- outcome: `pass`, `review`, `fail`, `blocked`, or `observer_timeout`
- dominant issue
- whether reveal/reuse remains valid after the run

Also keep `data/benchmark-review-summary.json` as the machine-readable artifact for the run.

## Go / No-Go Criteria

Approve the run only if all of the following are true:

- the machine can be tied up for a long CPU-bound run
- draft FLUX evidence is useful enough to justify the cost
- the result will be labeled `flux-draft`, not `qwen-acceptance`
- the user understands this may end at `pending_review`, `observer_timeout`, or process failure

Do not approve if the goal is final Qwen quality signoff. That must remain off-box.

## Current WR3-007 State

- one `flux-draft-smoke` run was approved and completed on 2026-06-03
- job id: `dfc36b9bde8d4ee7b111c5196d8ecb24`
- run id: `37706e19de514559a21a0696d3705d5d`
- uploaded base image id: `d05dfaaaf8c840848d44551e759594b6`
- pending output image id: `6ea3269b9814425fa91ab6bdf149b01a`
- output path: `data/images/6ea3269b9814425fa91ab6bdf149b01a.png`
- status: `pending_review`
- stage/progress: `review`, `4/4`, `100%`
- elapsed time: 2387 seconds; backend latency: 2383889 ms
- wrapper exit: `0x00000000`
- scratch-copy reveal validation passed on 2026-06-04
- scratch reveal result: image `6ea3269b9814425fa91ab6bdf149b01a`, status `succeeded`, stage `complete`
- scratch reuse result: run appeared in `GET /api/runs?status=succeeded` and disappeared from
  `GET /api/runs?status=pending_review`
- scratch image retrieval: `GET /api/images/6ea3269b9814425fa91ab6bdf149b01a` returned 200
- real DB after validation remained `pending_review` with `pending_output_image_id` intact
- WR4-006 decision is locked in `docs/planning/wr3-007-fixture-decision.md`: keep the live benchmark DB
  job pending as a fixture and use scratch DB copies for routine reveal/reuse validation
