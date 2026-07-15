import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers import AppController, BaseController  # noqa: E402
from app.views import BaseView  # noqa: E402


class DummyView(BaseView):
    def __init__(self) -> None:
        self.show_calls = 0
        self.close_calls = 0
        self.is_visible = False
        self.raise_on_show = False
        self.raise_on_close = False

    def show(self) -> None:
        self.show_calls += 1
        if self.raise_on_show:
            raise RuntimeError("show failed")
        self.is_visible = True

    def close(self) -> None:
        self.close_calls += 1
        if self.raise_on_close:
            raise RuntimeError("close failed")
        self.is_visible = False


def test_app_controller_can_be_created_with_concrete_view() -> None:
    view = DummyView()
    controller = AppController(view)

    assert isinstance(controller, AppController)


def test_new_controller_is_not_running() -> None:
    controller = AppController(DummyView())

    assert controller.is_running is False


def test_controller_view_property_returns_the_provided_view() -> None:
    view = DummyView()
    controller = AppController(view)

    assert controller.view is view


def test_start_calls_show() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()

    assert view.show_calls == 1


def test_start_sets_running_state_to_true() -> None:
    controller = AppController(DummyView())

    controller.start()

    assert controller.is_running is True


def test_repeated_start_does_not_call_show_again() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()
    controller.start()

    assert view.show_calls == 1


def test_stop_after_start_calls_close() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()
    controller.stop()

    assert view.close_calls == 1


def test_stop_sets_running_state_to_false() -> None:
    controller = AppController(DummyView())

    controller.start()
    controller.stop()

    assert controller.is_running is False


def test_repeated_stop_does_not_call_close_again() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()
    controller.stop()
    controller.stop()

    assert view.close_calls == 1


def test_stop_before_start_does_not_call_close() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.stop()

    assert view.close_calls == 0


def test_controller_can_be_started_again_after_stopping() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()
    controller.stop()
    controller.start()

    assert view.show_calls == 2


def test_repeated_start_after_stop_calls_show_again() -> None:
    view = DummyView()
    controller = AppController(view)

    controller.start()
    controller.stop()
    controller.start()

    assert view.show_calls == 2


def test_show_exception_is_propagated() -> None:
    view = DummyView()
    view.raise_on_show = True
    controller = AppController(view)

    with pytest.raises(RuntimeError, match="show failed"):
        controller.start()

    assert controller.is_running is False


def test_close_exception_is_propagated() -> None:
    view = DummyView()
    view.raise_on_close = True
    controller = AppController(view)
    controller.start()

    with pytest.raises(RuntimeError, match="close failed"):
        controller.stop()

    assert controller.is_running is True


def test_is_running_property_is_read_only() -> None:
    controller = AppController(DummyView())

    with pytest.raises(AttributeError):
        controller.is_running = True


def test_app_controller_is_a_base_controller_instance() -> None:
    controller = AppController(DummyView())

    assert isinstance(controller, BaseController)


def test_app_controller_can_be_imported_from_app_controllers_package() -> None:
    from app.controllers import AppController as ImportedAppController

    assert ImportedAppController is AppController
