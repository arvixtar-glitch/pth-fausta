"""Guarded modal editor for a complete product aggregate."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.product import (
    PRODUCT_STATUS_ACTIVE,
    PRODUCT_STATUS_INACTIVE,
    PRODUCT_TYPE_PRODUCT,
    PRODUCT_TYPE_SERVICE,
    VAT_TREATMENT_NOT_OBJECT,
    VAT_TREATMENT_RATE,
    Product,
    ProductCategory,
    UnitOfMeasure,
)
from app.views.dirty_state import DirtyStateTracker, GuardedDialog
from app.ui.shared import CardDialogShell, ConfirmationDialog, form_field

if TYPE_CHECKING:
    from app.controllers.product_controller import ProductController


class BarcodeDialog(QDialog):
    """Collect one barcode row without applying business validation."""

    def __init__(self, parent: QWidget, value: dict[str, Any] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Barkodas")
        self.barcode_input = QLineEdit(str((value or {}).get("barcode", "")))
        self.type_input = QComboBox()
        for label, code in (
            ("EAN-13", "ean13"),
            ("EAN-8", "ean8"),
            ("UPC-A", "upca"),
            ("Kitas", "other"),
        ):
            self.type_input.addItem(label, code)
        index = self.type_input.findData((value or {}).get("barcode_type", "other"))
        self.type_input.setCurrentIndex(max(index, 0))
        self.default_input = QCheckBox("Numatytasis")
        self.default_input.setChecked(bool((value or {}).get("is_default", False)))
        form = QFormLayout()
        form.addRow("Barkodas", self.barcode_input)
        form.addRow("Tipas", self.type_input)
        form.addRow("", self.default_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "barcode": self.barcode_input.text(),
            "barcode_type": str(self.type_input.currentData()),
            "is_default": self.default_input.isChecked(),
        }


class ProductDialog:
    """Create or edit one product including category, pricing, and barcodes."""

    def __init__(self) -> None:
        self._dialog = GuardedDialog()
        self._dialog.setModal(True)
        self._dialog.setMinimumSize(760, 600)
        self._controller: ProductController | None = None
        self._product: Product | None = None
        self._product_id: int | None = None
        self._loading = False
        self._vat_payer = False
        self._barcodes: list[dict[str, Any]] = []
        self._categories: list[ProductCategory] = []
        self._units: list[UnitOfMeasure] = []
        self._dirty_state = DirtyStateTracker()
        self.product_type = QButtonGroup(self._dialog)
        self.product_radio = QRadioButton("Prekė")
        self.service_radio = QRadioButton("Paslauga")
        self.product_type.addButton(self.product_radio)
        self.product_type.addButton(self.service_radio)
        self.name_input = QLineEdit()
        self.code_input = QLineEdit()
        self.category_input = QComboBox()
        self.unit_input = QComboBox()
        self.status_input = QComboBox()
        self.status_input.addItem("Aktyvi", PRODUCT_STATUS_ACTIVE)
        self.status_input.addItem("Neaktyvi", PRODUCT_STATUS_INACTIVE)
        self.price_input = QLineEdit()
        self.vat_input = QComboBox()
        self.vat_input.addItem("21 %", (VAT_TREATMENT_RATE, "21"))
        self.vat_input.addItem("9 %", (VAT_TREATMENT_RATE, "9"))
        self.vat_input.addItem("5 %", (VAT_TREATMENT_RATE, "5"))
        self.vat_input.addItem("0 %", (VAT_TREATMENT_RATE, "0"))
        self.vat_input.addItem("Ne PVM objektas", (VAT_TREATMENT_NOT_OBJECT, ""))
        self.gross_input = QLineEdit()
        self.gross_input.setReadOnly(True)
        self.notes_input = QTextEdit()
        self._build_ui()
        self._dialog.guard_close_with(self.close)
        for editor in (self.name_input, self.code_input, self.price_input):
            editor.textChanged.connect(self._on_changed)
        for combo in (
            self.category_input,
            self.unit_input,
            self.status_input,
            self.vat_input,
        ):
            combo.currentIndexChanged.connect(self._on_changed)
        self.notes_input.textChanged.connect(self._on_changed)
        self.product_type.buttonClicked.connect(self._on_type_changed)

    def _build_ui(self) -> None:
        shell = CardDialogShell(
            self._dialog,
            close=self.close,
            restore=self.restore_snapshot,
            save=self._save,
        )
        self.title_label = shell.title_label
        self.dirty_label = shell.dirty_label
        self.tabs = shell.tabs
        self.close_button = shell.close_button
        self.cancel_button = shell.cancel_button
        self.save_button = shell.save_button
        self.message_label = shell.message_label
        self._success_timer = shell.success_timer
        self.tabs.addTab(self._general_tab(), "Bendri duomenys")
        self.tabs.addTab(self._pricing_tab(), "Kainodara")
        self.tabs.addTab(self._barcodes_tab(), "Barkodai")
        self.tabs.addTab(self._notes_tab(), "Pastabos")
        shell.add_reserved_tab("Istorija (greitai)")
        shell.add_reserved_tab("Dokumentai (greitai)")

    def _general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        types = QHBoxLayout()
        types.addWidget(self.product_radio)
        types.addWidget(self.service_radio)
        types.addStretch()
        layout.addWidget(QLabel("Tipas *"))
        layout.addLayout(types)
        layout.addWidget(form_field("Pavadinimas", self.name_input, True))
        layout.addWidget(form_field("Kodas", self.code_input))
        category_row = QHBoxLayout()
        category_row.addWidget(self.category_input, 1)
        self.add_category_button = QPushButton("+ Nauja kategorija...")
        self.add_category_button.clicked.connect(self._add_category)
        category_row.addWidget(self.add_category_button)
        category_box = QWidget()
        category_box.setLayout(category_row)
        layout.addWidget(form_field("Kategorija", category_box))
        layout.addWidget(form_field("Vienetas", self.unit_input, True))
        layout.addWidget(form_field("Būsena", self.status_input))
        layout.addStretch()
        return tab

    def _pricing_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.price_field = form_field("Kaina", self.price_input, True)
        self.vat_field = form_field("PVM tarifas", self.vat_input, True)
        self.gross_field = form_field("Kaina su PVM", self.gross_input)
        layout.addWidget(self.price_field)
        layout.addWidget(self.vat_field)
        layout.addWidget(self.gross_field)
        layout.addStretch()
        return tab

    def _barcodes_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        actions = QHBoxLayout()
        self.add_barcode_button = QPushButton("Pridėti")
        self.edit_barcode_button = QPushButton("Redaguoti")
        self.delete_barcode_button = QPushButton("Šalinti")
        actions.addWidget(self.add_barcode_button)
        actions.addWidget(self.edit_barcode_button)
        actions.addWidget(self.delete_barcode_button)
        actions.addStretch()
        self.barcode_table = QTableWidget(0, 3)
        self.barcode_table.setHorizontalHeaderLabels(
            ("Barkodas", "Tipas", "Numatytasis")
        )
        self.add_barcode_button.clicked.connect(self._add_barcode)
        self.edit_barcode_button.clicked.connect(self._edit_barcode)
        self.delete_barcode_button.clicked.connect(self._delete_barcode)
        layout.addLayout(actions)
        layout.addWidget(self.barcode_table)
        return tab

    def _notes_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(form_field("Pastabos", self.notes_input), 1)
        return tab

    def bind_controller(self, controller: ProductController) -> None:
        self._controller = controller

    def display_product(
        self,
        product: Product | None,
        values: dict[str, Any],
        categories: list[ProductCategory],
        units: list[UnitOfMeasure],
        vat_payer: bool,
    ) -> None:
        self._loading = True
        self._product = product
        self._product_id = product.id if product else None
        self._vat_payer = vat_payer
        self._categories = categories
        self._units = units
        self.title_label.setText(
            "Redaguoti įrašą"
            if product
            else (
                "Nauja paslauga"
                if values["product_type"] == PRODUCT_TYPE_SERVICE
                else "Nauja prekė"
            )
        )
        self.name_input.setText(str(values["name"]))
        self.code_input.setText(str(values["code"]))
        self.product_radio.setChecked(values["product_type"] == PRODUCT_TYPE_PRODUCT)
        self.service_radio.setChecked(values["product_type"] == PRODUCT_TYPE_SERVICE)
        self.category_input.clear()
        self.category_input.addItem("— Be kategorijos —", None)
        for category in categories:
            self.category_input.addItem(category.name, category.id)
        self.category_input.setCurrentIndex(
            max(self.category_input.findData(values["category_id"]), 0)
        )
        self.unit_input.clear()
        for unit in units:
            self.unit_input.addItem(unit.name, unit.id)
        self.unit_input.setCurrentIndex(
            max(self.unit_input.findData(values["unit_id"]), 0)
        )
        self.status_input.setCurrentIndex(
            max(self.status_input.findData(values["status"]), 0)
        )
        self.price_input.setText(str(values["unit_price"]))
        desired = (values["vat_treatment"], str(values["vat_rate"]))
        self.vat_input.setCurrentIndex(max(self.vat_input.findData(desired), 0))
        self.notes_input.setPlainText(str(values["notes"]))
        self._barcodes = deepcopy(values["barcodes"])
        self._refresh_barcodes()
        self.price_field.layout().itemAt(0).widget().setText(
            "Kaina be PVM *" if vat_payer else "Kaina *"
        )
        self.vat_field.setVisible(vat_payer)
        self.gross_field.setVisible(vat_payer)
        self._update_gross()
        self.tabs.setCurrentIndex(0)
        self.message_label.clear()
        self._dirty_state.capture(self.values())
        self._loading = False
        self._set_dirty(False)

    def values(self) -> dict[str, Any]:
        treatment, rate = self.vat_input.currentData() or (VAT_TREATMENT_RATE, "21")
        return {
            "product_type": PRODUCT_TYPE_SERVICE
            if self.service_radio.isChecked()
            else PRODUCT_TYPE_PRODUCT,
            "name": self.name_input.text(),
            "code": self.code_input.text(),
            "category_id": self.category_input.currentData(),
            "unit_id": self.unit_input.currentData(),
            "unit_price": self.price_input.text(),
            "vat_treatment": treatment,
            "vat_rate": rate,
            "status": self.status_input.currentData(),
            "notes": self.notes_input.toPlainText(),
            "barcodes": deepcopy(self._barcodes),
        }

    def _on_type_changed(self) -> None:
        if self.service_radio.isChecked() and self._product_id is None:
            index = self.unit_input.findText("val.")
            self.unit_input.setCurrentIndex(
                index if index >= 0 else self.unit_input.currentIndex()
            )
        self._on_changed()

    def _on_changed(self) -> None:
        if not self._loading:
            self._update_gross()
            self.message_label.clear()
            self._success_timer.stop()
            self._set_dirty(self._dirty_state.is_dirty(self.values()))

    def _set_dirty(self, dirty: bool) -> None:
        self.dirty_label.setText("● Neišsaugoti pakeitimai" if dirty else "")
        required = bool(
            self.name_input.text().strip()
            and self.price_input.text().strip()
            and self.unit_input.currentData()
        )
        self.save_button.setEnabled(dirty and required)
        self.cancel_button.setEnabled(dirty)

    def _update_gross(self) -> None:
        if not self._vat_payer or self._controller is None:
            return
        treatment, rate = self.vat_input.currentData() or (VAT_TREATMENT_RATE, "21")
        try:
            self.gross_input.setText(
                f"{self._controller.gross_price(Decimal(self.price_input.text().replace(',', '.') or '0'), treatment, Decimal(rate) if rate else None):.2f}"
            )
        except (InvalidOperation, ValueError):
            self.gross_input.clear()

    def _add_category(self) -> None:
        if self._controller is None:
            return
        from PySide6.QtWidgets import QInputDialog

        name, accepted = QInputDialog.getText(
            self._dialog, "Nauja kategorija", "Pavadinimas"
        )
        if accepted:
            try:
                category = self._controller.add_category(name)
            except ValueError as error:
                self.message_label.setText(str(error))
                return
            index = self.category_input.findData(category.id)
            if index < 0:
                self.category_input.addItem(category.name, category.id)
                index = self.category_input.count() - 1
            if not any(item.id == category.id for item in self._categories):
                self._categories.append(category)
            self.category_input.setCurrentIndex(index)

    def _add_barcode(self) -> None:
        dialog = BarcodeDialog(self._dialog)
        if dialog.exec():
            self._apply_barcode(None, dialog.values())

    def _edit_barcode(self) -> None:
        row = self.barcode_table.currentRow()
        if not 0 <= row < len(self._barcodes):
            return
        dialog = BarcodeDialog(self._dialog, self._barcodes[row])
        if dialog.exec():
            self._apply_barcode(row, dialog.values())

    def _apply_barcode(self, row: int | None, value: dict[str, Any]) -> None:
        if value["is_default"]:
            for item in self._barcodes:
                item["is_default"] = False
        if row is None:
            self._barcodes.append(value)
        else:
            self._barcodes[row] = value
        if self._barcodes and not any(item["is_default"] for item in self._barcodes):
            self._barcodes[0]["is_default"] = True
        self._refresh_barcodes()
        self._on_changed()

    def _delete_barcode(self) -> None:
        row = self.barcode_table.currentRow()
        if 0 <= row < len(self._barcodes):
            was_default = self._barcodes[row]["is_default"]
            self._barcodes.pop(row)
            if was_default and self._barcodes:
                self._barcodes[0]["is_default"] = True
            self._refresh_barcodes()
            self._on_changed()

    def _refresh_barcodes(self) -> None:
        labels = {"ean13": "EAN-13", "ean8": "EAN-8", "upca": "UPC-A", "other": "Kitas"}
        self.barcode_table.setRowCount(len(self._barcodes))
        for row, value in enumerate(self._barcodes):
            for column, text in enumerate(
                (
                    value["barcode"],
                    labels.get(value["barcode_type"], "Kitas"),
                    "Taip" if value["is_default"] else "—",
                )
            ):
                self.barcode_table.setItem(row, column, QTableWidgetItem(str(text)))

    def restore_snapshot(self) -> None:
        values = deepcopy(self._dirty_state.snapshot)
        self.display_product(
            self._product, values, self._categories, self._units, self._vat_payer
        )

    def _save(self) -> None:
        if self._controller is None:
            return
        try:
            product = self._controller.save_product(self._product_id, self.values())
        except (ValueError, LookupError) as error:
            self.message_label.setObjectName("error")
            self.message_label.setText(str(error))
            self._set_dirty(True)
            return
        values = self._controller.product_values(product)
        self.display_product(
            product, values, self._categories, self._units, self._vat_payer
        )
        self.message_label.setObjectName("success")
        self.message_label.setText("Įrašas išsaugotas")
        self._success_timer.start()

    def _confirm_discard(self) -> bool:
        return ConfirmationDialog.ask(
            self._dialog,
            title="Neišsaugoti pakeitimai",
            text=(
                "Turite neišsaugotų pakeitimų. Ar tikrai norite uždaryti neišsaugoję?"
            ),
            destructive_text="Uždaryti neišsaugant",
            cancel_text="Grįžti į formą",
        )

    def show(self) -> None:
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def close(self) -> None:
        if self._dirty_state.is_dirty(self.values()) and not self._confirm_discard():
            return
        self._dialog.force_close()

    def is_visible(self) -> bool:
        return self._dialog.isVisible()
