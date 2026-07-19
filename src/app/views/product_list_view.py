"""Product and service list workspace."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
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

from app.models.product import (
    PRODUCT_STATUS_ACTIVE,
    PRODUCT_STATUS_INACTIVE,
    PRODUCT_TYPE_PRODUCT,
    PRODUCT_TYPE_SERVICE,
    VAT_TREATMENT_NOT_APPLICABLE,
    VAT_TREATMENT_NOT_OBJECT,
    Product,
)
from app.views.base_view import BaseView
from app.views.customer_list_view import SortableHeader

if TYPE_CHECKING:
    from app.controllers.product_controller import ProductController


class ProductTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 8)
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


class ProductListView(BaseView):
    SORT_FIELDS = (
        "name",
        "code",
        "name",
        "product_type",
        "unit",
        "unit_price",
        "vat_rate",
        "status",
    )
    HEADERS = (
        "Pavadinimas",
        "Kodas",
        "Barkodas",
        "Tipas",
        "Vnt.",
        "Kaina",
        "PVM",
        "Būsena",
    )

    def __init__(self) -> None:
        self._widget = QWidget()
        self._controller: ProductController | None = None
        self._products: list[Product] = []
        self._vat_payer = False
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Prekės ir paslaugos")
        title.setObjectName("h1")
        description = QLabel("Tvarkykite prekių ir paslaugų sąrašą.")
        description.setObjectName("secondary")
        heading_text = QVBoxLayout()
        heading_text.addWidget(title)
        heading_text.addWidget(description)
        self.new_product_button = QPushButton("Nauja prekė")
        self.new_product_button.setObjectName("primary")
        self.new_service_button = QPushButton("Nauja paslauga")
        self.edit_button = QPushButton("Redaguoti")
        self.delete_button = QPushButton("Šalinti")
        self.delete_button.setObjectName("danger")
        heading = QHBoxLayout()
        heading.addLayout(heading_text)
        heading.addStretch()
        for button in (
            self.new_product_button,
            self.new_service_button,
            self.edit_button,
            self.delete_button,
        ):
            heading.addWidget(button)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ieškoti prekės ar paslaugos...")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Visi tipai", None)
        self.type_filter.addItem("Prekė", PRODUCT_TYPE_PRODUCT)
        self.type_filter.addItem("Paslauga", PRODUCT_TYPE_SERVICE)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Visos būsenos", None)
        self.status_filter.addItem("Aktyvi", PRODUCT_STATUS_ACTIVE)
        self.status_filter.addItem("Neaktyvi", PRODUCT_STATUS_INACTIVE)
        filters = QHBoxLayout()
        filters.addWidget(self.search_input, 1)
        filters.addWidget(self.type_filter)
        filters.addWidget(self.status_filter)
        self.content = QStackedWidget()
        self.table = ProductTable()
        self.table.setHorizontalHeader(SortableHeader())
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.content.addWidget(self.table)
        self.loading_page = QWidget()
        loading = QVBoxLayout(self.loading_page)
        loading.addStretch()
        label = QLabel("Kraunamos prekės ir paslaugos...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)
        loading.addWidget(label)
        loading.addWidget(self.loading_indicator)
        loading.addStretch()
        self.content.addWidget(self.loading_page)
        self.empty_page = QWidget()
        empty = QVBoxLayout(self.empty_page)
        empty.addStretch()
        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_description = QLabel()
        self.empty_description.setObjectName("secondary")
        self.empty_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.first_product_button = QPushButton("Sukurti pirmą įrašą")
        self.first_product_button.setObjectName("primary")
        empty.addWidget(self.empty_label)
        empty.addWidget(self.empty_description)
        empty.addWidget(
            self.first_product_button, alignment=Qt.AlignmentFlag.AlignCenter
        )
        empty.addStretch()
        self.content.addWidget(self.empty_page)
        self.count_label = QLabel("0 įrašų")
        self.count_label.setObjectName("secondary")
        status = QHBoxLayout()
        status.addStretch()
        status.addWidget(self.count_label)
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(16)
        layout.addLayout(heading)
        layout.addLayout(filters)
        layout.addWidget(self.content, 1)
        layout.addLayout(status)
        self._update_actions()

    def bind_controller(self, controller: ProductController) -> None:
        self._controller = controller
        self.new_product_button.clicked.connect(controller.open_new_product)
        self.first_product_button.clicked.connect(controller.open_new_product)
        self.new_service_button.clicked.connect(controller.open_new_service)
        self.edit_button.clicked.connect(controller.open_selected_product)
        self.delete_button.clicked.connect(controller.deactivate_selected_product)
        self.search_input.textChanged.connect(controller.set_search)
        self.type_filter.currentIndexChanged.connect(
            lambda _i: controller.set_type_filter(self.type_filter.currentData())
        )
        self.status_filter.currentIndexChanged.connect(
            lambda _i: controller.set_status_filter(self.status_filter.currentData())
        )
        self.table.itemSelectionChanged.connect(self._update_actions)
        self.table.itemDoubleClicked.connect(
            lambda _item: controller.open_selected_product()
        )
        self.table.horizontalHeader().sectionClicked.connect(controller.sort_by_column)
        self.table.on_activate = controller.open_selected_product
        self.table.on_delete = controller.deactivate_selected_product

    @property
    def widget(self) -> QWidget:
        return self._widget

    def set_vat_payer(self, value: bool) -> None:
        self._vat_payer = value
        self.table.setColumnHidden(6, not value)

    def set_loading(self, loading: bool) -> None:
        if loading:
            self.content.setCurrentWidget(self.loading_page)
            for widget in (
                self.search_input,
                self.type_filter,
                self.status_filter,
                self.new_product_button,
                self.new_service_button,
                self.edit_button,
                self.delete_button,
            ):
                widget.setEnabled(False)
        elif self.content.currentWidget() is self.loading_page:
            self.content.setCurrentWidget(self.table)

    def display_products(self, products: list[Product], total_count: int) -> None:
        self._products = products
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            barcode = (
                product.default_barcode.barcode if product.default_barcode else "—"
            )
            vat = (
                "—"
                if product.vat_treatment
                in (VAT_TREATMENT_NOT_OBJECT, VAT_TREATMENT_NOT_APPLICABLE)
                else f"{product.vat_rate:g}%"
            )
            values = (
                product.name,
                product.code or "—",
                barcode,
                "Prekė" if product.product_type == PRODUCT_TYPE_PRODUCT else "Paslauga",
                product.unit.code,
                f"{product.unit_price:.2f}",
                vat,
                "Aktyvi" if product.status == PRODUCT_STATUS_ACTIVE else "Neaktyvi",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, product.id)
                self.table.setItem(row, column, item)
        self.count_label.setText(f"{len(products)} įrašų")
        if products:
            self.content.setCurrentWidget(self.table)
        else:
            empty = total_count == 0
            self.empty_label.setText(
                "Kol kas nėra nei vienos prekės ar paslaugos."
                if empty
                else "Pagal pasirinktus filtrus nieko nerasta."
            )
            self.empty_description.setText(
                "Sukurkite pirmą įrašą."
                if empty
                else "Pakeiskite paiešką arba filtrus."
            )
            self.first_product_button.setVisible(empty)
            self.content.setCurrentWidget(self.empty_page)
        enabled = total_count > 0
        self.search_input.setEnabled(enabled)
        self.type_filter.setEnabled(enabled)
        self.status_filter.setEnabled(enabled)
        self.new_product_button.setEnabled(True)
        self.new_service_button.setEnabled(True)
        self._update_actions()

    def selected_product_id(self) -> int | None:
        row = self.table.currentRow()
        return self._products[row].id if 0 <= row < len(self._products) else None

    def selected_product(self) -> Product | None:
        row = self.table.currentRow()
        return self._products[row] if 0 <= row < len(self._products) else None

    def _update_actions(self) -> None:
        selected = self.selected_product_id() is not None
        self.edit_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def confirm_delete(self, name: str) -> bool:
        message = QMessageBox(self._widget)
        message.setWindowTitle("Šalinti įrašą")
        message.setText(f"Ar tikrai norite pašalinti „{name}“? Įrašas taps neaktyvus.")
        cancel = message.addButton("Atšaukti", QMessageBox.ButtonRole.RejectRole)
        deactivate = message.addButton(
            "Šalinti", QMessageBox.ButtonRole.DestructiveRole
        )
        message.setDefaultButton(cancel)
        message.exec()
        return message.clickedButton() is deactivate

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self._widget, "Prekės ir paslaugos", message)

    def show(self) -> None:
        self._widget.show()

    def close(self) -> None:
        self._widget.hide()
