import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.app import Application


class DummyLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)


class DummyConfig:
    def __init__(self) -> None:
        self.logger = DummyLogger()


class ApplicationTests(unittest.TestCase):
    def test_uses_provided_config(self) -> None:
        config = DummyConfig()
        application = Application(config)

        self.assertIs(application.config, config)

    def test_uses_config_logger(self) -> None:
        config = DummyConfig()
        application = Application(config)

        self.assertIs(application.logger, config.logger)

    def test_run_returns_zero(self) -> None:
        application = Application(DummyConfig())

        self.assertEqual(application.run(), 0)

    def test_run_logs_application_name_and_version(self) -> None:
        config = DummyConfig()
        application = Application(config)

        application.run()

        self.assertIn("Starting PTH Fausta 0.1.0.", config.logger.messages)

    def test_run_logs_ready_message(self) -> None:
        config = DummyConfig()
        application = Application(config)

        application.run()

        self.assertIn("Application is ready.", config.logger.messages)

    def test_shutdown_logs_shutdown_message(self) -> None:
        config = DummyConfig()
        application = Application(config)

        application.shutdown()

        self.assertIn("Application shutdown completed.", config.logger.messages)

    def test_execute_invokes_run(self) -> None:
        config = DummyConfig()
        application = Application(config)
        application.run = Mock(return_value=0)  # type: ignore[assignment]

        self.assertEqual(application.execute(), 0)
        application.run.assert_called_once_with()

    def test_execute_always_invokes_shutdown(self) -> None:
        config = DummyConfig()
        application = Application(config)
        application.run = Mock(side_effect=RuntimeError("boom"))  # type: ignore[assignment]
        application.shutdown = Mock()  # type: ignore[assignment]

        with self.assertRaises(RuntimeError):
            application.execute()

        application.shutdown.assert_called_once_with()

    def test_execute_returns_run_exit_code(self) -> None:
        config = DummyConfig()
        application = Application(config)
        application.run = Mock(return_value=7)  # type: ignore[assignment]

        self.assertEqual(application.execute(), 7)

    def test_execute_propagates_run_exception(self) -> None:
        config = DummyConfig()
        application = Application(config)
        application.run = Mock(side_effect=ValueError("boom"))  # type: ignore[assignment]

        with self.assertRaises(ValueError):
            application.execute()


if __name__ == "__main__":
    unittest.main()
