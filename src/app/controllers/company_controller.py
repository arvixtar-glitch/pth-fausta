"""Controller for company settings workflows."""

from __future__ import annotations

from app.controllers.base_controller import BaseController
from app.services.company_service import CompanyService
from app.views.company_view import CompanyView


class CompanyController(BaseController):
    """Coordinate company settings UI with the company service."""

    def __init__(self, service: CompanyService, view: CompanyView) -> None:
        super().__init__(view)
        self._service = service
        view.bind_controller(self)

    def start(self) -> None:
        self.refresh()
        self.view.show()

    def refresh(self) -> None:
        company = self._service.get_company()
        self.view.display_company(company)
        accounts = [] if company is None else self._service.list_bank_accounts()
        self.view.display_bank_accounts(accounts)

    def save_company(self, values: dict[str, str]) -> None:
        self._service.save_company(values)
        self.refresh()

    def add_bank_account(self, values: dict[str, object]) -> None:
        self._service.add_bank_account(values)
        self.refresh()

    def update_bank_account(self, account_id: int, values: dict[str, object]) -> None:
        self._service.update_bank_account(account_id, values)
        self.refresh()

    def delete_bank_account(self, account_id: int) -> None:
        self._service.delete_bank_account(account_id)
        self.refresh()

    def set_default_bank_account(self, account_id: int) -> None:
        self._service.set_default_bank_account(account_id)
        self.refresh()
