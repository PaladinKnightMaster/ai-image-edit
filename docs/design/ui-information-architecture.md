# UI Information Architecture

## Current IA

- `/` redirects to `/chat`
- `/chat` contains almost the entire product
- `/arena` is a status placeholder

This is implementation-convenient, but it is not the intended long-term product IA.

## Target IA

### Primary sections

- `Edit Photo`
- `Create from Scratch`
- `History`
- `Advanced`

### Primary objects

- source image
- optional reference image
- prompt or preset
- result image
- compare view
- run history

## Recommended shell

### Default landing

`Edit Photo`

### Secondary mode

`Create from Scratch`

### Supporting surfaces

- `History` for reuse, replay, and use-as-input
- `Advanced` drawer for model, steps, size, seed, and cleanup controls

## What should leave the default surface

- failed-runs maintenance
- cleanup toggles
- import/export thread controls
- backend-health placeholder content
- diagnostics surfaces presented too prominently

## Mode behavior

The product should expose explicit mode selection. It should not rely only on `attachments.length > 0` to infer whether the user intends to edit or generate.

## Relationship to current code

The current `frontend/app/chat/page.tsx` already contains most primitives needed for this IA:

- attachments
- history picker
- recent runs
- generated-image reuse
- reveal flow

The missing part is product structure, not raw capability.
