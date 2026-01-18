from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


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
