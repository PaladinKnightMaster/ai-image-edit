# WR5-008 CPU And UI Performance Baseline

Status: Recorded
Date: 2026-09-22
Method: non-model fakes in `backend/tests/test_perf_metrics.py`. No image model was run.

## What is recorded on each finished run

`runs` now stores:

- `queue_wait_ms` — created to running
- `model_load_ms` — `runner.load()`
- `execution_ms` — generate or edit only
- `output_commit_ms` — writing the output file
- `progress_event_count` and `progress_events_per_sec`
- `peak_ram_mb` — max RSS sample around load and execution, when `psutil` can read it

`latency_ms` remains execution plus output commit.

Approved OpenVINO evidence already on this machine stays the runtime reference: a library-base Natural Skin Retouch finished in about 37 seconds. These new fields split that wall time on the next real run. This report does not replace that sample.

## UI change, same fake workload

Workload: 20 progress events spread across 1 second.

| Behavior | Before | After |
| --- | --- | --- |
| Timeline commits | 20 (one per event) | 5 (coalesced every 250 ms) |
| Thread persistence | write on every message change | write after 400 ms of quiet |
| Scroll | smooth-scroll on every progress patch | smooth-scroll only when a message is added or removed |

The coalesce counts are locked by `test_progress_coalesce_cuts_ui_commits`.
