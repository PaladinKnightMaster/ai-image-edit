"""Persisted cancel and one-retry policy (WR5-006). No model execution."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


class CancelRetryTest(unittest.TestCase):
    def setUp(self) -> None:
        from app import config, db, jobs, orchestration

        self.config = config
        self.db = db
        self.jobs = jobs
        self.orchestration = orchestration
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = config.DB_PATH
        self.original_mode = config.INFERENCE_MODE
        config.DB_PATH = Path(self.temp_dir.name) / "test.db"
        config.INFERENCE_MODE = "local"
        db.init_db()

    def tearDown(self) -> None:
        self.config.DB_PATH = self.original_db_path
        self.config.INFERENCE_MODE = self.original_mode
        self.temp_dir.cleanup()

    def _insert_job(self, job_id: str, status: str) -> None:
        now = int(time.time() * 1000)
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, type, status, created_at, stage, last_activity_at, cancel_requested
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, "edit", status, now, status, now, 0),
            )
            conn.commit()

    def test_queued_cancel_is_terminal_and_not_retryable(self) -> None:
        self._insert_job("job-q", "queued")
        job = self.jobs.request_cancel("job-q")
        self.assertEqual(job["status"], "cancelled")
        self.assertTrue(job["cancel_requested"])
        self.assertFalse(self.orchestration.should_auto_retry("job-q", "cancelled"))

    def test_running_cancel_is_cooperative_and_child_stop_is_forced(self) -> None:
        self._insert_job("job-r", "running")
        attempt = self.orchestration.begin_attempt("job-r")
        self.jobs.request_cancel("job-r")
        self.assertTrue(self.orchestration.is_cancel_requested("job-r"))

        with self.assertRaises(self.orchestration.JobCancelled):
            if self.orchestration.is_cancel_requested("job-r"):
                raise self.orchestration.JobCancelled("Job cancelled.")

        process = MagicMock()
        process.wait.side_effect = [subprocess.TimeoutExpired(cmd="sd-cli", timeout=2), 0]
        self.orchestration.set_active_job("job-r")
        with self.assertRaises(self.orchestration.JobCancelled):
            self.orchestration.abort_child_if_cancelled(process, "job-r")
        process.terminate.assert_called_once()
        process.kill.assert_called_once()

        self.jobs._mark_job_cancelled("job-r")
        history = self.orchestration.list_attempts("job-r")
        self.assertEqual(history[0]["id"], attempt["id"])
        self.assertEqual(history[0]["status"], "cancelled")
        self.assertEqual(history[0]["failure_type"], "user_cancel")
        self.assertFalse(history[0]["retryable"])

    def test_transient_failure_retries_once_then_stops(self) -> None:
        self._insert_job("job-t", "running")
        self.assertTrue(
            self.orchestration.should_auto_retry("job-t", "Worker dispatch failed: timeout")
        )
        self.jobs._requeue_for_retry("job-t", "Worker dispatch failed: timeout")
        history = self.orchestration.list_attempts("job-t")
        self.assertEqual(history, [])
        self.orchestration.begin_attempt("job-t")
        self.orchestration.finish_open_attempts(
            "job-t",
            status="failed",
            message="Worker dispatch failed: timeout",
        )
        self.assertFalse(
            self.orchestration.should_auto_retry("job-t", "Worker dispatch failed: timeout")
        )
        self.assertFalse(self.orchestration.should_auto_retry("job-t", "CUDA out of memory"))

    def test_manual_retry_requeues_same_job(self) -> None:
        self._insert_job("job-m", "failed")
        self.orchestration.begin_attempt("job-m")
        self.orchestration.finish_open_attempts(
            "job-m",
            status="failed",
            failure_type="execution_error",
            retryable=False,
        )
        job = self.jobs.request_manual_retry("job-m")
        self.assertEqual(job["status"], "queued")
        self.assertEqual(len(job["attempts"]), 1)
        self.assertEqual(job["attempts"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
