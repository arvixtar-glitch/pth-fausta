import json
import logging
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.config import AppConfig
from app.core.paths import ProjectPaths
from app.core.settings import AppSettings, SettingsManager


class ConfigTests(unittest.TestCase):
    def _create_temp_project_structure(self, root: Path) -> None:
        (root / "src" / "app" / "core").mkdir(parents=True)
        (root / "database").mkdir()
        (root / "docs").mkdir()
        (root / "resources").mkdir()
        (root / "tests").mkdir()

    def test_app_config_initializes_components(self) -> None:
        temp_dir = TemporaryDirectory()
        try:
            root = Path(temp_dir.name)
            self._create_temp_project_structure(root)
            with patch("app.core.config.ProjectPaths", new=lambda: ProjectPaths(project_root=root)):
                config = AppConfig()

            self.assertIsInstance(config.paths, ProjectPaths)
            self.assertIsInstance(config.settings_manager, SettingsManager)
            self.assertEqual(config.settings, AppSettings())
            self.assertEqual(config.logger.name, "app.config")
        finally:
            logger = logging.getLogger("app")
            managed_handlers = [
                handler for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)
            ]
            for handler in managed_handlers:
                logger.removeHandler(handler)
                handler.close()
            temp_dir.cleanup()

    def test_save_settings_persists_changes(self) -> None:
        temp_dir = TemporaryDirectory()
        try:
            root = Path(temp_dir.name)
            self._create_temp_project_structure(root)
            with patch("app.core.config.ProjectPaths", new=lambda: ProjectPaths(project_root=root)):
                config = AppConfig()
                config.settings.theme = "dark"
                config.save_settings()

            settings_file = root / "database" / "settings.json"
            self.assertTrue(settings_file.exists())
            loaded = json.loads(settings_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["theme"], "dark")
        finally:
            logger = logging.getLogger("app")
            managed_handlers = [
                handler for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)
            ]
            for handler in managed_handlers:
                logger.removeHandler(handler)
                handler.close()
            temp_dir.cleanup()

    def test_settings_are_loaded_from_file(self) -> None:
        temp_dir = TemporaryDirectory()
        try:
            root = Path(temp_dir.name)
            self._create_temp_project_structure(root)
            settings_path = root / "database" / "settings.json"
            settings_path.write_text(json.dumps({"language": "en", "theme": "light", "auto_save": False}), encoding="utf-8")

            with patch("app.core.config.ProjectPaths", new=lambda: ProjectPaths(project_root=root)):
                config = AppConfig()

            self.assertEqual(config.settings.language, "en")
            self.assertEqual(config.settings.theme, "light")
            self.assertFalse(config.settings.auto_save)
        finally:
            logger = logging.getLogger("app")
            managed_handlers = [
                handler for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)
            ]
            for handler in managed_handlers:
                logger.removeHandler(handler)
                handler.close()
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
