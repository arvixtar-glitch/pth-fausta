"""Customer business rules and list queries."""

from __future__ import annotations

from app.models.customer import (
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_INACTIVE,
    CUSTOMER_TYPE_COMPANY,
    CUSTOMER_TYPE_INDIVIDUAL,
    Customer,
)
from app.repositories.customer_repository import CustomerRepository
from app.services.base_service import BaseService

CUSTOMER_FIELDS = (
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
)
SORTABLE_FIELDS = {
    "name",
    "company_code",
    "vat_code",
    "phone",
    "email",
    "city",
    "status",
}


class CustomerService(BaseService):
    """Manage customer CRUD, validation and list transformations."""

    def __init__(self, repository: CustomerRepository) -> None:
        self._repository = repository

    def get_customer(self, customer_id: int) -> Customer:
        customer = self._repository.get(customer_id)
        if customer is None:
            raise LookupError("Klientas nerastas.")
        return customer

    def list_customers(
        self,
        query: str = "",
        client_type: str | None = None,
        status: str | None = None,
        sort_by: str = "name",
        descending: bool = False,
    ) -> list[Customer]:
        if client_type not in (None, CUSTOMER_TYPE_COMPANY, CUSTOMER_TYPE_INDIVIDUAL):
            raise ValueError("Neteisingas kliento tipo filtras.")
        if status not in (None, CUSTOMER_STATUS_ACTIVE, CUSTOMER_STATUS_INACTIVE):
            raise ValueError("Neteisingas būsenos filtras.")
        if sort_by not in SORTABLE_FIELDS:
            raise ValueError("Neteisingas rūšiavimo laukas.")
        normalized_query = self._normalize(query)
        customers = [
            customer
            for customer in self._repository.list_all()
            if (client_type is None or customer.client_type == client_type)
            and (status is None or customer.status == status)
            and (not normalized_query or normalized_query in customer.search_text)
        ]
        return sorted(
            customers,
            key=lambda customer: self._normalize(str(getattr(customer, sort_by))),
            reverse=descending,
        )

    def count_customers(self) -> int:
        return len(self._repository.list_all())

    def create_customer(self, values: dict[str, str]) -> Customer:
        cleaned = self._validate(values)
        self._ensure_unique(cleaned)
        return self._repository.create(**cleaned)

    def update_customer(self, customer_id: int, values: dict[str, str]) -> Customer:
        self.get_customer(customer_id)
        cleaned = self._validate(values)
        self._ensure_unique(cleaned, except_id=customer_id)
        return self._repository.update(customer_id, **cleaned)

    def delete_customer(self, customer_id: int) -> None:
        self.get_customer(customer_id)
        self._repository.delete(customer_id)

    def customer_values(self, customer: Customer | None = None) -> dict[str, str]:
        """Return normalized form values suitable for dirty-state snapshots."""
        defaults = {
            "client_type": CUSTOMER_TYPE_COMPANY,
            "country_code": "Lietuva",
            "status": CUSTOMER_STATUS_ACTIVE,
        }
        return {
            field: str(getattr(customer, field, defaults.get(field, "")))
            if customer is not None
            else defaults.get(field, "")
            for field in CUSTOMER_FIELDS
        }

    def _validate(self, values: dict[str, str]) -> dict[str, str]:
        cleaned = {field: str(values.get(field, "")).strip() for field in CUSTOMER_FIELDS}
        if cleaned["client_type"] not in (
            CUSTOMER_TYPE_COMPANY,
            CUSTOMER_TYPE_INDIVIDUAL,
        ):
            raise ValueError("Pasirinkite teisingą kliento tipą.")
        if not cleaned["name"]:
            raise ValueError("Pavadinimas yra privalomas.")
        if cleaned["client_type"] == CUSTOMER_TYPE_COMPANY and not cleaned[
            "company_code"
        ]:
            raise ValueError("Juridinio asmens kodas yra privalomas.")
        if cleaned["status"] not in (
            CUSTOMER_STATUS_ACTIVE,
            CUSTOMER_STATUS_INACTIVE,
        ):
            raise ValueError("Pasirinkite teisingą kliento būseną.")
        cleaned["search_text"] = self._build_search_text(cleaned)
        return cleaned

    def _ensure_unique(self, values: dict[str, str], except_id: int | None = None) -> None:
        company_code = self._normalize(values["company_code"])
        vat_code = self._normalize(values["vat_code"])
        for customer in self._repository.list_all():
            if customer.id == except_id:
                continue
            if company_code and self._normalize(customer.company_code) == company_code:
                raise ValueError("Klientas su tokiu kodu jau egzistuoja.")
            if vat_code and self._normalize(customer.vat_code) == vat_code:
                raise ValueError("Klientas su tokiu PVM kodu jau egzistuoja.")

    def _build_search_text(self, values: dict[str, str]) -> str:
        fields = (
            "name",
            "company_code",
            "vat_code",
            "phone",
            "email",
            "address",
            "city",
        )
        return " ".join(self._normalize(values[field]) for field in fields)

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().split())
