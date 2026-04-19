from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class StartupSmokeTest(unittest.TestCase):
    def test_fast_check_profile_health_and_models(self) -> None:
        env = os.environ.copy()
        env["DOTENV_PATH"] = str(BACKEND_ROOT / ".env.fast-check")

        script = """
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app import config
from app.main import app

payload = {
    "db_name": Path(config.DB_PATH).name,
    "inference_mode": config.INFERENCE_MODE,
    "enabled_models": sorted(config.ENABLED_MODELS) if config.ENABLED_MODELS else None,
}

with TestClient(app) as client:
    payload["health_status"] = client.get("/health").status_code
    ready = client.get("/ready")
    payload["ready_status"] = ready.status_code
    payload["ready_ready"] = ready.json()["ready"]
    models = client.get("/api/models")
    payload["models_status"] = models.status_code
    payload["model_ids"] = [item["id"] for item in models.json()]

print(json.dumps(payload))
"""

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"startup smoke failed\\nstdout:\\n{result.stdout}\\nstderr:\\n{result.stderr}",
        )

        stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(stdout_lines, msg=f"startup smoke produced no output\\nstderr:\\n{result.stderr}")
        payload = json.loads(stdout_lines[-1])

        self.assertEqual(payload["db_name"], "app.fast-check.db")
        self.assertEqual(payload["inference_mode"], "local")
        self.assertEqual(payload["enabled_models"], ["qwen-image-2512"])
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(payload["ready_status"], 200)
        self.assertTrue(payload["ready_ready"])
        self.assertEqual(payload["models_status"], 200)
        self.assertEqual(payload["model_ids"], ["qwen-image-2512"])


if __name__ == "__main__":
    unittest.main()
