# WR3-007 Pending Fixture Decision

Status: Locked
Decision date: 2026-06-04
Related sprint ticket: WR4-006
Source evidence: `docs/testing/wr3-007-draft-preset-review-approval-packet.md`

## Decision

Keep live job `dfc36b9bde8d4ee7b111c5196d8ecb24` in `pending_review` as a benchmark fixture.

Do not reveal the live job during routine Sprint 4 work. Use scratch database copies for reveal and reuse
regression checks unless the Commander explicitly approves changing the live benchmark state.

## Fixture Snapshot

- database: `data/app.benchmark-review.db`
- job id: `dfc36b9bde8d4ee7b111c5196d8ecb24`
- run id: `37706e19de514559a21a0696d3705d5d`
- model id: `flux2-klein-9b-gguf`
- status: `pending_review`
- stage/progress: `review`, `4/4`, `100%`
- output image id: none
- pending output image id: `6ea3269b9814425fa91ab6bdf149b01a`
- output path: `data/images/6ea3269b9814425fa91ab6bdf149b01a.png`

## Rationale

- Scratch-copy reveal validation already proved the pending output can be promoted to reusable
  `succeeded` state.
- The scratch validation verified `pending_output_image_id` clears, `output_image_id` is set, the job
  reaches `succeeded`, reusable run history updates, and image retrieval returns 200.
- Revealing the live benchmark job would add little new reliability evidence.
- Preserving the live pending job gives Sprint 4 and later regression work a real pending-review fixture.
- The fixture is FLUX draft-lane evidence only and does not affect Qwen acceptance status.

## Allowed Future Change

Reveal the live job only after an explicit product or Commander decision that the output should become a
normal reusable result. If that happens, record the reveal date, resulting status, output image id, and any
follow-up reuse validation in this document and in `docs/context/current-state.md`.
