from __future__ import annotations

from typing import Callable

import torch
from diffusers import DiffusionPipeline
from PIL import Image

from app import model_registry
from inference.base import GenerationParams, Runner, EditParams, seed_everything


class QwenImage2512Runner(Runner):
    id = "qwen-image-2512"
    capabilities = {"t2i"}

    def _load_pipeline(self) -> DiffusionPipeline:
        local_path = model_registry.resolve_model_path(self.id)
        return DiffusionPipeline.from_pretrained(
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
        pipe = self.load()
        generator = seed_everything(params.seed, self.device)
        true_cfg_scale = params.true_cfg_scale if params.true_cfg_scale is not None else 1.0

        kwargs: dict[str, object] = {
            "prompt": params.prompt,
            "num_inference_steps": params.steps,
            "width": params.width,
            "height": params.height,
            "generator": generator,
            "true_cfg_scale": true_cfg_scale,
        }
        if params.negative_prompt:
            kwargs["negative_prompt"] = params.negative_prompt
        if params.guidance_scale is not None:
            kwargs["guidance_scale"] = params.guidance_scale

        kwargs = self._inject_progress_callback(pipe, kwargs, params.steps, progress_callback)

        with torch.inference_mode():
            result = pipe(**kwargs)
        return result.images[0]

    def edit(
        self,
        params: EditParams,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Image.Image:
        raise NotImplementedError("Edit is not supported by this runner.")
