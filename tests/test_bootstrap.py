"""Tests for the application composition root."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app.bootstrap as bootstrap_module
from app.controllers.app_controller import AppController
from app.controllers.company_controller import CompanyController
from app.controllers.customer_controller import CustomerController
from app.core.app import Application
from app.core.app_state import AppState
from app.core.event_bus import EventBus
from app.core.service_container import ServiceContainer
from app.infrastructure.qt_event_loop import QtEventLoop
from app.services.navigation_service import NavigationService
from app.services.customer_service import CustomerService
from app.repositories.customer_repository import CustomerRepository
from app.views.main_view import MainView
from app.views.company_view import CompanyView
from app.views.customer_dialog import CustomerDialog
from app.views.customer_list_view import CustomerListView


class FakeQApplication:
    """Track QApplication creation without starting Qt."""

    current: FakeQApplication | None = None
    creation_count = 0

    def __init__(self, arguments: list[str]) -> None:
        type(self).current = self
        type(self).creation_count += 1
        self.arguments = arguments
        self.stylesheet = ""

    def setStyleSheet(self, stylesheet: str) -> None:
        self.stylesheet = stylesheet

    @classmethod
    def instance(cls) -> FakeQApplication | None:
        return cls.current


class CapturingContainer(ServiceContainer):
    """Expose the container created by bootstrap to the test."""

    latest: CapturingContainer | None = None
    creation_count = 0

    def __init__(self) -> None:
        super().__init__()
        type(self).latest = self
        type(self).creation_count += 1


def test_bootstrap_composes_and_registers_single_object_graph(
    monkeypatch: MonkeyPatch,
) -> None:
    FakeQApplication.current = None
    FakeQApplication.creation_count = 0
    CapturingContainer.latest = None
    CapturingContainer.creation_count = 0

    monkeypatch.setattr(bootstrap_module, "QApplication", FakeQApplication)
    monkeypatch.setattr(bootstrap_module, "ServiceContainer", CapturingContainer)
    monkeypatch.setattr(bootstrap_module.MainView, "show", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_company", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_home", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_customers", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "set_customer_view", Mock())
    monkeypatch.setattr(bootstrap_module.CompanyView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CompanyView, "bind_controller", Mock())
    monkeypatch.setattr(bootstrap_module.CustomerListView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CustomerListView, "bind_controller", Mock())
    monkeypatch.setattr(bootstrap_module.CustomerDialog, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CustomerDialog, "bind_controller", Mock())

    application = bootstrap_module.bootstrap()

    container = CapturingContainer.latest
    assert isinstance(application, Application)
    assert container is not None
    assert FakeQApplication.creation_count == 1
    assert CapturingContainer.creation_count == 1
    assert container.service_count == 17
    assert container.resolve(AppState) is application.app_state
    assert container.resolve(EventBus) is not None
    assert container.resolve(NavigationService) is application.navigation_service
    assert container.resolve(MainView) is application.app_controller.view
    assert container.resolve(AppController) is application.app_controller
    assert container.resolve(QtEventLoop) is application.event_loop
    assert isinstance(container.resolve(CompanyView), CompanyView)
    assert isinstance(container.resolve(CompanyController), CompanyController)
    assert isinstance(container.resolve(CustomerRepository), CustomerRepository)
    assert isinstance(container.resolve(CustomerService), CustomerService)
    assert isinstance(container.resolve(CustomerListView), CustomerListView)
    assert isinstance(container.resolve(CustomerDialog), CustomerDialog)
    assert isinstance(container.resolve(CustomerController), CustomerController)
    assert not container.is_registered(ServiceContainer)
    assert application.navigation_service.current_controller is None
    assert application.app_controller.is_running is False
    bootstrap_module.MainView.show.assert_not_called()


def test_bootstrap_reuses_existing_qapplication(monkeypatch: MonkeyPatch) -> None:
    existing = FakeQApplication([])
    FakeQApplication.creation_count = 0
    monkeypatch.setattr(bootstrap_module, "QApplication", FakeQApplication)
    monkeypatch.setattr(bootstrap_module.MainView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_company", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_home", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "on_open_customers", Mock())
    monkeypatch.setattr(bootstrap_module.MainView, "set_customer_view", Mock())
    monkeypatch.setattr(bootstrap_module.CompanyView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CompanyView, "bind_controller", Mock())
    monkeypatch.setattr(bootstrap_module.CustomerListView, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CustomerListView, "bind_controller", Mock())
    monkeypatch.setattr(bootstrap_module.CustomerDialog, "__init__", lambda self: None)
    monkeypatch.setattr(bootstrap_module.CustomerDialog, "bind_controller", Mock())

    application = bootstrap_module.bootstrap()

    assert FakeQApplication.creation_count == 0
    assert application.event_loop._application is existing
