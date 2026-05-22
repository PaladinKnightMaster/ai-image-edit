# User Workflows

## 1. Edit Photo

Primary MVP flow.

1. user uploads a portrait
2. user chooses a preset or writes an edit instruction
3. system runs a preview job
4. user compares before and after
5. user refines instruction or renders a higher-quality result
6. user saves the final image

## 2. Create from Scratch

Supporting flow.

1. user writes a prompt
2. system generates a draft image
3. user chooses the best output
4. user reuses that output as input for editing

## 3. Generate -> Edit -> Refine

Bridge flow between T2I and the edit-first product.

1. create a draft image
2. select `use as input`
3. switch into edit mode
4. refine with portrait-oriented prompts or presets

## 4. Reference-Guided Edit

1. user uploads a base image
2. user optionally uploads one reference image
3. user uses the reference only as visual guidance for lighting, style, framing, or angle
4. system runs edit mode with one or two image ids
5. user compares and saves

The base image remains the identity/source image. The reference image should not be framed as a second
subject or replacement identity.

## 5. History and Replay

1. user opens recent runs or full history
2. user selects an output image
3. user uses it as input or replays parameters
4. system creates a new run instead of mutating the old one

## 6. Manual reveal

For engines with manual review:

1. job completes as `pending_review`
2. user chooses `Reveal result`
3. system moves the pending output into the normal visible result flow

## Known current mismatch

The code already supports these capabilities, but the visible product flow is still chat-shaped. The roadmap expects these workflows to become explicit top-level product paths.
