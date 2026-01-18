from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app import model_registry  # noqa: E402


class RunnerLoadTest(unittest.TestCase):
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

    def test_qwen_t2i_loads_locally(self) -> None:
        if os.getenv("HF_HUB_OFFLINE") != "1":
            self.skipTest("Offline mode is disabled.")
        try:
            model_registry.resolve_model_path("qwen-image-2512")
        except FileNotFoundError:
            self.skipTest("Model files missing.")
        from inference.manager import get_manager

        runner = get_manager().get_runner("qwen-image-2512")
        pipeline = runner.load()
        self.assertIsNotNone(pipeline)

    def test_qwen_edit_loads_locally(self) -> None:
        if os.getenv("HF_HUB_OFFLINE") != "1":
            self.skipTest("Offline mode is disabled.")
        try:
            model_registry.resolve_model_path("qwen-image-edit-2511")
        except FileNotFoundError:
            self.skipTest("Model files missing.")
        from inference.manager import get_manager

        runner = get_manager().get_runner("qwen-image-edit-2511")
        pipeline = runner.load()
        self.assertIsNotNone(pipeline)


if __name__ == "__main__":
    unittest.main()
