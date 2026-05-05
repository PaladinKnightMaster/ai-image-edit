from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app import jobs  # noqa: E402
from inference.base import GenerationParams  # noqa: E402


class ModelRegistrationTest(unittest.TestCase):
    def test_manager_rejects_unknown_enabled_models(self) -> None:
        script = textwrap.dedent(
            """
            from inference.manager import get_manager

            get_manager()
            """
        )
        env = os.environ.copy()
        env["ENABLED_MODELS"] = "not-a-real-model"

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown ENABLED_MODELS value(s): not-a-real-model", result.stderr)

    def test_api_models_reports_flux_detail_for_active_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            assets_dir = Path(tmp) / "flux-assets"
            assets_dir.mkdir()
            (assets_dir / "diffusion.gguf").write_text("ok", encoding="utf-8")
            (assets_dir / "vae.safetensors").write_text("ok", encoding="utf-8")
            (assets_dir / "text_encoder.safetensors").write_text("ok", encoding="utf-8")

            script = textwrap.dedent(
                """
                import json
                from fastapi.testclient import TestClient
                from app.main import app

                with TestClient(app) as client:
                    print(json.dumps(client.get("/api/models").json()))
                """
            )
            env = os.environ.copy()
            env["ENABLED_MODELS"] = "flux2-klein-9b-gguf"
            env["FLUX2_USE_PY_BINDINGS"] = "0"
            env["FLUX2_USE_SDCLI_FALLBACK"] = "1"
            env["FLUX2_MODEL_DIR"] = assets_dir.as_posix()
            env["FLUX2_DIFFUSION_GGUF"] = (assets_dir / "diffusion.gguf").as_posix()
            env["FLUX2_VAE"] = (assets_dir / "vae.safetensors").as_posix()
            env["FLUX2_TEXT_ENCODER"] = (assets_dir / "text_encoder.safetensors").as_posix()
            env["FLUX2_LLM_GGUF"] = (assets_dir / "missing-llm.gguf").as_posix()

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
            msg=f"/api/models probe failed\\nstdout:\\n{result.stdout}\\nstderr:\\n{result.stderr}",
        )
        stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(stdout_lines, msg=f"probe produced no output\\nstderr:\\n{result.stderr}")
        payload = json.loads(stdout_lines[-1])
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], "flux2-klein-9b-gguf")
        self.assertEqual(payload[0]["edit_input_limit"], 1)
        self.assertFalse(payload[0]["present"])
        self.assertIn("sd-cli: missing", payload[0]["detail"])
        self.assertIn("FLUX2_LLM_GGUF", payload[0]["detail"])


class JobErrorSurfaceTest(unittest.TestCase):
    def test_submit_job_includes_model_detail_when_assets_missing(self) -> None:
        runner = Mock()
        runner.capabilities = {"t2i"}
        runner.model_status.return_value = {
            "present": False,
            "detail": "sd-cli: missing FLUX2_LLM_GGUF.",
        }
        manager = Mock()
        manager.get_runner.return_value = runner
        params = GenerationParams(
            prompt="test prompt",
            seed=123,
            steps=1,
            width=512,
            height=512,
            guidance_scale=4.0,
        )

        with patch("app.jobs.get_manager", return_value=manager):
            with self.assertRaisesRegex(ValueError, "FLUX2_LLM_GGUF"):
                jobs.submit_job("t2i", "flux2-klein-9b-gguf", params)


if __name__ == "__main__":
    unittest.main()
