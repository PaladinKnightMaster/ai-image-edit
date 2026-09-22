"""Attempt history for local SQLite orchestration (WR5-005)."""

from __future__ import annotations

import sys
import tempfile
import time
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


class JobAttemptTest(unittest.TestCase):
    def setUp(self) -> None:
        from app import config, db, jobs, orchestration

        self.config = config
        self.db = db
        self.jobs = jobs
        self.orchestration = orchestration
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = config.DB_PATH
        config.DB_PATH = Path(self.temp_dir.name) / "test.db"
        db.init_db()
        now = int(time.time() * 1000)
        with db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, type, status, created_at, stage, last_activity_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("job-1", "edit", "running", now, "running", now),
            )
            conn.commit()

    def tearDown(self) -> None:
        self.config.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_attempt_history_is_append_only(self) -> None:
        first = self.orchestration.begin_attempt("job-1")
        self.orchestration.heartbeat(first["id"])
        self.orchestration.finish_attempt(
            first["id"],
            status="failed",
            failure_type="execution_error",
            retryable=False,
            exit_code=1,
        )
        second = self.orchestration.begin_attempt("job-1")
        self.orchestration.finish_attempt(
            second["id"],
            status="succeeded",
            output_image_id="img-1",
            exit_code=0,
        )

        history = self.orchestration.list_attempts("job-1")
        self.assertEqual([item["attempt_number"] for item in history], [1, 2])
        self.assertEqual(history[0]["status"], "failed")
        self.assertEqual(history[0]["failure_type"], "execution_error")
        self.assertFalse(history[0]["retryable"])
        self.assertEqual(history[1]["status"], "succeeded")
        self.assertEqual(history[1]["output_image_id"], "img-1")
        self.assertIsNotNone(history[1]["finished_at"])

        job = self.jobs.get_job("job-1")
        self.assertIsNotNone(job)
        self.assertEqual(len(job["attempts"]), 2)

    def test_restart_recovery_closes_open_attempt_without_deleting_history(self) -> None:
        attempt = self.orchestration.begin_attempt("job-1")
        recovered = self.jobs.recover_interrupted_jobs()
        self.assertEqual(recovered["interrupted"], 1)
        self.assertIn("job-1", recovered["requeue_ids"])
        history = self.orchestration.list_attempts("job-1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], attempt["id"])
        self.assertEqual(history[0]["status"], "interrupted")
        self.assertEqual(history[0]["failure_type"], "process_restart")
        self.assertTrue(history[0]["retryable"])
        job = self.jobs.get_job("job-1")
        self.assertEqual(job["status"], "queued")
        self.assertIsNone(job["error"])

    def test_classify_failure_does_not_retry_restart_or_oom(self) -> None:
        self.assertEqual(
            self.orchestration.classify_failure("server restarted"),
            ("process_restart", False),
        )
        self.assertEqual(
            self.orchestration.classify_failure("CUDA out of memory"),
            ("out_of_memory", False),
        )
        self.assertEqual(
            self.orchestration.classify_failure("Input image 'x' not found."),
            ("invalid_input", False),
        )


if __name__ == "__main__":
    unittest.main()
