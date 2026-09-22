"""Model folder confirmation. No downloads."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import config, model_location


class ModelLocationTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._original_dir = config.SDXL_OV_BASE_DIR
        self.addCleanup(lambda: setattr(config, "SDXL_OV_BASE_DIR", self._original_dir))
        model_location.set_store_path(Path(self._tmp.name) / "location.json")
        self.addCleanup(lambda: model_location.set_store_path(None))

    def test_suggests_the_repo_default_until_confirmed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SDXL_OV_BASE_DIR", None)
            info = model_location.describe()
        self.assertFalse(info["confirmed"])
        self.assertFalse(info["locked_by_env"])
        self.assertEqual(info["source"], "default")
        self.assertTrue(info["path"].endswith(str(Path("models") / "openvino" / "sdxl_base")))

    def test_confirm_saves_and_points_the_runtime_at_that_folder(self) -> None:
        os.environ.pop("SDXL_OV_BASE_DIR", None)
        chosen = Path(self._tmp.name) / "custom" / "sdxl"
        info = model_location.confirm(str(chosen))
        self.assertTrue(info["confirmed"])
        self.assertEqual(info["source"], "settings")
        self.assertEqual(Path(info["path"]), chosen.resolve())
        self.assertEqual(config.SDXL_OV_BASE_DIR, chosen.resolve())
        again = model_location.describe()
        self.assertEqual(again["path"], info["path"])

    def test_env_var_locks_the_folder(self) -> None:
        locked = Path(self._tmp.name) / "from-env"
        with mock.patch.dict(os.environ, {"SDXL_OV_BASE_DIR": str(locked)}):
            info = model_location.describe()
            self.assertTrue(info["locked_by_env"])
            self.assertTrue(info["confirmed"])
            self.assertEqual(Path(info["path"]), locked.resolve())
            with self.assertRaises(ValueError):
                model_location.confirm(str(Path(self._tmp.name) / "other"))


if __name__ == "__main__":
    unittest.main()
