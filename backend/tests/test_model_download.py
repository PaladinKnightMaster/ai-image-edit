"""In-app model download policy. No network and no real weights."""

from __future__ import annotations

import unittest
from pathlib import Path

from app import config, hardware, model_download


def _advice(model_id: str, *, present: bool, downloadable: bool, reason: str = "ok") -> dict:
    return {
        "models": [
            {
                "id": model_id,
                "present": present,
                "downloadable": downloadable,
                "reason": reason,
            }
        ]
    }


class ModelDownloadPolicyTest(unittest.TestCase):
    def tearDown(self) -> None:
        model_download._set(
            model_id=None,
            status="idle",
            bytes_downloaded=0,
            bytes_total=None,
            message="",
            error=None,
        )

    def test_refuses_models_without_an_in_app_recipe(self) -> None:
        with self.assertRaises(ValueError):
            model_download.start_download(
                "qwen-image-2512",
                advice=_advice("qwen-image-2512", present=False, downloadable=False),
                background=False,
            )
        with self.assertRaises(ValueError):
            model_download.start_download(
                "flux2-klein-9b-gguf",
                advice=_advice("flux2-klein-9b-gguf", present=False, downloadable=True),
                background=False,
            )

    def test_refuses_sdxl_when_hardware_says_not_downloadable(self) -> None:
        with self.assertRaises(ValueError) as caught:
            model_download.start_download(
                "sdxl-openvino",
                advice=_advice(
                    "sdxl-openvino",
                    present=False,
                    downloadable=False,
                    reason="Needs more disk",
                ),
                background=False,
            )
        self.assertIn("disk", str(caught.exception).lower())

    def test_sdxl_download_reports_progress_and_completes(self) -> None:
        import tempfile

        from app import model_location

        seen: list[tuple[int, int | None]] = []

        def fetcher(repo_id: str, local_dir: Path, on_progress) -> None:
            self.assertEqual(repo_id, model_download.SDXL_OPENVINO_REPO)
            local_dir.mkdir(parents=True, exist_ok=True)
            on_progress(10, 100)
            on_progress(100, 100)
            seen.append((100, 100))

        with tempfile.TemporaryDirectory() as tmp:
            model_location.set_store_path(Path(tmp) / "location.json")
            previous = config.SDXL_OV_BASE_DIR
            target = Path(tmp) / "sdxl_base"
            model_location.confirm(str(target))
            try:
                result = model_download.start_download(
                    "sdxl-openvino",
                    advice=_advice("sdxl-openvino", present=False, downloadable=True),
                    fetcher=fetcher,
                    background=False,
                )
            finally:
                config.SDXL_OV_BASE_DIR = previous
                model_location.set_store_path(None)
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["bytes_downloaded"], 100)
        self.assertEqual(result["bytes_total"], 100)
        self.assertTrue(seen)

    def test_download_requires_a_confirmed_folder(self) -> None:
        import tempfile

        from app import model_location

        with tempfile.TemporaryDirectory() as tmp:
            model_location.set_store_path(Path(tmp) / "location.json")
            with self.assertRaises(ValueError) as caught:
                model_download.start_download(
                    "sdxl-openvino",
                    advice=_advice("sdxl-openvino", present=False, downloadable=True),
                    background=False,
                )
        model_location.set_store_path(None)
        self.assertIn("Confirm", str(caught.exception))

    def test_already_present_does_not_fetch(self) -> None:
        def fetcher(*_args) -> None:
            raise AssertionError("fetcher should not run")

        result = model_download.start_download(
            "sdxl-openvino",
            advice=_advice("sdxl-openvino", present=True, downloadable=True),
            fetcher=fetcher,
            background=False,
        )
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["message"], "Already on disk.")

    def test_cpu_recommendation_marks_only_sdxl_in_app(self) -> None:
        result = hardware.recommend(
            {
                "has_cuda": False,
                "vram_gb": None,
                "ram_gb": 64.0,
                "disk_free_gb": 200.0,
                "openvino_devices": ["CPU"],
            }
        )
        flags = {item["id"]: item["in_app_download"] for item in result["models"]}
        self.assertTrue(flags["sdxl-openvino"])
        self.assertFalse(flags["flux2-klein-9b-gguf"])
        self.assertFalse(flags["qwen-image-2512"])


if __name__ == "__main__":
    unittest.main()
