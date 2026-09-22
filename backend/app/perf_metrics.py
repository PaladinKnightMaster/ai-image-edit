"""CPU and UI timing helpers. No model execution."""

from __future__ import annotations

from typing import Any

# Match the chat timeline: progress paints at most once per interval.
PROGRESS_FLUSH_MS = 250
THREAD_PERSIST_MS = 400


def current_rss_mb() -> float | None:
    try:
        import psutil

        return round(psutil.Process().memory_info().rss / (1024**2), 1)
    except Exception:
        return None


def peak_rss_mb(samples: list[float | None]) -> float | None:
    values = [sample for sample in samples if sample is not None]
    if not values:
        return None
    return round(max(values), 1)


def progress_events_per_sec(event_count: int, execution_ms: int) -> float:
    if execution_ms <= 0:
        return 0.0
    return round(event_count / (execution_ms / 1000.0), 2)


def build_run_metrics(
    *,
    queued_at_ms: int,
    started_at_ms: int,
    model_load_ms: int,
    execution_ms: int,
    output_commit_ms: int,
    progress_event_count: int,
    rss_samples: list[float | None],
) -> dict[str, Any]:
    return {
        "queue_wait_ms": max(0, started_at_ms - queued_at_ms),
        "model_load_ms": max(0, model_load_ms),
        "execution_ms": max(0, execution_ms),
        "output_commit_ms": max(0, output_commit_ms),
        "progress_event_count": progress_event_count,
        "progress_events_per_sec": progress_events_per_sec(progress_event_count, execution_ms),
        "peak_ram_mb": peak_rss_mb(rss_samples),
    }


def coalesce_flushes(event_count: int, span_ms: int, interval_ms: int) -> int:
    """How many UI commits remain when events are evenly spread and coalesced."""
    if event_count <= 0:
        return 0
    if event_count == 1:
        return 1
    step = span_ms / (event_count - 1)
    flushes = 0
    next_allowed = 0.0
    pending = False
    for index in range(event_count):
        timestamp = index * step
        pending = True
        if timestamp >= next_allowed:
            flushes += 1
            pending = False
            next_allowed = timestamp + interval_ms
    if pending:
        flushes += 1
    return flushes
