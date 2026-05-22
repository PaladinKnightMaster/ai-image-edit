from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import time
import tempfile
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


class JobStateTransitionTest(unittest.TestCase):
    def setUp(self) -> None:
        from app import config, db, images as image_store, jobs

        self.config = config
        self.db = db
        self.image_store = image_store
        self.jobs = jobs
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = config.DB_PATH
        self.original_image_root = image_store.IMAGE_ROOT
        config.DB_PATH = Path(self.temp_dir.name) / "test.db"
        image_store.IMAGE_ROOT = Path(self.temp_dir.name) / "images"
        image_store.IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
        db.init_db()

    def tearDown(self) -> None:
        self.config.DB_PATH = self.original_db_path
        self.image_store.IMAGE_ROOT = self.original_image_root
        self.temp_dir.cleanup()

    def _insert_run(
        self,
        *,
        job_id: str,
        run_id: str,
        status: str,
        output_image_id: str | None = None,
        pending_output_image_id: str | None = None,
        job_type: str = "edit",
    ) -> None:
        now = int(time.time() * 1000)
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, type, status, created_at, started_at, finished_at, error,
                    stage, progress_percent, progress_step, progress_total, last_activity_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    job_type,
                    status,
                    now,
                    now if status in {"running", "pending_review", "succeeded"} else None,
                    now if status in {"pending_review", "succeeded", "failed"} else None,
                    None,
                    "review" if status == "pending_review" else status,
                    100 if status in {"pending_review", "succeeded"} else 0,
                    0,
                    None,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO runs (
                    id, job_id, model_id, prompt, negative_prompt, seed, steps,
                    width, height, guidance_scale, true_cfg_scale, strength,
                    input_image_ids, output_image_id, pending_output_image_id, latency_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    job_id,
                    "flux2-klein-9b-gguf",
                    "clean up the portrait",
                    None,
                    123,
                    4,
                    None,
                    None,
                    4.0,
                    1.0,
                    0.65,
                    json.dumps(["base-image"]),
                    output_image_id,
                    pending_output_image_id,
                    250,
                ),
            )
            conn.commit()

    def test_reveal_pending_review_promotes_output_for_reuse(self) -> None:
        job_id = "job-pending"
        run_id = "run-pending"
        pending_image_id = "pending-image"
        self._insert_run(
            job_id=job_id,
            run_id=run_id,
            status="pending_review",
            pending_output_image_id=pending_image_id,
        )

        image_id = self.jobs.reveal_job(job_id)

        self.assertEqual(image_id, pending_image_id)
        job = self.jobs.get_job(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job["status"], "succeeded")
        self.assertEqual(job["stage"], "complete")
        self.assertEqual(job["progress_percent"], 100)
        self.assertEqual(job["run"]["output_image_id"], pending_image_id)
        self.assertIsNone(job["run"]["pending_output_image_id"])

        run = self.jobs.get_run(run_id)
        self.assertEqual(run["output_image_id"], pending_image_id)
        self.assertIsNone(run["pending_output_image_id"])

        from app.main import JobResponse, RunResponse

        job_payload = JobResponse.model_validate(job).model_dump()
        run_payload = RunResponse.model_validate(run).model_dump()
        self.assertEqual(job_payload["status"], "succeeded")
        self.assertEqual(job_payload["status_label"], "Complete")
        self.assertEqual(job_payload["status_detail"], "The output is available for compare, download, or reuse.")
        self.assertEqual(job_payload["stage_label"], "Complete")
        self.assertEqual(job_payload["run"]["output_image_id"], pending_image_id)
        self.assertIsNone(job_payload["run"]["pending_output_image_id"])
        self.assertEqual(run_payload["output_image_id"], pending_image_id)
        self.assertIsNone(run_payload["pending_output_image_id"])

        reusable_runs = self.jobs.list_runs(status="succeeded")
        self.assertEqual(len(reusable_runs), 1)
        self.assertEqual(reusable_runs[0]["output_image_id"], pending_image_id)
        self.assertIsNone(reusable_runs[0]["pending_output_image_id"])
        self.assertEqual(self.jobs.list_runs(status="pending_review"), [])

    def test_reveal_endpoint_updates_job_and_runs_api(self) -> None:
        job_id = "job-api-pending"
        run_id = "run-api-pending"
        pending_image_id = "pending-api-image"
        self._insert_run(
            job_id=job_id,
            run_id=run_id,
            status="pending_review",
            pending_output_image_id=pending_image_id,
        )

        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            reveal_response = client.post(f"/api/jobs/{job_id}/reveal")
            self.assertEqual(reveal_response.status_code, 200)
            self.assertEqual(reveal_response.json(), {"image_id": pending_image_id})

            job_response = client.get(f"/api/jobs/{job_id}")
            self.assertEqual(job_response.status_code, 200)
            job_payload = job_response.json()
            self.assertEqual(job_payload["status"], "succeeded")
            self.assertEqual(job_payload["status_label"], "Complete")
            self.assertEqual(job_payload["status_detail"], "The output is available for compare, download, or reuse.")
            self.assertEqual(job_payload["stage"], "complete")
            self.assertEqual(job_payload["stage_label"], "Complete")
            self.assertEqual(job_payload["run"]["output_image_id"], pending_image_id)
            self.assertIsNone(job_payload["run"]["pending_output_image_id"])

            succeeded_response = client.get("/api/runs?status=succeeded&limit=10")
            self.assertEqual(succeeded_response.status_code, 200)
            succeeded_runs = succeeded_response.json()
            revealed = [run for run in succeeded_runs if run["id"] == run_id]
            self.assertEqual(len(revealed), 1)
            self.assertEqual(revealed[0]["status_label"], "Complete")
            self.assertEqual(
                revealed[0]["status_detail"],
                "The output is available for compare, download, or reuse.",
            )
            self.assertEqual(revealed[0]["output_image_id"], pending_image_id)
            self.assertIsNone(revealed[0]["pending_output_image_id"])

            pending_response = client.get("/api/runs?status=pending_review&limit=10")
            self.assertEqual(pending_response.status_code, 200)
            self.assertEqual(
                [run for run in pending_response.json() if run["id"] == run_id],
                [],
            )

    def test_delete_pending_review_run_can_delete_pending_image(self) -> None:
        job_id = "job-delete"
        run_id = "run-delete"
        pending_image_id = "pending-delete-image"
        image_path = self.image_store.get_image_path(pending_image_id)
        image_path.write_bytes(b"not a real png")
        self._insert_run(
            job_id=job_id,
            run_id=run_id,
            status="pending_review",
            pending_output_image_id=pending_image_id,
        )

        deleted = self.jobs.delete_run(run_id, delete_images=True)

        self.assertTrue(deleted)
        self.assertIsNone(self.jobs.get_run(run_id))
        self.assertFalse(image_path.exists())

    def test_recover_interrupted_jobs_marks_queued_and_running_failed(self) -> None:
        self._insert_run(job_id="job-queued", run_id="run-queued", status="queued")
        self._insert_run(job_id="job-running", run_id="run-running", status="running")
        self._insert_run(
            job_id="job-succeeded",
            run_id="run-succeeded",
            status="succeeded",
            output_image_id="output-image",
        )

        recovered = self.jobs.recover_interrupted_jobs()

        self.assertEqual(recovered, {"queued": 1, "running": 1, "marked_failed": 2})
        queued = self.jobs.get_job("job-queued")
        running = self.jobs.get_job("job-running")
        succeeded = self.jobs.get_job("job-succeeded")
        self.assertEqual(queued["status"], "failed")
        self.assertEqual(queued["error"], "server restarted")
        self.assertEqual(queued["status_label"], "Failed")
        self.assertEqual(queued["stage_label"], "Failed")
        self.assertEqual(
            queued["error_detail"],
            "This job was marked failed during backend restart recovery. The run metadata is safe, but the job is not resumable.",
        )
        self.assertEqual(queued["stage"], "failed")
        self.assertEqual(running["status"], "failed")
        self.assertEqual(running["error"], "server restarted")
        self.assertEqual(running["status_label"], "Failed")
        self.assertEqual(
            running["error_detail"],
            "This job was marked failed during backend restart recovery. The run metadata is safe, but the job is not resumable.",
        )
        self.assertEqual(running["stage"], "failed")
        self.assertEqual(succeeded["status"], "succeeded")

    def test_status_copy_distinguishes_pending_review_and_observer_timeout(self) -> None:
        self._insert_run(
            job_id="job-review",
            run_id="run-review",
            status="pending_review",
            pending_output_image_id="pending-image",
        )
        self._insert_run(job_id="job-timeout", run_id="run-timeout", status="failed")
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE jobs SET error = ? WHERE id = ?",
                ("observer_timeout after 7200s; job remained running", "job-timeout"),
            )
            conn.commit()

        review = self.jobs.get_job("job-review")
        timeout = self.jobs.get_run("run-timeout")

        self.assertEqual(review["status_label"], "Ready for review")
        self.assertEqual(review["status_detail"], "The output is ready but hidden until it is revealed.")
        self.assertEqual(review["stage_label"], "Review")
        self.assertEqual(timeout["status_label"], "Failed")
        self.assertEqual(
            timeout["error_detail"],
            "The observer stopped waiting while the job may still have been active. Treat this as monitoring evidence, not model-quality failure.",
        )


