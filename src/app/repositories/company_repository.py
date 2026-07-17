"""Company profile data access."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyBankAccount
from app.persistence.session_factory import SessionFactory
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository):
    """Persist the company profile and its bank accounts."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def get_company(self) -> Company | None:
        with self._session_factory.session() as session:
            statement = select(Company).options(selectinload(Company.bank_accounts))
            return session.scalars(statement).first()

    def create_company(self, **values: str) -> Company:
        with self._session_factory.session() as session:
            company = Company(**values)
            session.add(company)
            session.commit()
            session.refresh(company)
            return company

    def save_company(self, company_id: int, **values: str) -> Company:
        with self._session_factory.session() as session:
            company = session.get(Company, company_id)
            if company is None:
                raise LookupError("Company was not found")
            for field, value in values.items():
                setattr(company, field, value)
            session.commit()
            session.refresh(company)
            return company

    def add_bank_account(self, company_id: int, **values: object) -> CompanyBankAccount:
        with self._session_factory.session() as session:
            account = CompanyBankAccount(company_id=company_id, **values)
            session.add(account)
            session.commit()
            session.refresh(account)
            return account

    def update_bank_account(
        self, account_id: int, **values: object
    ) -> CompanyBankAccount:
        with self._session_factory.session() as session:
            account = session.get(CompanyBankAccount, account_id)
            if account is None:
                raise LookupError("Bank account was not found")
            for field, value in values.items():
                setattr(account, field, value)
            session.commit()
            session.refresh(account)
            return account

    def delete_bank_account(self, account_id: int) -> None:
        with self._session_factory.session() as session:
            account = session.get(CompanyBankAccount, account_id)
            if account is None:
                raise LookupError("Bank account was not found")
            session.delete(account)
            session.commit()

    def list_bank_accounts(self, company_id: int) -> list[CompanyBankAccount]:
        with self._session_factory.session() as session:
            statement = (
                select(CompanyBankAccount)
                .where(CompanyBankAccount.company_id == company_id)
                .order_by(CompanyBankAccount.id)
            )
            return list(session.scalars(statement))
