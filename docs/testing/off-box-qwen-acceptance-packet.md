# Off-Box Qwen Acceptance Packet

Status: Prepared; execution not started
Last updated: 2026-06-04
Sprint: Sprint 4
Ticket: WR4-002

## Purpose

This packet prepares the `qwen-image-edit-2511` acceptance lane for stronger hardware. It is a runbook and
evidence contract only. It does not approve a local model run and does not change the Sprint 4 beta scope.

Final Qwen-acceptance beta remains no-go until results from this packet are recorded.

## Acceptance Boundary

This packet is for the intended edit model:

- model: `qwen-image-edit-2511`
- evidence lane: `qwen-acceptance`
- benchmark pack: `benchmark-pack-v0`
- asset root: `fixtures/private/benchmark-pack-v0`
- summary artifact: `data/qwen-acceptance-summary.json`
- database artifact: `data/qwen-acceptance.db`

Do not mix these results with local FLUX draft evidence.

## Hardware / Environment Requirements

Use a stronger off-box machine that can run `qwen-image-edit-2511` without the local Windows native crash.

Before execution, confirm:

- fixture images exist under `fixtures/private/benchmark-pack-v0/`
- fixture filenames match `docs/testing/benchmark-pack.v0.json`
- mirrored Qwen edit model exists under `models/hf/Qwen/Qwen-Image-Edit-2511`
- `backend/.env` is configured for the target machine
- `MODEL_ROOT` resolves to the mirrored Qwen root, normally `models/hf`
- the machine has enough RAM/VRAM for the selected run
- the reviewer understands this is a heavy acceptance run

## Qwen Acceptance Targets

Run the active Qwen edit/reference subset:

| Target | Case id | Inputs |
| --- | --- | --- |
| `headshot-cleanup` | `edit-001-headshot-cleanup` | base |
| `studio-relight` | `edit-002-studio-relight` | base |
| `background-simplify` | `edit-003-background-simplify` | base |
| `softbox-relight` | `ref-001-softbox-relight` | base + reference |
| `editorial-look-transfer` | `ref-002-editorial-look-transfer` | base + reference |
| `multi-angle-portrait` | `ref-003-pose-and-crop-guidance` | base + reference |

## Preflight Commands

Run from repo root:

```powershell
cd D:\1_PROJECT\PRIVATE_WORK\ai-image-edit
```

List supported review targets without model execution:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 -ListTargets
```

Preview the full Qwen acceptance target set without model execution:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 `
  -PresetRun headshot-cleanup,studio-relight,background-simplify,softbox-relight,editorial-look-transfer,multi-angle-portrait `
  -DotenvPath .\backend\.env `
  -ModelRoot .\models\hf `
  -DbPath .\data\qwen-acceptance.db `
  -SummaryPath .\data\qwen-acceptance-summary.json
```

Expected preview behavior:

- prints `Model run approval required.`
- lists all selected `qwen-image-edit-2511` targets
- prints `No model execution started.`
- exits without upload, job submission, or model load

## Execution Command After Explicit Approval

Run this only after the off-box reviewer explicitly approves the heavy model execution:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\run_edit_benchmark_case.ps1 `
  -PresetRun headshot-cleanup,studio-relight,background-simplify,softbox-relight,editorial-look-transfer,multi-angle-portrait `
  -DotenvPath .\backend\.env `
  -ModelRoot .\models\hf `
  -DbPath .\data\qwen-acceptance.db `
  -SummaryPath .\data\qwen-acceptance-summary.json `
  -MaxWaitSec 14400 `
  -PollIntervalSec 10 `
  -RunApproved
```

`MaxWaitSec` is an observer window. It is not a model-failure rule.

## Expected Artifacts

Collect these after the run:

- `data/qwen-acceptance-summary.json`
- `data/qwen-acceptance.db`
- generated image files under `data/images/`
- terminal output showing wrapper exit code
- reviewer notes copied into `docs/testing/preset-quality-review-worksheet.md`

The summary should include, per target:

- `preset_id`
- `case_id`
- `job_id`
- `model_id`
- uploaded image ids
- final `status`
- `outcome`
- `error`, if any
- elapsed seconds
- `output_image_id` or `pending_output_image_id`
- `stage`, progress, and `last_activity_at`
- output path

## Review Outcomes

Use the worksheet outcome scale:

- `pass`: usable acceptance result with no beta-blocking defect
- `review`: directionally usable but needs reviewer judgment or tuning notes
- `fail`: material quality defect
- `blocked`: run cannot complete in the off-box environment
- `observer_timeout`: observer stopped waiting while backend state was not terminal

`pending_review` is acceptable as a successful generation state only if the output image exists and can be
revealed through the review gate.

## Manual Review After Execution

For each output, score only the mapped dimensions:

- identity preservation
- skin realism
- eye detail
- hair detail
- lighting coherence
- background cleanliness
- prompt or instruction adherence
- artifact absence

Write one dominant issue for every case, including pass cases.

## Result Logging Template

Copy one row per case into `docs/testing/preset-quality-review-worksheet.md`:

| Date | Preset | Case id | Lane | Model | Outcome | Dominant issue | Decision | Reviewer notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | Headshot Cleanup | `edit-001-headshot-cleanup` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |
| YYYY-MM-DD | Studio Relight | `edit-002-studio-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |
| YYYY-MM-DD | Background Simplify | `edit-003-background-simplify` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |
| YYYY-MM-DD | Softbox Relight | `ref-001-softbox-relight` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |
| YYYY-MM-DD | Editorial Look Transfer | `ref-002-editorial-look-transfer` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |
| YYYY-MM-DD | Multi-Angle Portrait | `ref-003-pose-and-crop-guidance` | `qwen-acceptance` | `qwen-image-edit-2511` | pending | - | - | job id, image id, reviewer notes |

## Go / No-Go Rule

After off-box execution:

- If all cases pass or are acceptable `review`, Qwen-acceptance beta can move to beta readiness review.
- If any core identity-preservation case fails, do not claim Qwen acceptance.
- If execution is blocked, keep draft-lane beta scope and record the infrastructure blocker.
- If outputs reach `pending_review`, validate reveal/reuse on a scratch copy before counting them as reusable product-flow evidence.
