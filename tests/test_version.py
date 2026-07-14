import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.version import (
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_VERSION,
    AppVersion,
)


class VersionTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(APP_NAME, "pth_fausta")
        self.assertEqual(APP_DISPLAY_NAME, "PTH Fausta")
        self.assertEqual(APP_VERSION, "0.1.0")

    def test_parse_returns_expected_app_version(self) -> None:
        self.assertEqual(AppVersion.parse("0.1.0"), AppVersion(0, 1, 0))

    def test_str_returns_major_minor_patch(self) -> None:
        self.assertEqual(str(AppVersion(1, 2, 3)), "1.2.3")

    def test_parse_accepts_zero_version(self) -> None:
        self.assertEqual(AppVersion.parse("0.0.0"), AppVersion(0, 0, 0))

    def test_parse_rejects_invalid_version_formats(self) -> None:
        invalid_versions = [
            "1",
            "1.2",
            "1.2.3.4",
            "v1.2.3",
            "1.a.3",
            "-1.2.3",
            "1..3",
            "",
        ]

        for version in invalid_versions:
            with self.subTest(version=version):
                with self.assertRaises(ValueError) as context:
                    AppVersion.parse(version)
                self.assertIn("expected format", str(context.exception))
                self.assertIn(version, str(context.exception))

    def test_constructor_rejects_bool_values(self) -> None:
        with self.assertRaises(ValueError):
            AppVersion(True, 0, 0)

    def test_constructor_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            AppVersion(-1, 0, 0)

    def test_app_version_constant_is_valid(self) -> None:
        self.assertEqual(AppVersion.parse(APP_VERSION), AppVersion(0, 1, 0))


if __name__ == "__main__":
    unittest.main()
