import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers import BaseController  # noqa: E402
from app.services import NavigationService  # noqa: E402
from app.views import BaseView  # noqa: E402


class DummyView(BaseView):
    def __init__(self) -> None:
        self.show_calls = 0
        self.close_calls = 0
        self.visible = False
        self.raise_on_show = False
        self.raise_on_close = False

    def show(self) -> None:
        self.show_calls += 1
        if self.raise_on_show:
            raise RuntimeError("show failed")
        self.visible = True

    def close(self) -> None:
        self.close_calls += 1
        if self.raise_on_close:
            raise RuntimeError("close failed")
        self.visible = False


class DummyController(BaseController):
    def __init__(self, view: DummyView, operations: list[str]) -> None:
        super().__init__(view)
        self.operations = operations
        self.raise_on_start = False
        self.raise_on_stop = False
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        self.operations.append("start")
        if self.raise_on_start:
            raise RuntimeError("start failed")
        self.view.show()

    def stop(self) -> None:
        self.stop_calls += 1
        self.operations.append("stop")
        if self.raise_on_stop:
            raise RuntimeError("stop failed")
        self.view.close()


def test_new_service_has_no_active_controller() -> None:
    service = NavigationService()

    assert service.current_controller is None
    assert service.has_active_controller is False


def test_navigate_to_starts_the_controller() -> None:
    service = NavigationService()
    view = DummyView()
    controller = DummyController(view, [])

    service.navigate_to(controller)

    assert service.current_controller is controller
    assert controller.start_calls == 1
    assert view.visible is True


def test_navigate_to_switches_to_new_controller_and_stops_previous() -> None:
    service = NavigationService()
    operations: list[str] = []
    old_view = DummyView()
    new_view = DummyView()
    old_controller = DummyController(old_view, operations)
    new_controller = DummyController(new_view, operations)

    service.navigate_to(old_controller)
    service.navigate_to(new_controller)

    assert operations == ["start", "stop", "start"]
    assert service.current_controller is new_controller
    assert old_view.visible is False
    assert new_view.visible is True


def test_navigating_to_same_controller_does_nothing_additional() -> None:
    service = NavigationService()
    operations: list[str] = []
    controller = DummyController(DummyView(), operations)

    service.navigate_to(controller)
    service.navigate_to(controller)

    assert operations == ["start"]


def test_close_current_stops_the_active_controller() -> None:
    service = NavigationService()
    view = DummyView()
    controller = DummyController(view, [])

    service.navigate_to(controller)
    service.close_current()

    assert controller.stop_calls == 1
    assert service.current_controller is None
    assert view.visible is False


def test_close_current_when_no_controller_is_noop() -> None:
    service = NavigationService()

    service.close_current()

    assert service.current_controller is None


def test_close_current_is_idempotent() -> None:
    service = NavigationService()
    controller = DummyController(DummyView(), [])

    service.navigate_to(controller)
    service.close_current()
    service.close_current()

    assert controller.stop_calls == 1


def test_navigate_to_rejects_non_controller_objects() -> None:
    service = NavigationService()

    with pytest.raises(TypeError):
        service.navigate_to(object())


def test_previous_stop_failure_prevents_new_start() -> None:
    service = NavigationService()
    operations: list[str] = []
    old_controller = DummyController(DummyView(), operations)
    new_controller = DummyController(DummyView(), operations)
    old_controller.raise_on_stop = True

    service.navigate_to(old_controller)

    with pytest.raises(RuntimeError, match="stop failed"):
        service.navigate_to(new_controller)

    assert service.current_controller is old_controller
    assert new_controller.start_calls == 0


def test_new_start_failure_clears_current_controller() -> None:
    service = NavigationService()
    operations: list[str] = []
    old_controller = DummyController(DummyView(), operations)
    new_controller = DummyController(DummyView(), operations)
    new_controller.raise_on_start = True

    service.navigate_to(old_controller)

    with pytest.raises(RuntimeError, match="start failed"):
        service.navigate_to(new_controller)

    assert service.current_controller is None


def test_close_current_propagates_stop_exception() -> None:
    service = NavigationService()
    controller = DummyController(DummyView(), [])
    controller.raise_on_stop = True

    service.navigate_to(controller)

    with pytest.raises(RuntimeError, match="stop failed"):
        service.close_current()

    assert service.current_controller is controller


def test_current_controller_property_is_read_only() -> None:
    service = NavigationService()

    with pytest.raises(AttributeError):
        service.current_controller = object()


def test_has_active_controller_property_is_read_only() -> None:
    service = NavigationService()

    with pytest.raises(AttributeError):
        service.has_active_controller = True


def test_navigation_service_can_be_imported_from_app_services_package() -> None:
    from app.services import NavigationService as ImportedNavigationService

    assert ImportedNavigationService is NavigationService
