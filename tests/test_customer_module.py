"""Persistence, repository, service and controller tests for customers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.controllers.customer_controller import CustomerController
from app.models.customer import Customer
from app.persistence.orm import OrmBase
from app.persistence.session_factory import SessionFactory
from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService


@pytest.fixture
def repository() -> CustomerRepository:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    OrmBase.metadata.create_all(engine)
    return CustomerRepository(SessionFactory(engine))


def company_values(name: str = "Acme", code: str = "123") -> dict[str, str]:
    return {
        "client_type": "company",
        "name": name,
        "company_code": code,
        "status": "active",
    }


def test_customer_orm_matches_documented_table(repository: CustomerRepository) -> None:
    columns = set(Customer.__table__.columns.keys())
    assert columns == {
        "id",
        "client_type",
        "name",
        "company_code",
        "vat_code",
        "address",
        "city",
        "postal_code",
        "country_code",
        "phone",
        "email",
        "notes",
        "status",
        "search_text",
        "created_at",
        "updated_at",
    }


def test_customer_repository_crud(repository: CustomerRepository) -> None:
    customer = repository.create(**company_values())
    assert repository.get(customer.id).name == "Acme"
    assert [item.id for item in repository.list_all()] == [customer.id]
    updated = repository.update(customer.id, city="Vilnius")
    assert updated.city == "Vilnius"
    repository.delete(customer.id)
    assert repository.list_all() == []


def test_service_validates_required_fields_and_type(
    repository: CustomerRepository,
) -> None:
    service = CustomerService(repository)
    with pytest.raises(ValueError, match="Pavadinimas"):
        service.create_customer(company_values(name=""))
    with pytest.raises(ValueError, match="kodas"):
        service.create_customer(company_values(code=""))
    individual = service.create_customer(
        {"client_type": "individual", "name": "Jonas", "status": "active"}
    )
    assert individual.company_code == ""


def test_service_rejects_duplicate_codes(repository: CustomerRepository) -> None:
    service = CustomerService(repository)
    service.create_customer(company_values())
    with pytest.raises(ValueError, match="jau egzistuoja"):
        service.create_customer(company_values("Kitas", " 123 "))


def test_search_filters_and_sort_work_together(
    repository: CustomerRepository,
) -> None:
    service = CustomerService(repository)
    service.create_customer(
        company_values("Žara, UAB", "002") | {"city": "Kaunas", "phone": "222"}
    )
    service.create_customer(
        company_values("Alfa, UAB", "001")
        | {"city": "Vilnius", "email": "info@alfa.lt", "status": "inactive"}
    )
    service.create_customer(
        {"client_type": "individual", "name": "Jonas", "status": "active"}
    )
    assert [item.name for item in service.list_customers()] == [
        "Alfa, UAB",
        "Jonas",
        "Žara, UAB",
    ]
    assert [
        item.name
        for item in service.list_customers(
            "vilnius", client_type="company", status="inactive"
        )
    ] == ["Alfa, UAB"]
    assert [
        item.company_code
        for item in service.list_customers(sort_by="company_code", descending=True)
    ][:2] == ["002", "001"]


class FakeCustomerView:
    SORT_FIELDS = ("name",)

    def __init__(self) -> None:
        self.controller: CustomerController | None = None
        self.customers: list[Customer] = []
        self.total = 0
        self.loading: list[bool] = []
        self.visible = False
        self.selected_id: int | None = None

    def bind_controller(self, controller: CustomerController) -> None:
        self.controller = controller

    def show(self) -> None:
        self.visible = True

    def close(self) -> None:
        self.visible = False

    def set_loading(self, loading: bool) -> None:
        self.loading.append(loading)

    def display_customers(self, customers: list[Customer], total: int) -> None:
        self.customers = customers
        self.total = total

    def selected_customer_id(self) -> int | None:
        return self.selected_id

    def selected_customer(self) -> Customer | None:
        return next((item for item in self.customers if item.id == self.selected_id), None)

    def confirm_delete(self, _name: str) -> bool:
        return True

    def show_error(self, _message: str) -> None:
        raise AssertionError("unexpected error")


class FakeCustomerDialog:
    def __init__(self) -> None:
        self.controller: CustomerController | None = None
        self.customer: Customer | None = None
        self.values: dict[str, str] = {}
        self.visible = False

    def bind_controller(self, controller: CustomerController) -> None:
        self.controller = controller

    def display_customer(
        self, customer: Customer | None, values: dict[str, str]
    ) -> None:
        self.customer = customer
        self.values = values

    def show(self) -> None:
        self.visible = True


def test_controller_crud_and_loading_state(repository: CustomerRepository) -> None:
    service = CustomerService(repository)
    view = FakeCustomerView()
    dialog = FakeCustomerDialog()
    controller = CustomerController(service, view, dialog)  # type: ignore[arg-type]
    controller.start()
    assert view.visible
    assert view.loading == [True, False]
    controller.open_new_customer()
    assert dialog.visible and dialog.customer is None
    customer = controller.save_customer(None, company_values())
    view.selected_id = customer.id
    controller.open_selected_customer()
    assert dialog.customer.id == customer.id
    controller.delete_selected_customer()
    assert service.count_customers() == 0
