"""Tests for reusable shared UI components."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

from app.ui.shared import (
    ActionTable,
    BaseListView,
    CardDialogShell,
    CrudToolbar,
    EmptyStateWidget,
    FilterBar,
    LoadingStateWidget,
    StatusBarWidget,
)
from app.views.customer_list_view import CustomerListView
from app.views.dirty_state import GuardedDialog
from app.views.product_list_view import ProductListView


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    yield QApplication.instance() or QApplication([])


def test_crud_toolbar_supports_named_and_additional_actions(
    application: QApplication,
) -> None:
    toolbar = CrudToolbar(
        (
            ("new", "Naujas", "primary"),
            ("extra", "Papildomas", None),
            ("delete", "Šalinti", "danger"),
        )
    )
    assert list(toolbar.buttons) == ["new", "extra", "delete"]
    assert toolbar.buttons["new"].text() == "Naujas"
    assert toolbar.buttons["delete"].objectName() == "danger"


def test_filter_bar_combines_search_and_controlled_filters(
    application: QApplication,
) -> None:
    filters = FilterBar(
        "Ieškoti...", (("status", (("Visi", None), ("Aktyvūs", "active"))),)
    )
    assert filters.search_input.placeholderText() == "Ieškoti..."
    assert filters.filters["status"].itemData(1) == "active"
    filters.set_controls_enabled(False)
    assert not filters.search_input.isEnabled()
    assert not filters.filters["status"].isEnabled()


def test_empty_loading_and_status_widgets_keep_standard_states(
    application: QApplication,
) -> None:
    empty = EmptyStateWidget("Sukurti")
    empty.display("Tuščia", "Paaiškinimas", True)
    assert empty.message_label.text() == "Tuščia"
    assert not empty.action_button.isHidden()
    empty.display("Nerasta", "Keiskite filtrą", False)
    assert empty.action_button.isHidden()
    loading = LoadingStateWidget("Kraunama...")
    assert loading.indicator.minimum() == 0 == loading.indicator.maximum()
    status = StatusBarWidget("0 įrašų")
    assert status.count_label.text() == "0 įrašų"


def test_base_list_view_owns_table_loading_empty_and_filter_states(
    application: QApplication,
) -> None:
    view = BaseListView(
        title="Testas",
        description="Aprašymas",
        table=ActionTable(1, ("Pavadinimas",)),
        actions=(("new", "Naujas", "primary"),),
        search_placeholder="Ieškoti...",
        filters=(("status", (("Visi", None),)),),
        loading_text="Kraunama...",
        first_action_text="Sukurti",
        initial_count_text="0 įrašų",
    )
    view.set_loading(True)
    assert view.content.currentWidget() is view.loading_page
    assert not view.toolbar.buttons["new"].isEnabled()
    view.display_state(
        visible_count=0,
        total_count=0,
        empty_message="Tuščia",
        empty_description="Sukurkite",
        no_results_message="Nerasta",
        no_results_description="Keiskite filtrus",
    )
    assert view.content.currentWidget() is view.empty_page
    assert view.empty_label.text() == "Tuščia"
    view.display_state(
        visible_count=0,
        total_count=2,
        empty_message="Tuščia",
        empty_description="Sukurkite",
        no_results_message="Nerasta",
        no_results_description="Keiskite filtrus",
    )
    assert view.empty_label.text() == "Nerasta"
    assert view.search_input.isEnabled()


def test_customer_and_product_lists_inherit_shared_base(
    application: QApplication,
) -> None:
    assert isinstance(CustomerListView(), BaseListView)
    assert isinstance(ProductListView(), BaseListView)


def test_card_dialog_shell_builds_standard_actions_and_reserved_tabs(
    application: QApplication,
) -> None:
    dialog = GuardedDialog()
    calls: list[str] = []
    shell = CardDialogShell(
        dialog,
        close=lambda: calls.append("close"),
        restore=lambda: calls.append("restore"),
        save=lambda: calls.append("save"),
    )
    shell.add_reserved_tab("Istorija (greitai)")
    shell.close_button.click()
    shell.cancel_button.click()
    shell.save_button.click()
    assert calls == ["close", "restore", "save"]
    assert not shell.tabs.isTabEnabled(0)
    assert shell.success_timer.interval() == 3_000
