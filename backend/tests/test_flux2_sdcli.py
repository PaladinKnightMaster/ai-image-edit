from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import config
from inference.flux2_klein_gguf import Flux2Assets, _Flux2SdCliBackend


class Flux2SdCliArgsTest(unittest.TestCase):
    def test_sdcli_requires_text_encoder_gguf(self) -> None:
        assets = Flux2Assets(
            model_dir=Path("models/flux2_klein_9b_gguf"),
            diffusion_gguf=Path("diffusion.gguf"),
            vae=Path("vae.safetensors"),
            text_encoder=Path("text_encoder.safetensors"),
            text_encoder_gguf=None,
            llm_gguf=None,
        )
        backend = _Flux2SdCliBackend(assets)
        with self.assertRaises(RuntimeError):
            backend._build_args(
                prompt="test",
                negative_prompt=None,
                width=512,
                height=512,
                steps=4,
                guidance=4.0,
                seed=123,
                output_path=Path("out.png"),
            )

    def test_sdcli_builds_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text_gguf = Path(tmp) / "text_encoder.gguf"
            assets = Flux2Assets(
                model_dir=Path(tmp),
                diffusion_gguf=Path(tmp) / "diffusion.gguf",
                vae=Path(tmp) / "vae.safetensors",
                text_encoder=Path(tmp) / "text_encoder.safetensors",
                text_encoder_gguf=text_gguf,
                llm_gguf=None,
            )
            backend = _Flux2SdCliBackend(assets)
            original_extra = config.FLUX2_SDCLI_EXTRA_ARGS
            config.FLUX2_SDCLI_EXTRA_ARGS = "--foo bar"
            try:
                args = backend._build_args(
                    prompt="test",
                    negative_prompt="bad",
                    width=512,
                    height=512,
                    steps=4,
                    guidance=4.0,
                    seed=123,
                    output_path=Path(tmp) / "out.png",
                )
            finally:
                config.FLUX2_SDCLI_EXTRA_ARGS = original_extra

            self.assertIn("--diffusion-model", args)
            self.assertIn(str(assets.diffusion_gguf), args)
            self.assertIn("--vae", args)
            self.assertIn(str(assets.vae), args)
            self.assertIn("--llm", args)
            self.assertIn(str(text_gguf), args)
            self.assertIn("-p", args)
            self.assertIn("test", args)


if __name__ == "__main__":
    unittest.main()
