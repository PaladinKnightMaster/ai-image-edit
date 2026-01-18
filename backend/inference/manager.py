from __future__ import annotations

from typing import Dict, List

from app import model_registry
from inference.base import Runner
from inference.qwen_image_2512 import QwenImage2512Runner
from inference.qwen_image_edit_2511 import QwenImageEdit2511Runner


class InferenceManager:
    def __init__(self) -> None:
        self._runners: Dict[str, Runner] = {
            QwenImage2512Runner.id: QwenImage2512Runner(),
            QwenImageEdit2511Runner.id: QwenImageEdit2511Runner(),
        }

    def get_runner(self, model_id: str) -> Runner:
        if model_id not in self._runners:
            raise KeyError(f"Unknown model id '{model_id}'.")
        return self._runners[model_id]

    def list_models(self) -> List[dict]:
        local_status = {item["id"]: item for item in model_registry.list_models()}
        output = []
        for runner in self._runners.values():
            status = local_status.get(runner.id, {})
            output.append(
                {
                    "id": runner.id,
                    "capabilities": sorted(runner.capabilities),
                    "present": status.get("present", False),
                    "local_path": status.get("local_path"),
                    "revision": status.get("revision"),
                }
            )
        return output

    def warmup_all(self) -> None:
        for runner in self._runners.values():
            runner.load()


_MANAGER = InferenceManager()


def get_manager() -> InferenceManager:
    return _MANAGER
