"""Application composition root."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.controllers.app_controller import AppController
from app.controllers.company_controller import CompanyController
from app.controllers.customer_controller import CustomerController
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
from app.repositories.customer_repository import CustomerRepository
from app.services.company_service import CompanyService
from app.services.customer_service import CustomerService
from app.services.navigation_service import NavigationService
from app.ui.styles import application_stylesheet
from app.views.company_view import CompanyView
from app.views.customer_dialog import CustomerDialog
from app.views.customer_list_view import CustomerListView
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
    customer_repository = CustomerRepository(session_factory)
    customer_service = CustomerService(customer_repository)
    customer_view = CustomerListView()
    customer_dialog = CustomerDialog()
    customer_controller = CustomerController(
        customer_service, customer_view, customer_dialog
    )
    main_view = MainView()
    main_view.set_customer_view(customer_view)
    main_view.set_company_exists(company_service.get_company() is not None)
    company_controller.on_company_changed(main_view.set_company_exists)
    main_view.on_open_home(navigation_service.close_current)

    def open_customers() -> None:
        main_view.show_customers()
        navigation_service.navigate_to(customer_controller)

    def open_company() -> None:
        navigation_service.close_current()
        company_controller.start()

    main_view.on_open_customers(open_customers)
    main_view.on_open_company(open_company)
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
    container.register(CustomerRepository, customer_repository)
    container.register(CustomerService, customer_service)
    container.register(CustomerListView, customer_view)
    container.register(CustomerDialog, customer_dialog)
    container.register(CustomerController, customer_controller)

    application = Application(
        app_state,
        navigation_service,
        app_controller,
        event_loop,
    )
    return application
