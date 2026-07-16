"""Tests for the application entry point."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app.main as app_main


def test_main_bootstraps_application_and_executes_it() -> None:
    with patch("app.main.bootstrap") as bootstrap:
        application = bootstrap.return_value
        application.execute.return_value = 7

        assert app_main.main() == 7
        bootstrap.assert_called_once_with()
        application.execute.assert_called_once_with()


def test_importing_app_main_does_not_run_program() -> None:
    assert hasattr(app_main, "main")


def test_main_propagates_bootstrap_exception() -> None:
    with patch("app.main.bootstrap", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            app_main.main()


def test_main_propagates_execute_exception() -> None:
    with patch("app.main.bootstrap") as bootstrap:
        bootstrap.return_value.execute.side_effect = ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            app_main.main()
