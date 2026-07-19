"""Controller for product list and aggregate editor workflows."""

from __future__ import annotations

from typing import Any

from app.controllers.base_controller import BaseController
from app.models.product import PRODUCT_TYPE_PRODUCT, PRODUCT_TYPE_SERVICE, Product
from app.services.product_service import ProductService
from app.views.product_dialog import ProductDialog
from app.views.product_list_view import ProductListView


class ProductController(BaseController):
    """Coordinate product views with product business operations."""

    def __init__(
        self, service: ProductService, view: ProductListView, dialog: ProductDialog
    ) -> None:
        super().__init__(view)
        self._service = service
        self._dialog = dialog
        self._query = ""
        self._product_type: str | None = None
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
            self.view.set_vat_payer(self._service.is_vat_payer())
            products = self._service.list_products(
                self._query,
                self._product_type,
                self._status,
                self._sort_by,
                self._descending,
            )
            self.view.display_products(products, self._service.count_products())
        except (ValueError, LookupError) as error:
            self.view.show_error(str(error))
        finally:
            self.view.set_loading(False)

    def set_search(self, query: str) -> None:
        self._query = query
        self.refresh()

    def set_type_filter(self, value: str | None) -> None:
        self._product_type = value
        self.refresh()

    def set_status_filter(self, value: str | None) -> None:
        self._status = value
        self.refresh()

    def sort_by_column(self, column: int) -> None:
        field = self.view.SORT_FIELDS[column]
        if self._sort_by == field:
            self._descending = not self._descending
        else:
            self._sort_by, self._descending = field, False
        self.refresh()
        labels = list(self.view.HEADERS)
        labels[column] = f"{labels[column]} {'▼' if self._descending else '▲'}"
        self.view.table.setHorizontalHeaderLabels(labels)

    def open_new_product(self) -> None:
        self._open_new(PRODUCT_TYPE_PRODUCT)

    def open_new_service(self) -> None:
        self._open_new(PRODUCT_TYPE_SERVICE)

    def _open_new(self, product_type: str) -> None:
        self._dialog.display_product(
            None,
            self._service.product_values(product_type=product_type),
            self._service.list_categories(),
            self._service.list_units(),
            self._service.is_vat_payer(),
        )
        self._dialog.show()

    def open_selected_product(self) -> None:
        product_id = self.view.selected_product_id()
        if product_id is None:
            return
        product = self._service.get_product(product_id)
        self._dialog.display_product(
            product,
            self._service.product_values(product),
            self._service.list_categories(),
            self._service.list_units(),
            self._service.is_vat_payer(),
        )
        self._dialog.show()

    def deactivate_selected_product(self) -> None:
        product = self.view.selected_product()
        if product is None or not self.view.confirm_delete(product.name):
            return
        try:
            self._service.deactivate_product(product.id)
            self.refresh()
        except (ValueError, LookupError) as error:
            self.view.show_error(str(error))

    def save_product(self, product_id: int | None, values: dict[str, Any]) -> Product:
        product = self._service.save_product(product_id, values)
        self.refresh()
        return product

    def add_category(self, name: str):
        return self._service.add_category(name)

    def product_values(self, product: Product) -> dict[str, Any]:
        return self._service.product_values(product)

    def gross_price(self, price, treatment: str, rate):
        return self._service.gross_price(price, treatment, rate)
