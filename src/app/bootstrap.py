"""Application composition root."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.controllers.app_controller import AppController
from app.core.app import Application
from app.core.app_state import AppState
from app.core.event_bus import EventBus
from app.core.service_container import ServiceContainer
from app.infrastructure.qt_event_loop import QtEventLoop
from app.services.navigation_service import NavigationService
from app.views.main_view import MainView

__all__ = ["bootstrap"]


def bootstrap() -> Application:
    """Create, connect, and register the application's object graph."""
    qt_application = QApplication.instance()
    if qt_application is None:
        qt_application = QApplication(sys.argv)

    event_loop = QtEventLoop(qt_application)
    container = ServiceContainer()
    app_state = AppState()
    event_bus = EventBus()
    navigation_service = NavigationService()
    main_view = MainView()
    app_controller = AppController(main_view)

    container.register(AppState, app_state)
    container.register(EventBus, event_bus)
    container.register(NavigationService, navigation_service)
    container.register(MainView, main_view)
    container.register(AppController, app_controller)
    container.register(QtEventLoop, event_loop)

    application = Application(
        app_state,
        navigation_service,
        app_controller,
        event_loop,
    )
    return application
