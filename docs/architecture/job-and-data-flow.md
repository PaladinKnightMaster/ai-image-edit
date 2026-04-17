# Job and Data Flow

## Core entities

The backend stores three main entity types:

- `jobs`
  - top-level execution state
- `runs`
  - parameters and results for one job execution
- `images`
  - uploaded or generated image metadata

## Current state machine

### Job states

- `queued`
- `running`
- `pending_review`
- `succeeded`
- `failed`

`pending_review` is used for lanes such as FLUX when manual reveal is required before the output image is exposed to the normal result flow.

## Generation flow

1. frontend submits `/api/jobs/t2i`
2. backend validates params and runner capability
3. job and run rows are inserted
4. job is either queued locally or dispatched to the worker
5. SSE events stream status, stage, and progress
6. output image is saved to filesystem and `images` metadata is recorded
7. run is updated with `output_image_id` and latency

## Edit flow

1. frontend uploads or reuses image ids
2. frontend submits `/api/jobs/edit`
3. backend validates runner capability and input images
4. run proceeds through the same queue and event system
5. result is written as a new output image

## Worker flow

1. API persists the job
2. API sends `job_id` to `/worker/run`
3. worker enqueues the job id
4. worker executes `jobs.run_job(...)`
5. worker sends event payloads back to `/api/internal/jobs/{job_id}/event`
6. API pushes those events to SSE subscribers

## Persistence

- database file: `backend/app/db.py` initializes SQLite at `config.DB_PATH`
- image files: `data/images/<image_id>.png`
- extra engine artifacts may be written elsewhere, such as FLUX output directories

## Known limitations

- queued and running jobs are marked failed on restart
- no durable replay queue exists today
- restart behavior is safe for metadata consistency, but not resilient for long-running CPU jobs

## Recommended future direction

- keep the current state machine
- document restart semantics clearly
- add smoke tests for queue and worker behavior
- later, add durable requeue or resumable recovery if the product needs stronger long-run reliability
