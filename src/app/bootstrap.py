"""Application composition root."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.controllers.app_controller import AppController
from app.controllers.company_controller import CompanyController
from app.core.app import Application
from app.core.app_state import AppState
from app.core.event_bus import EventBus
from app.core.paths import ProjectPaths
from app.core.service_container import ServiceContainer
from app.infrastructure.qt_event_loop import QtEventLoop
from app.persistence.database_config import DatabaseConfig
from app.persistence.engine import DatabaseEngine
from app.persistence.orm import OrmBase
from app.persistence.session_factory import SessionFactory
from app.repositories.company_repository import CompanyRepository
from app.services.company_service import CompanyService
from app.services.navigation_service import NavigationService
from app.ui.styles import application_stylesheet
from app.views.company_view import CompanyView
from app.views.main_view import MainView

__all__ = ["bootstrap"]


def bootstrap() -> Application:
    """Create, connect, and register the application's object graph."""
    qt_application = QApplication.instance()
    if qt_application is None:
        qt_application = QApplication(sys.argv)
    qt_application.setStyleSheet(application_stylesheet())

    event_loop = QtEventLoop(qt_application)
    container = ServiceContainer()
    app_state = AppState()
    event_bus = EventBus()
    navigation_service = NavigationService()
    database_config = DatabaseConfig.default(ProjectPaths().project_root)
    database_config.ensure_directories()
    database_engine = DatabaseEngine(database_config)
    OrmBase.metadata.create_all(database_engine.engine)
    session_factory = SessionFactory(database_engine.engine)
    company_repository = CompanyRepository(session_factory)
    company_service = CompanyService(company_repository)
    company_view = CompanyView()
    company_controller = CompanyController(company_service, company_view)
    main_view = MainView()
    main_view.on_open_company(company_controller.start)
    app_controller = AppController(main_view)

    container.register(AppState, app_state)
    container.register(EventBus, event_bus)
    container.register(NavigationService, navigation_service)
    container.register(MainView, main_view)
    container.register(AppController, app_controller)
    container.register(QtEventLoop, event_loop)
    container.register(DatabaseEngine, database_engine)
    container.register(SessionFactory, session_factory)
    container.register(CompanyRepository, company_repository)
    container.register(CompanyService, company_service)
    container.register(CompanyView, company_view)
    container.register(CompanyController, company_controller)

    application = Application(
        app_state,
        navigation_service,
        app_controller,
        event_loop,
    )
    return application
