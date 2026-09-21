"""Regression tests for wrapped-pipeline backends (e.g. Optimum Intel OpenVINO).

Optimum Intel exposes its pipelines as `__call__(self, *args, **kwargs)`, which hides
the real parameters from `inspect.signature`. Two code paths used to break on that:

1. `_filter_kwargs` filtered every argument away (including `prompt`).
2. `_inject_progress_callback` found no callback parameter, so progress never fired.

Additionally, OpenVINO pipelines expose `enable_vae_slicing()` but cannot apply it,
which raised `AttributeError` during model load.
"""

from __future__ import annotations

import unittest
from unittest import mock

from inference import base as runner_base
from inference.sdxl_openvino import _filter_kwargs


class _KwargsPipe:
    """Mimics Optimum Intel: real params hidden behind *args/**kwargs."""

    def __call__(self, *args, **kwargs):
        return kwargs


class _ExplicitPipe:
    def __call__(self, prompt=None, num_inference_steps=None):
        return prompt


class _StubRunner(runner_base.Runner):
    id = "stub"
    capabilities = {"t2i"}

    def _load_pipeline(self):
        raise NotImplementedError

    def generate(self, params, progress_callback=None):
        raise NotImplementedError

    def edit(self, params, progress_callback=None):
        raise NotImplementedError


class _UnsupportedOptimizationPipe:
    def enable_attention_slicing(self):
        raise AttributeError("'OVModelVae' object has no attribute 'enable_slicing'")

    def enable_vae_slicing(self):
        raise AttributeError("'OVModelVae' object has no attribute 'enable_slicing'")


class FilterKwargsTest(unittest.TestCase):
    def test_passthrough_signature_keeps_all_kwargs(self) -> None:
        kwargs = {"prompt": "a cat", "num_inference_steps": 8, "width": 768}
        self.assertEqual(_filter_kwargs(_KwargsPipe().__call__, kwargs), kwargs)

    def test_explicit_signature_still_filters_unknown_kwargs(self) -> None:
        kwargs = {"prompt": "a cat", "bogus_param": 1}
        self.assertEqual(
            _filter_kwargs(_ExplicitPipe().__call__, kwargs), {"prompt": "a cat"}
        )


class MemoryOptimizationTest(unittest.TestCase):
    def test_unsupported_backend_does_not_block_load(self) -> None:
        runner = _StubRunner()
        with (
            mock.patch.object(runner_base.config, "ENABLE_ATTENTION_SLICING", True),
            mock.patch.object(runner_base.config, "ENABLE_VAE_SLICING", True),
            mock.patch.object(runner_base.config, "ENABLE_VAE_TILING", False),
        ):
            # Must not raise even though the backend rejects both optimizations.
            runner._apply_memory_optimizations(_UnsupportedOptimizationPipe())


class ProgressCallbackTest(unittest.TestCase):
    def test_wrapped_pipe_gets_modern_callback(self) -> None:
        runner = _StubRunner()
        kwargs = runner._inject_progress_callback(
            _KwargsPipe(), {}, 8, lambda step, total: None
        )
        self.assertIn("callback_on_step_end", kwargs)

    def test_missing_callback_leaves_kwargs_untouched(self) -> None:
        runner = _StubRunner()
        self.assertEqual(
            runner._inject_progress_callback(_KwargsPipe(), {"a": 1}, 8, None), {"a": 1}
        )


if __name__ == "__main__":
    unittest.main()
