"""UI and navigation behavior for the customer module."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from app.models.customer import Customer
from app.views.customer_dialog import CustomerDialog
from app.views.customer_list_view import CustomerListView
from app.views.main_view import MainView


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    yield QApplication.instance() or QApplication([])


def customer(customer_id: int = 1, name: str = "Acme") -> Customer:
    return Customer(
        id=customer_id,
        client_type="company",
        name=name,
        company_code="123",
        vat_code="",
        phone="",
        email="",
        city="Vilnius",
        status="active",
    )


def test_customer_list_empty_state_variants(application: QApplication) -> None:
    view = CustomerListView()
    view.display_customers([], 0)
    assert view.content.currentWidget() is view.empty_page
    assert view.empty_label.text() == "Kol kas nėra nė vieno kliento."
    assert not view.first_customer_button.isHidden()
    assert not view.search_input.isEnabled()
    view.display_customers([], 3)
    assert view.empty_label.text() == "Pagal pasirinktus filtrus klientų nerasta."
    assert view.first_customer_button.isHidden()
    assert view.search_input.isEnabled()


def test_customer_list_loading_and_table_state(application: QApplication) -> None:
    view = CustomerListView()
    view.set_loading(True)
    assert view.content.currentWidget() is view.loading_page
    assert not view.new_button.isEnabled()
    view.display_customers([customer()], 1)
    assert view.content.currentWidget() is view.table
    assert view.table.rowCount() == 1
    assert view.table.item(0, 2).text() == "—"
    assert view.count_label.text() == "1 klientų"


def test_customer_table_keyboard_actions(application: QApplication) -> None:
    view = CustomerListView()
    calls: list[str] = []
    view.table.on_activate = lambda: calls.append("edit")
    view.table.on_delete = lambda: calls.append("delete")
    view.table.keyPressEvent(
        QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    )
    view.table.keyPressEvent(
        QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
    )
    assert calls == ["edit", "delete"]


def test_customer_dialog_tabs_and_dirty_state(application: QApplication) -> None:
    dialog = CustomerDialog()
    values = {
        "client_type": "company",
        "name": "Acme",
        "company_code": "123",
        "vat_code": "",
        "address": "",
        "city": "",
        "postal_code": "",
        "country_code": "Lietuva",
        "phone": "",
        "email": "",
        "notes": "",
        "status": "active",
    }
    dialog.display_customer(customer(), values)
    assert dialog.tabs.count() == 5
    assert not dialog.tabs.isTabEnabled(4)
    assert not dialog.save_button.isEnabled()
    dialog._inputs["city"].setText("Kaunas")
    assert dialog.dirty_label.text() == "● Neišsaugoti pakeitimai"
    assert dialog.save_button.isEnabled()
    dialog.restore_snapshot()
    assert dialog._inputs["city"].text() == ""
    assert not dialog.save_button.isEnabled()


def test_customer_dialog_close_uses_dirty_guard(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    dialog = CustomerDialog()
    values = {
        "client_type": "individual",
        "name": "Jonas",
        "company_code": "",
        "vat_code": "",
        "address": "",
        "city": "",
        "postal_code": "",
        "country_code": "Lietuva",
        "phone": "",
        "email": "",
        "notes": "",
        "status": "active",
    }
    dialog.display_customer(None, values)
    dialog.show()
    dialog._inputs["phone"].setText("+370")
    monkeypatch.setattr(dialog, "_confirm_discard", lambda: False)
    dialog.close()
    assert dialog.is_visible()
    monkeypatch.setattr(dialog, "_confirm_discard", lambda: True)
    dialog.close()
    assert not dialog.is_visible()


def test_customer_workspace_navigation(application: QApplication) -> None:
    main = MainView()
    customers = CustomerListView()
    main.set_customer_view(customers)
    main.show_customers()
    assert main.workspace.currentWidget() is customers.widget
    assert main.customer_button.isChecked()
    main.show_home()
    assert main.workspace.currentWidget() is main.home_view
    assert main.home_button.isChecked()
    main.close()
