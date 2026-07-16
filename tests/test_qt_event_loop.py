"""Tests for the Qt event loop adapter."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.infrastructure.qt_event_loop import QtEventLoop  # noqa: E402


def test_run_delegates_to_qapplication_exec() -> None:
    application = Mock()
    application.exec.return_value = 4

    assert QtEventLoop(application).run() == 4
    application.exec.assert_called_once_with()


def test_quit_delegates_to_qapplication_quit() -> None:
    application = Mock()

    QtEventLoop(application).quit()

    application.quit.assert_called_once_with()
