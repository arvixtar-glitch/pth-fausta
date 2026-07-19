"""Product and service list workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from app.models.product import (
    PRODUCT_STATUS_ACTIVE,
    PRODUCT_STATUS_INACTIVE,
    PRODUCT_TYPE_PRODUCT,
    PRODUCT_TYPE_SERVICE,
    VAT_TREATMENT_NOT_APPLICABLE,
    VAT_TREATMENT_NOT_OBJECT,
    Product,
)
from app.ui.shared import ActionTable, BaseListView, ConfirmationDialog

if TYPE_CHECKING:
    from app.controllers.product_controller import ProductController


class ProductTable(ActionTable):
    """Product-specific instance of the shared action table."""

    def __init__(self) -> None:
        super().__init__(8, ProductListView.HEADERS)


class ProductListView(BaseListView):
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
        super().__init__(
            title="Prekės ir paslaugos",
            description="Tvarkykite prekių ir paslaugų sąrašą.",
            table=ProductTable(),
            actions=(
                ("new_product", "Nauja prekė", "primary"),
                ("new_service", "Nauja paslauga", None),
                ("edit", "Redaguoti", None),
                ("delete", "Šalinti", "danger"),
            ),
            search_placeholder="Ieškoti prekės ar paslaugos...",
            filters=(
                (
                    "type",
                    (
                        ("Visi tipai", None),
                        ("Prekė", PRODUCT_TYPE_PRODUCT),
                        ("Paslauga", PRODUCT_TYPE_SERVICE),
                    ),
                ),
                (
                    "status",
                    (
                        ("Visos būsenos", None),
                        ("Aktyvi", PRODUCT_STATUS_ACTIVE),
                        ("Neaktyvi", PRODUCT_STATUS_INACTIVE),
                    ),
                ),
            ),
            loading_text="Kraunamos prekės ir paslaugos...",
            first_action_text="Sukurti pirmą įrašą",
            initial_count_text="0 įrašų",
        )
        self._controller: ProductController | None = None
        self._products: list[Product] = []
        self._vat_payer = False
        self.new_product_button = self.toolbar.buttons["new_product"]
        self.new_service_button = self.toolbar.buttons["new_service"]
        self.edit_button = self.toolbar.buttons["edit"]
        self.delete_button = self.toolbar.buttons["delete"]
        self.type_filter = self.filters["type"]
        self.status_filter = self.filters["status"]
        self.first_product_button = self.first_action_button
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
            lambda _index: controller.set_type_filter(self.type_filter.currentData())
        )
        self.status_filter.currentIndexChanged.connect(
            lambda _index: controller.set_status_filter(
                self.status_filter.currentData()
            )
        )
        self.table.itemSelectionChanged.connect(self._update_actions)
        self.table.itemDoubleClicked.connect(
            lambda _item: controller.open_selected_product()
        )
        self.table.horizontalHeader().sectionClicked.connect(controller.sort_by_column)
        self.table.on_activate = controller.open_selected_product
        self.table.on_delete = controller.deactivate_selected_product

    def set_vat_payer(self, value: bool) -> None:
        self._vat_payer = value
        self.table.setColumnHidden(6, not value)

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
        self.display_state(
            visible_count=len(products),
            total_count=total_count,
            empty_message="Kol kas nėra nei vienos prekės ar paslaugos.",
            empty_description="Sukurkite pirmą įrašą.",
            no_results_message="Pagal pasirinktus filtrus nieko nerasta.",
            no_results_description="Pakeiskite paiešką arba filtrus.",
        )
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
        return ConfirmationDialog.ask(
            self._widget,
            title="Šalinti įrašą",
            text=f"Ar tikrai norite pašalinti „{name}“? Įrašas taps neaktyvus.",
            destructive_text="Šalinti",
        )

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self._widget, "Prekės ir paslaugos", message)
