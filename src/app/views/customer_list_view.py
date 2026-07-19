"""Customer list workspace with search, filters and UI states."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QWidget

from app.models.customer import (
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_INACTIVE,
    CUSTOMER_TYPE_COMPANY,
    CUSTOMER_TYPE_INDIVIDUAL,
    Customer,
)
from app.ui.shared import (
    ActionTable,
    BaseListView,
    ConfirmationDialog,
)
from app.ui.theme import COLOR_SUCCESS, COLOR_TEXT_SECONDARY

if TYPE_CHECKING:
    from app.controllers.customer_controller import CustomerController


class CustomerTable(ActionTable):
    """Customer-specific instance of the shared action table."""

    def __init__(self) -> None:
        super().__init__(
            7,
            (
                "Pavadinimas",
                "Kodas",
                "PVM kodas",
                "Telefonas",
                "El. paštas",
                "Miestas",
                "Būsena",
            ),
        )


class CustomerListView(BaseListView):
    """Present and interact with the customer collection."""

    SORT_FIELDS = (
        "name",
        "company_code",
        "vat_code",
        "phone",
        "email",
        "city",
        "status",
    )

    def __init__(self) -> None:
        super().__init__(
            title="Klientai",
            description="Tvarkykite klientų sąrašą ir jų kontaktinius duomenis.",
            table=CustomerTable(),
            actions=(
                ("new", "Naujas klientas", "primary"),
                ("edit", "Redaguoti", None),
                ("delete", "Šalinti", "danger"),
            ),
            search_placeholder="Ieškoti kliento...",
            filters=(
                (
                    "type",
                    (
                        ("Visi tipai", None),
                        ("Juridinis", CUSTOMER_TYPE_COMPANY),
                        ("Fizinis", CUSTOMER_TYPE_INDIVIDUAL),
                    ),
                ),
                (
                    "status",
                    (
                        ("Visos būsenos", None),
                        ("Aktyvus", CUSTOMER_STATUS_ACTIVE),
                        ("Neaktyvus", CUSTOMER_STATUS_INACTIVE),
                    ),
                ),
            ),
            loading_text="Kraunami klientai...",
            first_action_text="Sukurti pirmą klientą",
            initial_count_text="0 klientų",
        )
        self._controller: CustomerController | None = None
        self._customers: list[Customer] = []
        self.new_button = self.toolbar.buttons["new"]
        self.edit_button = self.toolbar.buttons["edit"]
        self.delete_button = self.toolbar.buttons["delete"]
        self.type_filter = self.filters["type"]
        self.status_filter = self.filters["status"]
        self.first_customer_button = self.first_action_button
        QWidget.setTabOrder(self.search_input, self.status_filter)
        QWidget.setTabOrder(self.status_filter, self.type_filter)
        QWidget.setTabOrder(self.type_filter, self.new_button)
        self._update_actions()

    def bind_controller(self, controller: CustomerController) -> None:
        self._controller = controller
        self.new_button.clicked.connect(controller.open_new_customer)
        self.first_customer_button.clicked.connect(controller.open_new_customer)
        self.edit_button.clicked.connect(controller.open_selected_customer)
        self.delete_button.clicked.connect(controller.delete_selected_customer)
        self.search_input.textChanged.connect(controller.set_search)
        self.type_filter.currentIndexChanged.connect(
            lambda _index: controller.set_type_filter(self.type_filter.currentData())
        )
        self.status_filter.currentIndexChanged.connect(
            lambda _index: controller.set_status_filter(
                self.status_filter.currentData()
            )
        )
        self.table.itemSelectionChanged.connect(self._update_actions)
        self.table.itemDoubleClicked.connect(
            lambda _item: controller.open_selected_customer()
        )
        self.table.horizontalHeader().sectionClicked.connect(controller.sort_by_column)
        self.table.on_activate = controller.open_selected_customer
        self.table.on_delete = controller.delete_selected_customer

    def display_customers(self, customers: list[Customer], total_count: int) -> None:
        self._customers = customers
        self.table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            values = (
                customer.name,
                customer.company_code or "—",
                customer.vat_code or "—",
                customer.phone or "—",
                customer.email or "—",
                customer.city or "—",
                "Aktyvus" if customer.status == CUSTOMER_STATUS_ACTIVE else "Neaktyvus",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, customer.id)
                if column == 6:
                    item.setForeground(
                        QColor(
                            COLOR_SUCCESS
                            if customer.status == CUSTOMER_STATUS_ACTIVE
                            else COLOR_TEXT_SECONDARY
                        )
                    )
                self.table.setItem(row, column, item)
        self.count_label.setText(f"{len(customers)} klientų")
        self.display_state(
            visible_count=len(customers),
            total_count=total_count,
            empty_message="Kol kas nėra nė vieno kliento.",
            empty_description=(
                "Sukurkite pirmą klientą, kad galėtumėte pradėti darbą."
            ),
            no_results_message="Pagal pasirinktus filtrus klientų nerasta.",
            no_results_description="Pakeiskite paiešką arba pasirinktus filtrus.",
        )
        self.new_button.setEnabled(True)
        self._update_actions()

    def selected_customer_id(self) -> int | None:
        row = self.table.currentRow()
        if not 0 <= row < len(self._customers):
            return None
        return self._customers[row].id

    def selected_customer(self) -> Customer | None:
        row = self.table.currentRow()
        return self._customers[row] if 0 <= row < len(self._customers) else None

    def _update_actions(self) -> None:
        selected = self.selected_customer_id() is not None
        self.edit_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def confirm_delete(self, customer_name: str) -> bool:
        return ConfirmationDialog.ask(
            self._widget,
            title="Šalinti klientą",
            text=(
                f"Ar tikrai norite pašalinti klientą {customer_name}? "
                "Šio veiksmo nebus galima atšaukti."
            ),
            destructive_text="Šalinti",
        )

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self._widget, "Klientai", message)