class BenchmarkReviewRevealFixtureTest(unittest.TestCase):
    FIXTURE_DB = BACKEND_ROOT.parent / "data" / "app.benchmark-review.db"
    PENDING_JOB_ID = "64ff0fcdc35b42c3b46e35be413c8e48"
    PENDING_RUN_ID = "4efd5b09d456429380f227c12cd80191"
    PENDING_IMAGE_ID = "340ab221970549709dc9d017b96b3cba"

    def setUp(self) -> None:
        if not self.FIXTURE_DB.exists():
            raise unittest.SkipTest("benchmark-review DB fixture is not available")
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.scratch_db = Path(self.temp_dir.name) / "app.benchmark-review.copy.db"
        shutil.copy2(self.FIXTURE_DB, self.scratch_db)

        from app import config, db, images as image_store

        self.config = config
        self.db = db
        self.image_store = image_store
        self.original_db_path = config.DB_PATH
        config.DB_PATH = self.scratch_db
        db.init_db()

    def tearDown(self) -> None:
        self.config.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    @staticmethod
    def _fetch_fixture_row(db_path: Path) -> dict | None:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT runs.id, runs.job_id, jobs.status, jobs.stage,
                       runs.output_image_id, runs.pending_output_image_id
                FROM runs
                JOIN jobs ON jobs.id = runs.job_id
                WHERE jobs.id = ?
                """,
                (BenchmarkReviewRevealFixtureTest.PENDING_JOB_ID,),
            ).fetchone()
        return dict(row) if row else None

    def test_copied_benchmark_pending_review_reveals_through_api(self) -> None:
        original_row = self._fetch_fixture_row(self.FIXTURE_DB)
        if not original_row:
            raise unittest.SkipTest("pending-review benchmark job is not available")
        if original_row["status"] != "pending_review":
            raise unittest.SkipTest("benchmark fixture is no longer pending_review")
        if original_row["pending_output_image_id"] != self.PENDING_IMAGE_ID:
            raise unittest.SkipTest("benchmark fixture pending image changed")
        self.assertIsNone(original_row["output_image_id"])
        self.assertTrue(
            self.image_store.get_image_path(self.PENDING_IMAGE_ID).exists(),
            "pending benchmark image file should exist",
        )

        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            reveal_response = client.post(f"/api/jobs/{self.PENDING_JOB_ID}/reveal")
            self.assertEqual(reveal_response.status_code, 200)
            self.assertEqual(reveal_response.json(), {"image_id": self.PENDING_IMAGE_ID})

            job_response = client.get(f"/api/jobs/{self.PENDING_JOB_ID}")
            self.assertEqual(job_response.status_code, 200)
            job_payload = job_response.json()
            self.assertEqual(job_payload["status"], "succeeded")
            self.assertEqual(job_payload["status_label"], "Complete")
            self.assertEqual(job_payload["stage"], "complete")
            self.assertEqual(job_payload["stage_label"], "Complete")
            self.assertEqual(job_payload["run"]["id"], self.PENDING_RUN_ID)
            self.assertEqual(job_payload["run"]["output_image_id"], self.PENDING_IMAGE_ID)
            self.assertIsNone(job_payload["run"]["pending_output_image_id"])

            succeeded_response = client.get("/api/runs?status=succeeded&limit=50")
            self.assertEqual(succeeded_response.status_code, 200)
            succeeded_runs = succeeded_response.json()
            revealed = [run for run in succeeded_runs if run["id"] == self.PENDING_RUN_ID]
            self.assertEqual(len(revealed), 1)
            self.assertEqual(revealed[0]["output_image_id"], self.PENDING_IMAGE_ID)
            self.assertIsNone(revealed[0]["pending_output_image_id"])

            pending_response = client.get("/api/runs?status=pending_review&limit=50")
            self.assertEqual(pending_response.status_code, 200)
            pending_runs = pending_response.json()
            self.assertEqual(
                [run for run in pending_runs if run["id"] == self.PENDING_RUN_ID],
                [],
            )

            image_response = client.get(f"/api/images/{self.PENDING_IMAGE_ID}")
            self.assertEqual(image_response.status_code, 200)

        copied_row = self._fetch_fixture_row(self.scratch_db)
        self.assertEqual(copied_row["status"], "succeeded")
        self.assertEqual(copied_row["output_image_id"], self.PENDING_IMAGE_ID)
        self.assertIsNone(copied_row["pending_output_image_id"])

        original_after = self._fetch_fixture_row(self.FIXTURE_DB)
        self.assertEqual(original_after, original_row)


class JobQueueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.getenv("RUN_INFERENCE_TESTS") != "1":
            raise unittest.SkipTest("Set RUN_INFERENCE_TESTS=1 to run inference tests.")
        try:
            import torch  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("torch not installed") from exc
        if not torch.cuda.is_available() and os.getenv("RUN_CPU_INFERENCE_TESTS") != "1":
            raise unittest.SkipTest(
                "CPU inference is slow; set RUN_CPU_INFERENCE_TESTS=1 to force."
            )
        try:
            import diffusers  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("diffusers not installed") from exc
        try:
            from fastapi.testclient import TestClient  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("fastapi test client not available") from exc

    def test_submit_job_and_complete(self) -> None:
        if os.getenv("HF_HUB_OFFLINE") != "1":
            self.skipTest("Offline mode is disabled.")
        from app import images as image_store
        from app import model_registry
        from app.main import app

        try:
            model_registry.resolve_model_path("qwen-image-2512")
        except FileNotFoundError:
            self.skipTest("Model files missing.")

        from fastapi.testclient import TestClient

        payload = {
            "model_id": "qwen-image-2512",
            "prompt": "a cinematic portrait of a robot painter",
            "negative_prompt": "blurry, low quality",
            "seed": 1234,
            "steps": 2,
            "width": 512,
            "height": 512,
            "guidance_scale": 4.0,
            "true_cfg_scale": 1.0,
        }

        with TestClient(app) as client:
            response = client.post("/api/jobs/t2i", json=payload)
            self.assertEqual(response.status_code, 200)
            job_id = response.json()["job_id"]

            job = None
            for _ in range(120):
                job_response = client.get(f"/api/jobs/{job_id}")
                self.assertEqual(job_response.status_code, 200)
                job = job_response.json()
                if job["status"] in {"succeeded", "failed"}:
                    break
                time.sleep(2)

            self.assertIsNotNone(job)
            self.assertEqual(job["status"], "succeeded")
            output_image_id = job["run"]["output_image_id"]
            self.assertTrue(output_image_id)
            self.assertTrue(image_store.get_image_path(output_image_id).exists())


if __name__ == "__main__":
    unittest.main()
