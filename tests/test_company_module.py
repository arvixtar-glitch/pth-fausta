"""Tests for the company profile vertical slice."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers.company_controller import CompanyController
from app.models.company import Company, CompanyBankAccount
from app.persistence.orm import OrmBase
from app.persistence.session_factory import SessionFactory
from app.repositories.company_repository import CompanyRepository
from app.services.company_service import CompanyService


@pytest.fixture
def repository() -> CompanyRepository:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    OrmBase.metadata.create_all(engine)
    return CompanyRepository(SessionFactory(engine))


def test_orm_company_bank_account_relationship(repository: CompanyRepository) -> None:
    company = repository.create_company(name="Fausta")
    account = repository.add_bank_account(
        company.id, bank_name="Bankas", iban="LT001", is_default=True
    )

    loaded = repository.get_company()

    assert isinstance(loaded, Company)
    assert isinstance(account, CompanyBankAccount)
    assert loaded.bank_accounts[0].company_id == loaded.id


def test_repository_company_and_bank_account_crud(
    repository: CompanyRepository,
) -> None:
    company = repository.create_company(name="Fausta")
    saved = repository.save_company(company.id, city="Vilnius")
    account = repository.add_bank_account(
        company.id, bank_name="A", iban="LT001", is_default=True
    )
    updated = repository.update_bank_account(account.id, bank_name="B")

    assert saved.city == "Vilnius"
    assert updated.bank_name == "B"
    assert len(repository.list_bank_accounts(company.id)) == 1

    repository.delete_bank_account(account.id)
    assert repository.list_bank_accounts(company.id) == []


def test_service_keeps_exactly_one_default_account(
    repository: CompanyRepository,
) -> None:
    service = CompanyService(repository)
    service.save_company({"name": "Fausta"})
    first = service.add_bank_account({"bank_name": "A", "iban": "LT001"})
    second = service.add_bank_account(
        {"bank_name": "B", "iban": "LT002", "is_default": True}
    )

    accounts = service.list_bank_accounts()

    assert first.id != second.id
    assert [item.id for item in accounts if item.is_default] == [second.id]


def test_deleting_default_promotes_remaining_account(
    repository: CompanyRepository,
) -> None:
    service = CompanyService(repository)
    service.save_company({"name": "Fausta"})
    first = service.add_bank_account({"bank_name": "A", "iban": "LT001"})
    second = service.add_bank_account({"bank_name": "B", "iban": "LT002"})

    service.delete_bank_account(first.id)

    assert service.list_bank_accounts()[0].id == second.id
    assert service.list_bank_accounts()[0].is_default is True


class FakeCompanyView:
    """Record controller output without Qt."""

    def __init__(self) -> None:
        self.controller: CompanyController | None = None
        self.company: Company | None = None
        self.accounts: list[CompanyBankAccount] = []
        self.visible = False

    def bind_controller(self, controller: CompanyController) -> None:
        self.controller = controller

    def display_company(self, company: Company | None) -> None:
        self.company = company

    def display_bank_accounts(self, accounts: list[CompanyBankAccount]) -> None:
        self.accounts = accounts

    def show(self) -> None:
        self.visible = True

    def close(self) -> None:
        self.visible = False


def test_controller_main_save_and_read_scenario(repository: CompanyRepository) -> None:
    service = CompanyService(repository)
    view = FakeCompanyView()
    controller = CompanyController(service, view)  # type: ignore[arg-type]

    controller.save_company({"name": "Fausta", "city": "Kaunas"})
    controller.add_bank_account({"bank_name": "Bankas", "iban": "LT001"})
    controller.start()

    assert view.visible is True
    assert view.company is not None
    assert view.company.city == "Kaunas"
    assert view.accounts[0].iban == "LT001"
