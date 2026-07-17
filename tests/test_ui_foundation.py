"""Tests for the finalized UI foundation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtWidgets import QApplication

from app.models.company import Company, CompanyBankAccount
from app.ui.styles import application_stylesheet
from app.ui.theme import COLOR_PRIMARY, SPACING_MD
from app.views.company_view import CompanyView
from app.views.home_view import HomeView
from app.views.main_view import MainView


@pytest.fixture(scope="module")
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_theme_has_central_tokens_and_application_qss() -> None:
    assert COLOR_PRIMARY in application_stylesheet()
    assert SPACING_MD == 16


def test_home_view_opens_company(application: QApplication) -> None:
    view = HomeView()
    calls: list[bool] = []
    view.on_open_company(lambda: calls.append(True))
    view.company_button.click()
    assert calls == [True]


def test_main_view_sidebar_navigation_and_status(application: QApplication) -> None:
    view = MainView()
    view.set_active_navigation("company")
    assert view.sidebar is not None
    assert view.company_button.isChecked()
    assert "Duomenų bazė: prijungta" in view.status_label.text()
    width = view.sidebar.width()
    view.toggle_sidebar()
    assert view.sidebar.width() != width


def test_company_view_dirty_cancel_and_empty_state(application: QApplication) -> None:
    view = CompanyView()
    company = Company(name="Fausta", city="Vilnius")
    view.display_company(company)
    view.display_bank_accounts([])
    assert not view.empty_label.isHidden()
    assert not view.save_button.isEnabled()
    view._inputs["city"].setText("Kaunas")
    assert view.save_button.isEnabled()
    view.restore_snapshot()
    assert view._inputs["city"].text() == "Vilnius"


def test_company_view_account_actions_follow_selection(
    application: QApplication,
) -> None:
    view = CompanyView()
    account = CompanyBankAccount(
        id=1,
        company_id=1,
        bank_name="Bankas",
        iban="LT001",
        is_default=True,
    )
    view.display_bank_accounts([account])
    assert not view.edit_button.isEnabled()
    view._table.selectRow(0)
    assert view.edit_button.isEnabled()
    assert view.delete_button.isEnabled()
    assert view.default_button.isEnabled()


def test_accessible_sidebar_controls(application: QApplication) -> None:
    view = MainView()
    assert view.collapse_button.accessibleName()
    assert view.company_button.toolTip() == "Įmonė"
