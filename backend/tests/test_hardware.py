from __future__ import annotations

import unittest

from app import hardware


def _cpu_box(**overrides):
    hw = {
        "has_cuda": False,
        "vram_gb": None,
        "device_name": None,
        "ram_gb": 64.0,
        "disk_free_gb": 200.0,
        "cpu_logical": 28,
        "os": "Windows",
        "arch": "AMD64",
        "openvino_devices": ["CPU", "GPU"],
    }
    hw.update(overrides)
    return hw


def _gpu_box(**overrides):
    base = {"has_cuda": True, "vram_gb": 24.0, "device_name": "RTX 4090"}
    base.update(overrides)
    return _cpu_box(**base)


class EvaluateModelTest(unittest.TestCase):
    def test_qwen_needs_gpu_on_cpu_box(self) -> None:
        req = hardware.REQ_BY_ID["qwen-image-edit-2511"]
        verdict, _ = hardware.evaluate_model(req, _cpu_box())
        self.assertEqual(verdict, "needs_gpu")

    def test_sdxl_recommended_on_cpu_box(self) -> None:
        req = hardware.REQ_BY_ID["sdxl-openvino"]
        verdict, _ = hardware.evaluate_model(req, _cpu_box())
        self.assertEqual(verdict, "recommended")

    def test_flux_usable_slow_on_cpu_box(self) -> None:
        req = hardware.REQ_BY_ID["flux2-klein-9b-gguf"]
        verdict, _ = hardware.evaluate_model(req, _cpu_box())
        self.assertEqual(verdict, "usable_slow")

    def test_qwen_recommended_on_gpu_box(self) -> None:
        req = hardware.REQ_BY_ID["qwen-image-2512"]
        verdict, _ = hardware.evaluate_model(req, _gpu_box())
        self.assertEqual(verdict, "recommended")

    def test_qwen_needs_gpu_when_vram_too_small(self) -> None:
        req = hardware.REQ_BY_ID["qwen-image-2512"]
        verdict, _ = hardware.evaluate_model(req, _gpu_box(vram_gb=8.0))
        self.assertEqual(verdict, "needs_gpu")

    def test_disk_gate_blocks_download(self) -> None:
        req = hardware.REQ_BY_ID["sdxl-openvino"]
        verdict, _ = hardware.evaluate_model(req, _cpu_box(disk_free_gb=2.0))
        self.assertEqual(verdict, "needs_more_disk")

    def test_low_ram_blocks_flux(self) -> None:
        req = hardware.REQ_BY_ID["flux2-klein-9b-gguf"]
        verdict, _ = hardware.evaluate_model(req, _cpu_box(ram_gb=8.0))
        self.assertEqual(verdict, "needs_more_ram")


class RecommendTest(unittest.TestCase):
    def test_best_choice_is_sdxl_on_cpu_box(self) -> None:
        result = hardware.recommend(_cpu_box())
        self.assertEqual(result["best_choice"], "sdxl-openvino")
        self.assertIn("Best local pick", result["summary"])
        # models sorted best-first
        self.assertEqual(result["models"][0]["id"], "sdxl-openvino")

    def test_best_choice_is_qwen_on_gpu_box(self) -> None:
        result = hardware.recommend(_gpu_box())
        # On a strong GPU the frontier models become recommended and rank first.
        recommended = {
            m["id"] for m in result["models"] if m["verdict"] == "recommended"
        }
        self.assertIn("qwen-image-edit-2511", recommended)
        self.assertIn("qwen-image-2512", recommended)

    def test_every_model_has_a_verdict(self) -> None:
        result = hardware.recommend(_cpu_box())
        ids = {m["id"] for m in result["models"]}
        self.assertEqual(ids, set(hardware.REQ_BY_ID))
        for m in result["models"]:
            self.assertIn(m["verdict"], hardware.VERDICT_RANK)


class HardwareEndpointTest(unittest.TestCase):
    def test_api_hardware_endpoint(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        with TestClient(app) as client:
            resp = client.get("/api/hardware")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("hardware", body)
        self.assertIn("models", body)
        self.assertIn("summary", body)
        self.assertTrue(len(body["models"]) >= 4)


if __name__ == "__main__":
    unittest.main()
