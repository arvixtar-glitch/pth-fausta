import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers import BaseController
from app.views import BaseView


class DummyView(BaseView):
    def __init__(self) -> None:
        self.closed = False

    def show(self) -> None:
        self.shown = True

    def close(self) -> None:
        self.closed = True


class DummyController(BaseController):
    def start(self) -> None:
        self._started = True


def test_base_controller_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        BaseController(DummyView())


def test_controller_stores_the_provided_view() -> None:
    view = DummyView()
    controller = DummyController(view)

    assert controller.view is view


def test_controller_view_property_returns_the_same_object() -> None:
    view = DummyView()
    controller = DummyController(view)

    assert controller.view is view


def test_stop_closes_the_view() -> None:
    view = DummyView()
    controller = DummyController(view)

    controller.stop()

    assert view.closed is True


def test_concrete_controller_can_start() -> None:
    view = DummyView()
    controller = DummyController(view)

    controller.start()

    assert getattr(controller, "_started") is True
