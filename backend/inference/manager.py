from __future__ import annotations

from typing import Dict, List

from app import config
from inference.base import Runner
from inference.flux2_klein_gguf import Flux2KleinGGUFRunner
from inference.qwen_image_2512 import QwenImage2512Runner
from inference.qwen_image_edit_2511 import QwenImageEdit2511Runner
from inference.sdxl_openvino import SDXLOpenVINORunner


class InferenceManager:
    def __init__(self) -> None:
        runners: list[Runner] = [
            QwenImage2512Runner(),
            QwenImageEdit2511Runner(),
            Flux2KleinGGUFRunner(),
            SDXLOpenVINORunner(),
        ]
        if config.ENABLED_MODELS:
            runners = [runner for runner in runners if runner.id in config.ENABLED_MODELS]
        self._runners = {runner.id: runner for runner in runners}

    def get_runner(self, model_id: str) -> Runner:
        if model_id not in self._runners:
            raise KeyError(f"Unknown model id '{model_id}'.")
        return self._runners[model_id]

    def list_models(self) -> List[dict]:
        output = []
        for runner in self._runners.values():
            status = runner.model_status()
            review_mode = "off"
            if runner.manual_review:
                review_mode = config.SAFETY_REVIEW_MODE
            output.append(
                {
                    "id": runner.id,
                    "label": runner.label or runner.id,
                    "capabilities": sorted(runner.capabilities),
                    "present": bool(status.get("present", False)),
                    "local_path": status.get("local_path"),
                    "revision": status.get("revision"),
                    "defaults": runner.defaults or {},
                    "review_mode": review_mode,
                }
            )
        return output

    def warmup_all(self) -> None:
        for runner in self._runners.values():
            status = runner.model_status()
            if status.get("present", True):
                runner.load()


_MANAGER = InferenceManager()


def get_manager() -> InferenceManager:
    return _MANAGER
