"""Tests for the main application view."""

import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication  # noqa: E402

from app.views import BaseView, MainView  # noqa: E402


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def main_view(application: QApplication) -> Iterator[MainView]:
    view = MainView()
    yield view
    view.close()
    application.processEvents()


def test_main_view_can_be_instantiated(main_view: MainView) -> None:
    assert isinstance(main_view, MainView)


def test_main_view_is_a_base_view() -> None:
    assert issubclass(MainView, BaseView)


def test_initial_title(main_view: MainView) -> None:
    assert main_view.window_title() == "PTH Fausta"


def test_set_title_changes_title(main_view: MainView) -> None:
    main_view.set_title("New title")

    assert main_view.window_title() == "New title"


def test_show_makes_window_visible(
    main_view: MainView, application: QApplication
) -> None:
    main_view.show()
    application.processEvents()

    assert main_view.is_visible()


def test_close_closes_window(
    main_view: MainView, application: QApplication
) -> None:
    main_view.show()
    application.processEvents()
    main_view.close()
    application.processEvents()

    assert not main_view.is_visible()
