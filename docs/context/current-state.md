# Current State

Status: Active
Last updated: 2026-09-22
Owner: Tech Lead

## Product And Code

- the product is edit-first with explicit `Edit Photo` and `Create from Scratch` modes
- base and optional reference-image roles are explicit
- portrait presets, generated-image-to-edit handoff, before/after compare, history, download, and reuse exist
- pending-review outputs require explicit reveal before normal reuse
- `/chat` sidebar includes a **Hardware fit** panel backed by `GET /api/hardware`
- the frontend is componentized but `frontend/app/chat/page.tsx` still owns substantial API, persistence, and
  EventSource orchestration
- backend jobs, runs, and images persist in SQLite plus filesystem storage
- runner abstractions cover Qwen T2I, Qwen Edit, FLUX GGUF, and SDXL OpenVINO lanes

## Runtime Lanes (truth)

| Lane | Role | Hardware |
| --- | --- | --- |
| `sdxl-openvino` | **Primary local** t2i + img2img edit | CPU / Intel OpenVINO |
| `flux2-klein-9b-gguf` | Optional slow advanced draft | CPU (very slow) / GPU faster |
| `qwen-image-2512` / `qwen-image-edit-2511` | Frontier off-box | CUDA GPU |
| Qwen-Image-2.1 | Catalogued candidate only | Evaluate off-box later |

## Verified Reliability Baseline

- OpenVINO SDXL edit smoke on this workstation (~37s library-base Natural Skin Retouch)
- OpenVINO txt2img and edit unit tests exist
- backend startup and fast-check API smoke pass on the current workstation
- frontend lint, typecheck, and production build have passed in the current workspace
- non-model backend tests cover pending-review reveal, API reveal responses, pending-output cleanup, model
  registration, seed behavior, startup, and queued/running restart classification
- one approved FLUX CPU draft edit completed historically in 2387 seconds and reached `pending_review`
- Windows Sandbox clean-machine smoke is **not** recorded (host `WinRT.Runtime` crash)

## Active Strategy Progress

Sprint 5 Backend + UI reliability is the active improvement track. See
`docs/planning/strategy-checkpoint.md` status table and `docs/planning/sprint-5-outline.md`.

**Not completed yet:** clean-env gate, Playwright flows, SSE reconciliation, durable attempts, cancel/retry,
restart recovery, performance baseline.

## Immediate Next Action

Implement WR5-004 job-stream reconciliation so EventSource disconnect cannot mark a still-running job failed
without backend evidence. Then continue Sprint 5 P0 tickets in outline order.

## Heavy-Run Rule

Do not submit an edit job or run Qwen, FLUX, conversion, or other heavy model work without explicit user approval
after stating expected CPU, memory, and time cost. Do not download Qwen-Image-2.1 onto this CPU box as a product
default.
