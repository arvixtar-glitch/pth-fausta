"""Customer list workspace with search, filters and UI states."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.customer import (
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_INACTIVE,
    CUSTOMER_TYPE_COMPANY,
    CUSTOMER_TYPE_INDIVIDUAL,
    Customer,
)
from app.views.base_view import BaseView
from app.ui.theme import COLOR_SUCCESS, COLOR_TEXT_SECONDARY

if TYPE_CHECKING:
    from app.controllers.customer_controller import CustomerController


class CustomerTable(QTableWidget):
    """Expose row activation and deletion through the keyboard."""

    def __init__(self) -> None:
        super().__init__(0, 7)
        self.on_activate: Callable[[], None] | None = None
        self.on_delete: Callable[[], None] | None = None

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.on_activate:
            self.on_activate()
            return
        if event.key() == Qt.Key.Key_Delete and self.on_delete:
            self.on_delete()
            return
        super().keyPressEvent(event)


class SortableHeader(QHeaderView):
    """Make table sorting available with Left/Right and Enter/Space."""

    def __init__(self) -> None:
        super().__init__(Qt.Orientation.Horizontal)
        self._keyboard_section = 0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self._keyboard_section = max(0, self._keyboard_section - 1)
            return
        if event.key() == Qt.Key.Key_Right:
            self._keyboard_section = min(
                self.count() - 1, self._keyboard_section + 1
            )
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.sectionClicked.emit(self._keyboard_section)
            return
        super().keyPressEvent(event)


class CustomerListView(BaseView):
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
        self._widget = QWidget()
        self._controller: CustomerController | None = None
        self._customers: list[Customer] = []
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Klientai")
        title.setObjectName("h1")
        description = QLabel("Tvarkykite klientų sąrašą ir jų kontaktinius duomenis.")
        description.setObjectName("secondary")
        heading_text = QVBoxLayout()
        heading_text.addWidget(title)
        heading_text.addWidget(description)
        self.new_button = QPushButton("Naujas klientas")
        self.new_button.setObjectName("primary")
        self.edit_button = QPushButton("Redaguoti")
        self.delete_button = QPushButton("Šalinti")
        self.delete_button.setObjectName("danger")
        heading = QHBoxLayout()
        heading.addLayout(heading_text)
        heading.addStretch()
        heading.addWidget(self.new_button)
        heading.addWidget(self.edit_button)
        heading.addWidget(self.delete_button)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ieškoti kliento...")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Visi tipai", None)
        self.type_filter.addItem("Juridinis", CUSTOMER_TYPE_COMPANY)
        self.type_filter.addItem("Fizinis", CUSTOMER_TYPE_INDIVIDUAL)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Visos būsenos", None)
        self.status_filter.addItem("Aktyvus", CUSTOMER_STATUS_ACTIVE)
        self.status_filter.addItem("Neaktyvus", CUSTOMER_STATUS_INACTIVE)
        filters = QHBoxLayout()
        filters.addWidget(self.search_input, 1)
        filters.addWidget(self.type_filter)
        filters.addWidget(self.status_filter)
        self.content = QStackedWidget()
        self.table = CustomerTable()
        self.table.setHorizontalHeader(SortableHeader())
        self.table.setHorizontalHeaderLabels(
            ("Pavadinimas", "Kodas", "PVM kodas", "Telefonas", "El. paštas", "Miestas", "Būsena")
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.content.addWidget(self.table)
        self.loading_page = QWidget()
        loading_layout = QVBoxLayout(self.loading_page)
        loading_layout.addStretch()
        loading_label = QLabel("Kraunami klientai...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)
        loading_layout.addWidget(loading_label)
        loading_layout.addWidget(self.loading_indicator)
        loading_layout.addStretch()
        self.content.addWidget(self.loading_page)
        self.empty_page = QWidget()
        empty_layout = QVBoxLayout(self.empty_page)
        empty_layout.addStretch()
        self.empty_icon = QLabel("○")
        self.empty_icon.setObjectName("h1")
        self.empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_description = QLabel()
        self.empty_description.setObjectName("secondary")
        self.empty_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.first_customer_button = QPushButton("Sukurti pirmą klientą")
        self.first_customer_button.setObjectName("primary")
        empty_layout.addWidget(self.empty_icon)
        empty_layout.addWidget(self.empty_label)
        empty_layout.addWidget(self.empty_description)
        empty_layout.addWidget(
            self.first_customer_button, alignment=Qt.AlignmentFlag.AlignCenter
        )
        empty_layout.addStretch()
        self.content.addWidget(self.empty_page)
        self.count_label = QLabel("0 klientų")
        self.count_label.setObjectName("secondary")
        status_bar = QHBoxLayout()
        status_bar.addStretch()
        status_bar.addWidget(self.count_label)
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(16)
        layout.addLayout(heading)
        layout.addLayout(filters)
        layout.addWidget(self.content, 1)
        layout.addLayout(status_bar)
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
            lambda _index: controller.set_status_filter(self.status_filter.currentData())
        )
        self.table.itemSelectionChanged.connect(self._update_actions)
        self.table.itemDoubleClicked.connect(
            lambda _item: controller.open_selected_customer()
        )
        self.table.horizontalHeader().sectionClicked.connect(controller.sort_by_column)
        self.table.on_activate = controller.open_selected_customer
        self.table.on_delete = controller.delete_selected_customer

    @property
    def widget(self) -> QWidget:
        return self._widget

    def set_loading(self, loading: bool) -> None:
        if loading:
            self.content.setCurrentWidget(self.loading_page)
            for widget in (
                self.search_input,
                self.type_filter,
                self.status_filter,
                self.new_button,
                self.edit_button,
                self.delete_button,
            ):
                widget.setEnabled(False)

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
        if customers:
            self.content.setCurrentWidget(self.table)
        else:
            no_customers = total_count == 0
            self.empty_label.setText(
                "Kol kas nėra nė vieno kliento."
                if no_customers
                else "Pagal pasirinktus filtrus klientų nerasta."
            )
            self.empty_description.setText(
                "Sukurkite pirmą klientą, kad galėtumėte pradėti darbą."
                if no_customers
                else "Pakeiskite paiešką arba pasirinktus filtrus."
            )
            self.first_customer_button.setVisible(no_customers)
            self.content.setCurrentWidget(self.empty_page)
        filters_enabled = total_count > 0
        self.search_input.setEnabled(filters_enabled)
        self.type_filter.setEnabled(filters_enabled)
        self.status_filter.setEnabled(filters_enabled)
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
        message = QMessageBox(self._widget)
        message.setWindowTitle("Šalinti klientą")
        message.setText(
            f"Ar tikrai norite pašalinti klientą {customer_name}? "
            "Šio veiksmo nebus galima atšaukti."
        )
        cancel = message.addButton("Atšaukti", QMessageBox.ButtonRole.RejectRole)
        delete = message.addButton("Šalinti", QMessageBox.ButtonRole.DestructiveRole)
        message.setDefaultButton(cancel)
        message.exec()
        return message.clickedButton() is delete

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self._widget, "Klientai", message)

    def show(self) -> None:
        self._widget.show()

    def close(self) -> None:
        self._widget.hide()
