"""Customer data access."""

from __future__ import annotations

from sqlalchemy import select

from app.models.customer import Customer
from app.persistence.session_factory import SessionFactory
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    """Persist customers without applying business rules."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def create(self, **values: str) -> Customer:
        with self._session_factory.session() as session:
            customer = Customer(**values)
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer

    def get(self, customer_id: int) -> Customer | None:
        with self._session_factory.session() as session:
            return session.get(Customer, customer_id)

    def list_all(self) -> list[Customer]:
        with self._session_factory.session() as session:
            return list(session.scalars(select(Customer).order_by(Customer.name)))

    def update(self, customer_id: int, **values: str) -> Customer:
        with self._session_factory.session() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                raise LookupError("Klientas nerastas.")
            for field, value in values.items():
                setattr(customer, field, value)
            session.commit()
            session.refresh(customer)
            return customer

    def delete(self, customer_id: int) -> None:
        with self._session_factory.session() as session:
            customer = session.get(Customer, customer_id)
            if customer is None:
                raise LookupError("Klientas nerastas.")
            session.delete(customer)
            session.commit()
