from __future__ import annotations

import hashlib
import io
import os
import sys
import unittest
from pathlib import Path

from PIL import Image

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app import model_registry  # noqa: E402


def _image_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class SeedDeterminismTest(unittest.TestCase):
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

    def test_t2i_seed_determinism(self) -> None:
        try:
            model_registry.resolve_model_path("qwen-image-2512")
        except FileNotFoundError:
            self.skipTest("Model files missing.")

        from inference.base import GenerationParams
        from inference.manager import get_manager
        import torch

        runner = get_manager().get_runner("qwen-image-2512")
        params = GenerationParams(
            prompt="a still life of apples on a wooden table",
            negative_prompt="blurry, low quality",
            seed=1234,
            steps=5,
            width=512,
            height=512,
            guidance_scale=4.0,
            true_cfg_scale=1.0,
        )

        image_a = runner.generate(params)
        image_b = runner.generate(params)

        if torch.cuda.is_available():
            self.assertEqual(_image_bytes(image_a), _image_bytes(image_b))
            return

        hash_a = hashlib.sha256(_image_bytes(image_a)).hexdigest()
        hash_b = hashlib.sha256(_image_bytes(image_b)).hexdigest()
        self.assertEqual(hash_a, hash_b)


if __name__ == "__main__":
    unittest.main()
