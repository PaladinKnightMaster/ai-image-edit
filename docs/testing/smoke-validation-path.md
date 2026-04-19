# Smoke Validation Path

## Sprint 1 standard smoke engine

The standard Sprint 1 inference smoke engine is:

- `qwen-image-2512`

## Why this engine

`qwen-image-2512` is the standard smoke lane because it is the least surprising path that already
matches the current Sprint 1 runtime and documentation:

- it is the engine already scoped in `backend/.env.fast-check`
- it uses the canonical mirrored-asset flow under `MODEL_ROOT`
- it exercises the current text-to-image job path without requiring image upload first
- it matches the engineering sequence of stabilizing the current T2I lane before broader edit-first
  restructuring

## Why the other engines are not the standard smoke lane

- `qwen-image-edit-2511`
  - important MVP lane, but not the smoke baseline because it requires upload/edit setup first
- `flux2-klein-9b-gguf`
  - useful advanced lane, but not the Sprint 1 smoke baseline because it requires separate asset
    provisioning and manual-review behavior
- `sdxl-openvino`
  - research lane only in Sprint 1

## Standard smoke recipe

Environment:

- backend started with `.\scripts\start_backend.ps1 -Mode fast-check`
- `backend/.env.fast-check`
- `ENABLED_MODELS=qwen-image-2512`

Payload:

- model: `qwen-image-2512`
- prompt: `a cinematic portrait of a robot painter`
- negative prompt: `blurry, low quality`
- seed: `1234`
- size: `512x512`
- steps: `8`
- guidance scale: `3.5`
- true cfg scale: `1.1`

## Standard command

After the backend is running in fast-check mode:

```powershell
.\scripts\smoke_qwen_t2i.ps1
```

The script:

- verifies `qwen-image-2512` is registered and `present`
- submits the standard smoke payload
- polls `/api/jobs/{job_id}`
- exits non-zero on failure or timeout

## Success criteria

A smoke pass means:

- the backend accepts the job
- the job progresses through the queue without crashing
- the final status is `succeeded`
- the run returns an `output_image_id`

This is a correctness check, not a quality sign-off check.
