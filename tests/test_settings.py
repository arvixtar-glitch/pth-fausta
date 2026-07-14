import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.paths import ProjectPaths
from app.core.settings import AppSettings, SettingsError, SettingsManager


class SettingsTests(unittest.TestCase):
    def test_default_app_settings(self) -> None:
        settings = AppSettings()

        self.assertEqual(settings.language, "lt")
        self.assertEqual(settings.theme, "system")
        self.assertTrue(settings.auto_save)

    def test_validate_accepts_allowed_values(self) -> None:
        settings = AppSettings(language="en", theme="dark", auto_save=False)
        settings.validate()

    def test_validate_rejects_invalid_language(self) -> None:
        with self.assertRaises(ValueError) as context:
            AppSettings(language="jp").validate()
        self.assertIn("language", str(context.exception))

    def test_validate_rejects_invalid_theme(self) -> None:
        with self.assertRaises(ValueError) as context:
            AppSettings(theme="blue").validate()
        self.assertIn("theme", str(context.exception))

    def test_validate_rejects_non_bool_auto_save(self) -> None:
        settings = AppSettings(auto_save=1)  # type: ignore[arg-type]
        with self.assertRaises(ValueError) as context:
            settings.validate()
        self.assertIn("auto_save", str(context.exception))

    def test_from_dict_uses_default_values_for_missing_keys(self) -> None:
        data = {"language": "en"}
        settings = AppSettings.from_dict(data)

        self.assertEqual(settings.language, "en")
        self.assertEqual(settings.theme, "system")
        self.assertTrue(settings.auto_save)

    def test_from_dict_ignores_unknown_keys(self) -> None:
        data = {"language": "lt", "theme": "light", "auto_save": True, "extra": 123}
        settings = AppSettings.from_dict(data)

        self.assertEqual(settings.language, "lt")
        self.assertEqual(settings.theme, "light")
        self.assertTrue(settings.auto_save)

    def test_load_returns_defaults_when_file_missing(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            paths = ProjectPaths(project_root=Path(tmp_dir))
            manager = SettingsManager(paths)

            loaded = manager.load()

            self.assertEqual(loaded, AppSettings())
            self.assertFalse(manager.file_path.exists())

    def test_save_creates_valid_utf8_json_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)
            settings = AppSettings(language="en", theme="dark", auto_save=False)

            manager.save(settings)

            self.assertTrue(manager.file_path.exists())
            content = manager.file_path.read_text(encoding="utf-8")
            parsed = json.loads(content)
            self.assertEqual(parsed, settings.to_dict())
            self.assertFalse((database_dir / "settings.json.tmp").exists())

    def test_save_and_load_round_trip(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)
            settings = AppSettings(language="en", theme="light", auto_save=True)

            manager.save(settings)
            loaded = manager.load()

            self.assertEqual(loaded, settings)

    def test_load_raises_settings_error_for_invalid_json(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()
            file_path = database_dir / "settings.json"
            file_path.write_text("{ invalid json }", encoding="utf-8")

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)

            with self.assertRaises(SettingsError) as context:
                manager.load()
            self.assertIn("Invalid JSON", str(context.exception))

    def test_load_raises_settings_error_for_json_array_root(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()
            file_path = database_dir / "settings.json"
            file_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)

            with self.assertRaises(SettingsError) as context:
                manager.load()
            self.assertIn("root must be an object", str(context.exception))

    def test_load_raises_settings_error_for_invalid_value(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()
            file_path = database_dir / "settings.json"
            file_path.write_text(json.dumps({"language": "jp"}), encoding="utf-8")

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)

            with self.assertRaises(SettingsError) as context:
                manager.load()
            self.assertIn("Invalid settings values", str(context.exception))

    def test_reset_saves_and_returns_default_settings(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            database_dir = root / "database"
            database_dir.mkdir()

            paths = ProjectPaths(project_root=root)
            manager = SettingsManager(paths)

            reset_settings = manager.reset()

            self.assertEqual(reset_settings, AppSettings())
            self.assertTrue(manager.file_path.exists())
            self.assertEqual(manager.load(), AppSettings())


if __name__ == "__main__":
    unittest.main()
