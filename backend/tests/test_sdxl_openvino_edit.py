"""Tests for SDXL OpenVINO edit (img2img) support."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from PIL import Image

from inference.base import EditParams
from inference.sdxl_openvino import (
    DEFAULT_EDIT_STRENGTH,
    SDXLOpenVINORunner,
    _SDXLOVPipelines,
    _fit_image,
)


class FitImageTest(unittest.TestCase):
    def test_already_within_limits_keeps_size(self) -> None:
        image = Image.new("RGB", (512, 384), color=(10, 20, 30))
        fitted = _fit_image(image, 768, 768)
        self.assertEqual(fitted.size, (512, 384))

    def test_downscales_and_aligns_to_8(self) -> None:
        image = Image.new("RGB", (2000, 1000), color=(10, 20, 30))
        fitted = _fit_image(image, 768, 768)
        self.assertLessEqual(fitted.size[0], 768)
        self.assertLessEqual(fitted.size[1], 768)
        self.assertEqual(fitted.size[0] % 8, 0)
        self.assertEqual(fitted.size[1] % 8, 0)

    def test_converts_to_rgb(self) -> None:
        image = Image.new("RGBA", (64, 64), color=(10, 20, 30, 128))
        fitted = _fit_image(image, 768, 768)
        self.assertEqual(fitted.mode, "RGB")


class SDXLOpenVINOEditTest(unittest.TestCase):
    def test_capabilities_include_edit(self) -> None:
        runner = SDXLOpenVINORunner()
        self.assertEqual(runner.capabilities, {"t2i", "edit"})
        self.assertEqual(runner.edit_input_limit, 1)
        self.assertEqual(runner.defaults.get("strength"), DEFAULT_EDIT_STRENGTH)

    def test_edit_requires_exactly_one_image(self) -> None:
        runner = SDXLOpenVINORunner()
        params = EditParams(
            prompt="soften skin",
            image_ids=["a", "b"],
            seed=1,
            steps=4,
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            runner.edit(params)

    def test_edit_calls_img2img_with_strength_and_prompt(self) -> None:
        runner = SDXLOpenVINORunner()
        fake_img2img = MagicMock()
        fake_img2img.return_value = MagicMock(images=[Image.new("RGB", (64, 64))])

        pipes = _SDXLOVPipelines(base=MagicMock(), refiner=None, img2img=None)
        with (
            TemporaryDirectory() as tmp,
            patch.object(runner, "load", return_value=pipes),
            patch.object(runner, "_ensure_img2img", return_value=fake_img2img),
            patch(
                "inference.sdxl_openvino.image_store.load_image",
                return_value=Image.new("RGB", (640, 480)),
            ),
            patch("inference.sdxl_openvino.seed_everything", return_value="gen"),
        ):
            image_path = Path(tmp) / "in.png"
            image_path.write_bytes(b"unused")
            params = EditParams(
                prompt="natural editorial retouch",
                image_ids=["img-1"],
                seed=42,
                steps=8,
                strength=0.55,
                guidance_scale=5.0,
            )
            result = runner.edit(params)

        self.assertIsInstance(result, Image.Image)
        fake_img2img.assert_called_once()
        kwargs = fake_img2img.call_args.kwargs
        self.assertEqual(kwargs["prompt"], "natural editorial retouch")
        self.assertEqual(kwargs["strength"], 0.55)
        self.assertEqual(kwargs["num_inference_steps"], 8)
        self.assertEqual(kwargs["guidance_scale"], 5.0)
        self.assertIsInstance(kwargs["image"], Image.Image)

    def test_edit_defaults_strength_when_unset(self) -> None:
        runner = SDXLOpenVINORunner()
        fake_img2img = MagicMock()
        fake_img2img.return_value = MagicMock(images=[Image.new("RGB", (32, 32))])
        pipes = _SDXLOVPipelines(base=MagicMock(), refiner=None, img2img=None)
        with (
            patch.object(runner, "load", return_value=pipes),
            patch.object(runner, "_ensure_img2img", return_value=fake_img2img),
            patch(
                "inference.sdxl_openvino.image_store.load_image",
                return_value=Image.new("RGB", (256, 256)),
            ),
            patch("inference.sdxl_openvino.seed_everything", return_value="gen"),
        ):
            params = EditParams(
                prompt="cleanup",
                image_ids=["img-1"],
                seed=7,
                steps=4,
            )
            runner.edit(params)

        self.assertEqual(
            fake_img2img.call_args.kwargs["strength"], DEFAULT_EDIT_STRENGTH
        )


if __name__ == "__main__":
    unittest.main()
