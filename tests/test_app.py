"""Tests for application lifecycle orchestration."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core.app import Application  # noqa: E402


class DummyLogger:
    """Collect logged informational messages."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)


class DummyConfig:
    """Provide a logger to Application."""

    def __init__(self) -> None:
        self.logger = DummyLogger()


@pytest.fixture
def dependencies() -> tuple[Mock, Mock, Mock, Mock, DummyConfig]:
    app_state = Mock()
    navigation = Mock()
    controller = Mock()
    event_loop = Mock()
    event_loop.run.return_value = 7
    return app_state, navigation, controller, event_loop, DummyConfig()


def make_application(dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig]) -> Application:
    app_state, navigation, controller, event_loop, config = dependencies
    return Application(app_state, navigation, controller, event_loop, config)  # type: ignore[arg-type]


def test_uses_provided_dependencies(
    dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig],
) -> None:
    application = make_application(dependencies)
    app_state, navigation, controller, event_loop, config = dependencies

    assert application.app_state is app_state
    assert application.navigation_service is navigation
    assert application.app_controller is controller
    assert application.event_loop is event_loop
    assert application.config is config
    assert application.logger is config.logger


def test_run_starts_state_navigates_and_runs_event_loop(
    dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig],
) -> None:
    application = make_application(dependencies)
    app_state, navigation, controller, event_loop, config = dependencies

    result = application.run()

    assert result == 7
    assert config.logger.messages == ["Starting PTH Fausta 0.1.0."]
    app_state.start.assert_called_once_with()
    navigation.navigate_to.assert_called_once_with(controller)
    event_loop.run.assert_called_once_with()


def test_shutdown_closes_controller_state_and_event_loop(
    dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig],
) -> None:
    application = make_application(dependencies)
    app_state, navigation, _, event_loop, config = dependencies

    application.shutdown()

    navigation.close_current.assert_called_once_with()
    app_state.stop.assert_called_once_with()
    event_loop.quit.assert_called_once_with()
    assert config.logger.messages == ["Application shutdown completed."]


def test_execute_returns_event_loop_exit_code(
    dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig],
) -> None:
    assert make_application(dependencies).execute() == 7


def test_execute_always_invokes_shutdown(
    dependencies: tuple[Mock, Mock, Mock, Mock, DummyConfig],
) -> None:
    application = make_application(dependencies)
    application.run = Mock(side_effect=RuntimeError("boom"))  # type: ignore[method-assign]
    application.shutdown = Mock()  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="boom"):
        application.execute()

    application.shutdown.assert_called_once_with()


def test_core_application_has_no_qt_or_mvc_imports() -> None:
    source = (ROOT / "src" / "app" / "core" / "app.py").read_text(encoding="utf-8")

    assert "PySide6" not in source
    assert "app.controllers" not in source
    assert "app.views" not in source
