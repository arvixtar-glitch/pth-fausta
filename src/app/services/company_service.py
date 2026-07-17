"""Company profile business rules."""

from __future__ import annotations

from app.models.company import Company, CompanyBankAccount
from app.repositories.company_repository import CompanyRepository
from app.services.base_service import BaseService


class CompanyService(BaseService):
    """Manage the company profile and enforce bank account rules."""

    def __init__(self, repository: CompanyRepository) -> None:
        self._repository = repository

    def get_company(self) -> Company | None:
        return self._repository.get_company()

    def save_company(self, values: dict[str, str]) -> Company:
        clean_values = {key: value.strip() for key, value in values.items()}
        if not clean_values.get("name"):
            raise ValueError("Company name is required")
        company = self.get_company()
        if company is None:
            return self._repository.create_company(**clean_values)
        return self._repository.save_company(company.id, **clean_values)

    def list_bank_accounts(self) -> list[CompanyBankAccount]:
        company = self._require_company()
        return self._repository.list_bank_accounts(company.id)

    def add_bank_account(self, values: dict[str, object]) -> CompanyBankAccount:
        company = self._require_company()
        clean_values = self._validate_account(values)
        accounts = self._repository.list_bank_accounts(company.id)
        if not accounts:
            clean_values["is_default"] = True
        elif clean_values["is_default"]:
            self._clear_default(accounts)
        return self._repository.add_bank_account(company.id, **clean_values)

    def update_bank_account(
        self, account_id: int, values: dict[str, object]
    ) -> CompanyBankAccount:
        company = self._require_company()
        accounts = self._repository.list_bank_accounts(company.id)
        current = next((item for item in accounts if item.id == account_id), None)
        if current is None:
            raise LookupError("Bank account was not found")
        clean_values = self._validate_account(values)
        if clean_values["is_default"]:
            self._clear_default(accounts, except_id=account_id)
        elif current.is_default and len(accounts) > 1:
            raise ValueError("Choose another default account first")
        return self._repository.update_bank_account(account_id, **clean_values)

    def delete_bank_account(self, account_id: int) -> None:
        company = self._require_company()
        accounts = self._repository.list_bank_accounts(company.id)
        current = next((item for item in accounts if item.id == account_id), None)
        if current is None:
            raise LookupError("Bank account was not found")
        self._repository.delete_bank_account(account_id)
        remaining = [item for item in accounts if item.id != account_id]
        if current.is_default and remaining:
            self._repository.update_bank_account(remaining[0].id, is_default=True)

    def set_default_bank_account(self, account_id: int) -> CompanyBankAccount:
        company = self._require_company()
        accounts = self._repository.list_bank_accounts(company.id)
        if not any(item.id == account_id for item in accounts):
            raise LookupError("Bank account was not found")
        self._clear_default(accounts, except_id=account_id)
        return self._repository.update_bank_account(account_id, is_default=True)

    def _require_company(self) -> Company:
        company = self.get_company()
        if company is None:
            raise ValueError("Save the company profile first")
        return company

    def _clear_default(
        self, accounts: list[CompanyBankAccount], except_id: int | None = None
    ) -> None:
        for account in accounts:
            if account.is_default and account.id != except_id:
                self._repository.update_bank_account(account.id, is_default=False)

    def _validate_account(self, values: dict[str, object]) -> dict[str, object]:
        cleaned = dict(values)
        for field in ("bank_name", "swift_bic", "iban", "account_holder", "currency"):
            cleaned[field] = str(cleaned.get(field, "")).strip()
        if not cleaned["bank_name"]:
            raise ValueError("Bank name is required")
        if not cleaned["iban"]:
            raise ValueError("IBAN is required")
        cleaned["currency"] = str(cleaned["currency"]).upper() or "EUR"
        cleaned["is_default"] = bool(cleaned.get("is_default", False))
        cleaned["status"] = str(cleaned.get("status", "active"))
        return cleaned
