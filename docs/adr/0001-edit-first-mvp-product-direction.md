# ADR 0001: Edit-First MVP Product Direction

- Status: Accepted
- Date: 2026-04-17

## Context

The codebase already supports both text-to-image and image-edit flows:

- `backend/inference/qwen_image_2512.py` provides text-to-image
- `backend/inference/qwen_image_edit_2511.py` provides prompt-driven editing
- `frontend/app/chat/page.tsx` already supports image attachments, history reuse, and generated-image reuse

At the same time, the repo and visible shell are still framed as an "arena" or chat-first generator product. That framing does not match the strongest product wedge discussed in planning.

## Decision

The public MVP is positioned as a local, privacy-first portrait editor.

Text-to-image remains a supported workflow, but it is a secondary lane that feeds the primary `generate -> edit -> refine` loop.

## Why

- Edit-first is more differentiated than a generic local T2I playground.
- It matches the strongest existing model capability for the target product: `qwen-image-edit-2511`.
- It fits the offline-after-setup and privacy-first thesis.
- It makes better use of history reuse, reference images, and manual review patterns already present in the codebase.

## Consequences

- UI and copy should move away from "arena" and "chat" as the product identity.
- `/chat` is an implementation detail, not the desired long-term IA.
- `Create from Scratch` remains important, but it becomes a supporting path.
- Workflow docs, presets, and acceptance testing should be portrait-edit centric.

## Non-goals

- This decision does not remove T2I support.
- This decision does not commit the repo to a full Photoshop-style editor.
