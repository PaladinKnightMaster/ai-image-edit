# Job Status And Recovery States

Status: Draft
Last updated: 2026-05-21
Sprint: Sprint 3 / WR3-004

## Purpose

This note defines how existing job and run states should be presented during Sprint 3 beta-readiness work.
It does not add new backend states or change job behavior.

## API Contract

`GET /api/jobs/{job_id}` and `GET /api/runs` keep their machine-readable `status`, `stage`, and `error`
fields. They also expose presentation metadata so clients can communicate long waits, review gates, and
failures consistently:

- `status_label`
- `status_detail`
- `stage_label`
- `error_detail`

Clients should continue using `status` for branching logic. Presentation fields are copy helpers, not
state-machine inputs.

## Status Meanings

| Machine status | Label | User meaning | Reuse state |
| --- | --- | --- | --- |
| `queued` | Queued | Waiting for the local backend to start the job. | Not reusable |
| `running` | Running locally | Local inference is active; CPU runs can take a long time. | Not reusable |
| `pending_review` | Ready for review | Output exists but is hidden until reveal. | Not reusable until reveal |
| `succeeded` | Complete | Output is available for compare, download, or reuse. | Reusable |
| `failed` | Failed | Job stopped before producing a reusable output. | Not reusable |

## Recovery And Observer Notes

- `server restarted` is a recovery marker for queued or running jobs found during backend startup. The job
  is not resumable.
- `observer_timeout` is monitoring evidence from the benchmark harness. It should not be treated as a
  model-quality failure unless the backend job itself is terminal `failed`.
- `pending_review` is a successful generation state for manual-review lanes. Reveal promotes the pending
  output to `output_image_id`, clears `pending_output_image_id`, sets status to `succeeded`, and makes the
  run reusable.

## Remaining WR3-004 Work

- Browser-check the new status labels/details against the existing scratch pending-review fixture if the UI
  starts consuming backend presentation fields directly.
- Keep frontend and backend copy aligned if wording changes.
- Do not add fixed ETA promises for CPU inference in Sprint 3.
