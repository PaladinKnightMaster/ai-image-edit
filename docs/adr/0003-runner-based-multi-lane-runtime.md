# ADR 0003: Runner-Based Multi-Lane Runtime

- Status: Accepted
- Date: 2026-04-17

## Context

The backend already uses a `Runner` abstraction in `backend/inference/base.py` and registers multiple runtime lanes in `backend/inference/manager.py`:

- `qwen-image-2512`
- `qwen-image-edit-2511`
- `flux2-klein-9b-gguf`
- `sdxl-openvino`

Those lanes do not all have the same capability, provisioning path, or maturity level.

## Decision

Keep the runner-based multi-lane architecture. Treat models as runtime lanes behind a stable API contract rather than hard-coding product behavior into a single model family.

## Why

- It keeps model-specific details isolated.
- It supports mixed maturity across lanes.
- It allows the product to keep one UX while swapping or constraining engines behind the API.
- It matches the current backend shape and avoids a destabilizing rewrite.

## Consequences

- The repo needs a central model catalog doc and better lifecycle consistency.
- Registered runners, mirrored assets, and MVP-supported lanes must be documented separately.
- OpenVINO remains a research lane until it supports the actual edit requirements.

## Non-goals

- This does not mean every registered runner is MVP-core.
- This does not mean every lane is mirrored or provisioned the same way.
