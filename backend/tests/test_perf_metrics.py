"""Non-model proof for the WR5-008 timing and UI coalesce baseline."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.perf_metrics import (  # noqa: E402
    PROGRESS_FLUSH_MS,
    THREAD_PERSIST_MS,
    build_run_metrics,
    coalesce_flushes,
)


class PerfMetricsTest(unittest.TestCase):
    def test_run_metrics_split_queue_load_exec_and_commit(self) -> None:
        metrics = build_run_metrics(
            queued_at_ms=1_000,
            started_at_ms=1_400,
            model_load_ms=800,
            execution_ms=2_000,
            output_commit_ms=50,
            progress_event_count=20,
            rss_samples=[100.0, None, 180.5],
        )
        self.assertEqual(metrics["queue_wait_ms"], 400)
        self.assertEqual(metrics["model_load_ms"], 800)
        self.assertEqual(metrics["execution_ms"], 2_000)
        self.assertEqual(metrics["output_commit_ms"], 50)
        self.assertEqual(metrics["progress_event_count"], 20)
        self.assertEqual(metrics["progress_events_per_sec"], 10.0)
        self.assertEqual(metrics["peak_ram_mb"], 180.5)

    def test_progress_coalesce_cuts_ui_commits(self) -> None:
        event_count = 20
        span_ms = 1_000
        before = event_count
        after = coalesce_flushes(event_count, span_ms, PROGRESS_FLUSH_MS)
        self.assertLess(after, before)
        self.assertEqual(after, 5)
        self.assertEqual(THREAD_PERSIST_MS, 400)
        self.assertGreaterEqual(before - after, 15)


if __name__ == "__main__":
    unittest.main()
