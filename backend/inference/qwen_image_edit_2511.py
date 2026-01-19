from __future__ import annotations

from typing import Callable

import torch
from diffusers import QwenImageEditPlusPipeline
from PIL import Image

from app import config, images as image_store, model_registry
from inference.base import EditParams, GenerationParams, Runner, seed_everything


class QwenImageEdit2511Runner(Runner):
    id = "qwen-image-edit-2511"
    label = "Qwen Image Edit 2511"
    capabilities = {"edit"}
    defaults = {
        "steps": config.DEFAULT_STEPS,
        "guidance_scale": None,
        "true_cfg_scale": None,
    }

    def model_status(self) -> dict[str, object]:
        return model_registry.get_model_status(self.id)

    def _load_pipeline(self) -> QwenImageEditPlusPipeline:
        local_path = model_registry.resolve_model_path(self.id)
        return QwenImageEditPlusPipeline.from_pretrained(
            local_path,
            torch_dtype=self.dtype,
            local_files_only=True,
            low_cpu_mem_usage=True,
        )

    def generate(
        self,
        params: GenerationParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        raise NotImplementedError("Text-to-image is not supported by this runner.")

    def edit(
        self,
        params: EditParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        pipe = self.load()
        input_images = [image_store.load_image(image_id) for image_id in params.image_ids]
        if not 1 <= len(input_images) <= 2:
            raise ValueError("Expected 1 or 2 input images for edit.")
        generator = seed_everything(params.seed, self.device)
        true_cfg_scale = params.true_cfg_scale if params.true_cfg_scale is not None else 1.0

        kwargs: dict[str, object] = {
            "prompt": params.prompt,
            "image": input_images,
            "num_inference_steps": params.steps,
            "generator": generator,
            "true_cfg_scale": true_cfg_scale,
        }
        if params.guidance_scale is not None:
            kwargs["guidance_scale"] = params.guidance_scale

        kwargs = self._inject_progress_callback(pipe, kwargs, params.steps, progress_callback)

        with torch.inference_mode():
            result = pipe(**kwargs)
        return result.images[0]
