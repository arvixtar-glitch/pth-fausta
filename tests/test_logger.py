import logging
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.logger import configure_logging, get_logger
from app.core.paths import ProjectPaths


class LoggerTests(unittest.TestCase):
    def tearDown(self) -> None:
        logger = logging.getLogger("app")
        managed_handlers = [
            handler for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)
        ]
        for handler in managed_handlers:
            logger.removeHandler(handler)
            handler.close()

    def _cleanup_app_logger(self) -> None:
        logger = logging.getLogger("app")
        managed_handlers = [
            handler for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)
        ]
        for handler in managed_handlers:
            logger.removeHandler(handler)
            handler.close()

    def test_get_logger_returns_app_child(self) -> None:
        self.assertEqual(get_logger("services.invoice").name, "app.services.invoice")
        self.assertEqual(get_logger("").name, "app")
        self.assertEqual(get_logger("app.services.invoice").name, "app.services.invoice")
        self.assertEqual(get_logger("app").name, "app")

    def test_configure_logging_creates_runtime_directory_and_file_handler(self) -> None:
        temp_dir = TemporaryDirectory()
        try:
            root_path = Path(temp_dir.name)
            paths = ProjectPaths(project_root=root_path)

            configure_logging(paths, level=logging.DEBUG, console_enabled=False)

            logger = logging.getLogger("app")
            self.assertEqual(logger.level, logging.DEBUG)
            self.assertFalse(logger.propagate)
            self.assertTrue(paths.logs.is_dir())
            self.assertTrue((paths.logs / "app.log").exists())

            file_handlers = [
                handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
            ]
            self.assertEqual(len(file_handlers), 1)
            self.assertFalse(
                any(type(handler) is logging.StreamHandler for handler in logger.handlers)
            )
        finally:
            self._cleanup_app_logger()
            temp_dir.cleanup()

    def test_configure_logging_is_idempotent(self) -> None:
        temp_dir = TemporaryDirectory()
        try:
            root_path = Path(temp_dir.name)
            paths = ProjectPaths(project_root=root_path)

            configure_logging(paths, console_enabled=True)
            logger = logging.getLogger("app")
            self.assertEqual(sum(1 for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)), 2)

            configure_logging(paths, console_enabled=False)
            logger = logging.getLogger("app")
            self.assertEqual(sum(1 for handler in logger.handlers if getattr(handler, "_app_core_logger_handler", False)), 1)
            self.assertEqual(sum(1 for handler in logger.handlers if isinstance(handler, logging.FileHandler)), 1)
        finally:
            self._cleanup_app_logger()
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
