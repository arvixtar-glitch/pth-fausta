"""Qt UI and navigation behavior for the product module."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.controllers.app_controller import AppController
from app.controllers.product_controller import ProductController
from app.models.product import Product, ProductBarcode, ProductCategory, UnitOfMeasure
from app.persistence.orm import OrmBase
from app.persistence.session_factory import SessionFactory
from app.repositories.company_repository import CompanyRepository
from app.repositories.product_repository import ProductRepository
from app.services.company_service import CompanyService
from app.services.navigation_service import NavigationService
from app.services.product_service import ProductService
from app.views.customer_list_view import CustomerListView
from app.views.main_view import MainView
from app.views.product_dialog import ProductDialog
from app.views.product_list_view import ProductListView


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    yield QApplication.instance() or QApplication([])


def product() -> Product:
    item = Product(
        id=1,
        name="Popierius",
        code="P-1",
        product_type="product",
        category_id=1,
        unit_id=1,
        unit_price=Decimal("3.20"),
        price_basis="net",
        vat_treatment="rate",
        vat_rate=Decimal("21"),
        status="active",
        notes="",
    )
    item.category = ProductCategory(id=1, name="Biuras", normalized_name="biuras")
    item.unit = UnitOfMeasure(id=1, code="vnt.", name="vnt.")
    item.barcodes = [
        ProductBarcode(id=1, barcode="123", barcode_type="other", is_default=True)
    ]
    return item


def base_values() -> dict[str, object]:
    return {
        "product_type": "product",
        "name": "Popierius",
        "code": "P-1",
        "category_id": 1,
        "unit_id": 1,
        "unit_price": "3.20",
        "vat_treatment": "rate",
        "vat_rate": "21",
        "status": "active",
        "notes": "",
        "barcodes": [{"barcode": "123", "barcode_type": "other", "is_default": True}],
    }


class FakeController:
    def gross_price(self, price, treatment, rate):
        return (
            price
            if treatment != "rate"
            else (price * (Decimal("1") + rate / 100)).quantize(Decimal("0.01"))
        )


def test_product_list_columns_vat_visibility_and_states(
    application: QApplication,
) -> None:
    view = ProductListView()
    assert view.table.columnCount() == 8
    assert [view.table.horizontalHeaderItem(i).text() for i in range(8)] == list(
        view.HEADERS
    )
    view.set_vat_payer(False)
    assert view.table.isColumnHidden(6)
    view.set_vat_payer(True)
    assert not view.table.isColumnHidden(6)
    view.display_products([], 0)
    assert view.empty_label.text() == "Kol kas nėra nei vienos prekės ar paslaugos."
    assert not view.first_product_button.isHidden()
    view.display_products([], 2)
    assert view.empty_label.text() == "Pagal pasirinktus filtrus nieko nerasta."
    assert view.first_product_button.isHidden()
    view.set_loading(True)
    assert view.content.currentWidget() is view.loading_page
    assert not view.new_product_button.isEnabled()
    view.display_products([product()], 1)
    assert view.table.item(0, 2).text() == "123"
    assert view.table.item(0, 6).text() == "21%"


def test_product_table_keyboard_actions(application: QApplication) -> None:
    view = ProductListView()
    calls: list[str] = []
    view.table.on_activate = lambda: calls.append("edit")
    view.table.on_delete = lambda: calls.append("delete")
    view.table.keyPressEvent(
        QKeyEvent(
            QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier
        )
    )
    view.table.keyPressEvent(
        QKeyEvent(
            QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier
        )
    )
    assert calls == ["edit", "delete"]


def test_product_dialog_tabs_pricing_and_aggregate_dirty_state(
    application: QApplication,
) -> None:
    dialog = ProductDialog()
    dialog.bind_controller(FakeController())  # type: ignore[arg-type]
    categories = [ProductCategory(id=1, name="Biuras", normalized_name="biuras")]
    units = [UnitOfMeasure(id=1, code="vnt.", name="vnt.")]
    dialog.display_product(product(), base_values(), categories, units, True)
    assert (
        dialog.tabs.count() == 6
        and not dialog.tabs.isTabEnabled(4)
        and not dialog.tabs.isTabEnabled(5)
    )
    assert not dialog.vat_field.isHidden() and dialog.gross_input.text() == "3.87"
    dialog._apply_barcode(
        None, {"barcode": "456", "barcode_type": "ean8", "is_default": True}
    )
    assert (
        dialog.dirty_label.text() == "● Neišsaugoti pakeitimai"
        and dialog.barcode_table.rowCount() == 2
    )
    dialog.restore_snapshot()
    assert dialog.barcode_table.rowCount() == 1 and not dialog.save_button.isEnabled()
    dialog.display_product(None, base_values(), categories, units, False)
    assert dialog.vat_field.isHidden() and dialog.gross_field.isHidden()


def test_full_workspace_navigation_keeps_main_controller_alive(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    main = MainView()
    customers = CustomerListView()
    products = ProductListView()
    main.set_customer_view(customers)
    main.set_product_view(products)
    customer_refresh, product_refresh = Mock(), Mock()
    main.on_open_customers(lambda: (main.show_customers(), customer_refresh()))
    main.on_open_products(lambda: (main.show_products(), product_refresh()))
    app_controller = AppController(main)
    navigation = NavigationService()
    original_close = main.close
    monkeypatch.setattr(main, "close", Mock(wraps=original_close))
    monkeypatch.setattr(app_controller, "stop", Mock(wraps=app_controller.stop))
    monkeypatch.setattr(
        navigation, "close_current", Mock(wraps=navigation.close_current)
    )
    navigation.navigate_to(app_controller)
    application.processEvents()
    main.home_button.click()
    main.customer_button.click()
    main.product_button.click()
    main.home_button.click()
    main.product_button.click()
    application.processEvents()
    assert main.workspace.currentWidget() is products.widget
    assert main.is_visible()
    assert app_controller.is_running
    assert product_refresh.call_count == 2
    assert customer_refresh.call_count == 1
    assert QApplication.instance() is application
    assert not application.closingDown()
    main.close.assert_not_called()
    app_controller.stop.assert_not_called()
    navigation.close_current.assert_not_called()
    original_close()
    application.processEvents()


def test_live_product_workspace_smoke_flow(application: QApplication) -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    OrmBase.metadata.create_all(engine)
    sessions = SessionFactory(engine)
    company = CompanyService(CompanyRepository(sessions))
    company.save_company({"name": "Testinė įmonė", "vat_code": "LT123"})
    service = ProductService(ProductRepository(sessions), company)
    service.ensure_default_units()
    view, dialog = ProductListView(), ProductDialog()
    controller = ProductController(service, view, dialog)
    customers = CustomerListView()
    main = MainView()
    main.set_customer_view(customers)
    main.set_product_view(view)
    main.on_open_products(lambda: (main.show_products(), controller.refresh()))
    main.show()
    main.product_button.click()
    application.processEvents()

    view.new_product_button.click()
    dialog.name_input.setText("Popierius")
    dialog.code_input.setText("P-1")
    dialog.price_input.setText("3,20")
    dialog._apply_barcode(
        None,
        {"barcode": "477000000001", "barcode_type": "ean13", "is_default": True},
    )
    dialog.save_button.click()
    assert service.count_products() == 1
    assert dialog.gross_input.text() == "3.87"
    dialog.close()

    view.new_service_button.click()
    dialog.name_input.setText("Konsultacija")
    dialog.code_input.setText("S-1")
    dialog.price_input.setText("50")
    dialog.save_button.click()
    assert service.count_products() == 2
    dialog.close()

    company.save_company({"name": "Testinė įmonė", "vat_code": ""})
    controller.refresh()
    assert view.table.isColumnHidden(6)
    view.search_input.setText("Konsultacija")
    view.type_filter.setCurrentIndex(view.type_filter.findData("service"))
    application.processEvents()
    assert view.table.rowCount() == 1

    main.home_button.click()
    main.customer_button.click()
    main.product_button.click()
    main.home_button.click()
    main.product_button.click()
    assert main.workspace.currentWidget() is view.widget
    main.close()
    application.processEvents()
    assert not main.is_visible()
