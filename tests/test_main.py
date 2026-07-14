import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app.main as app_main


class MainTests(unittest.TestCase):
    def test_main_creates_application_and_executes_it(self) -> None:
        with patch("app.main.Application") as application_class:
            application = application_class.return_value
            application.execute.return_value = 7

            result = app_main.main()

            application_class.assert_called_once_with()
            application.execute.assert_called_once_with()
            self.assertEqual(result, 7)

    def test_importing_app_main_does_not_run_program(self) -> None:
        self.assertTrue(hasattr(app_main, "main"))

    def test_main_propagates_application_init_exception(self) -> None:
        with patch("app.main.Application", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                app_main.main()

    def test_main_propagates_execute_exception(self) -> None:
        with patch("app.main.Application") as application_class:
            application = application_class.return_value
            application.execute.side_effect = ValueError("boom")

            with self.assertRaises(ValueError):
                app_main.main()


if __name__ == "__main__":
    unittest.main()
