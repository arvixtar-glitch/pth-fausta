"""Controller for customer list and editor workflows."""

from __future__ import annotations

from app.controllers.base_controller import BaseController
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.views.customer_dialog import CustomerDialog
from app.views.customer_list_view import CustomerListView


class CustomerController(BaseController):
    """Coordinate customer views with customer business operations."""

    def __init__(
        self,
        service: CustomerService,
        view: CustomerListView,
        dialog: CustomerDialog,
    ) -> None:
        super().__init__(view)
        self._service = service
        self._dialog = dialog
        self._query = ""
        self._client_type: str | None = None
        self._status: str | None = None
        self._sort_by = "name"
        self._descending = False
        view.bind_controller(self)
        dialog.bind_controller(self)

    def start(self) -> None:
        self.view.show()
        self.refresh()

    def refresh(self) -> None:
        self.view.set_loading(True)
        try:
            customers = self._service.list_customers(
                self._query,
                self._client_type,
                self._status,
                self._sort_by,
                self._descending,
            )
            self.view.display_customers(customers, self._service.count_customers())
        except (ValueError, LookupError) as error:
            self.view.show_error(str(error))
        finally:
            self.view.set_loading(False)

    def set_search(self, query: str) -> None:
        self._query = query
        self.refresh()

    def set_type_filter(self, client_type: str | None) -> None:
        self._client_type = client_type
        self.refresh()

    def set_status_filter(self, status: str | None) -> None:
        self._status = status
        self.refresh()

    def sort_by_column(self, column: int) -> None:
        sort_by = self.view.SORT_FIELDS[column]
        if self._sort_by == sort_by:
            self._descending = not self._descending
        else:
            self._sort_by = sort_by
            self._descending = False
        self.refresh()
        order = "▼" if self._descending else "▲"
        labels = [
            "Pavadinimas",
            "Kodas",
            "PVM kodas",
            "Telefonas",
            "El. paštas",
            "Miestas",
            "Būsena",
        ]
        labels[column] = f"{labels[column]} {order}"
        self.view.table.setHorizontalHeaderLabels(labels)

    def open_new_customer(self) -> None:
        self._dialog.display_customer(None, self._service.customer_values())
        self._dialog.show()

    def open_selected_customer(self) -> None:
        customer_id = self.view.selected_customer_id()
        if customer_id is None:
            return
        customer = self._service.get_customer(customer_id)
        self._dialog.display_customer(
            customer, self._service.customer_values(customer)
        )
        self._dialog.show()

    def delete_selected_customer(self) -> None:
        customer = self.view.selected_customer()
        if customer is None or not self.view.confirm_delete(customer.name):
            return
        try:
            self._service.delete_customer(customer.id)
            self.refresh()
        except (ValueError, LookupError) as error:
            self.view.show_error(str(error))

    def save_customer(
        self, customer_id: int | None, values: dict[str, str]
    ) -> Customer:
        customer = (
            self._service.create_customer(values)
            if customer_id is None
            else self._service.update_customer(customer_id, values)
        )
        self.refresh()
        return customer

    def get_customer(self, customer_id: int) -> Customer:
        return self._service.get_customer(customer_id)

    def customer_values(self, customer: Customer | None = None) -> dict[str, str]:
        return self._service.customer_values(customer)
