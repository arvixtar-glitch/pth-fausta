"""Modal customer editor following the shared card-dialog pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)

from app.models.customer import (
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_INACTIVE,
    CUSTOMER_TYPE_COMPANY,
    CUSTOMER_TYPE_INDIVIDUAL,
    Customer,
)
from app.views.dirty_state import DirtyStateTracker, GuardedDialog
from app.ui.shared import CardDialogShell, ConfirmationDialog, form_field

if TYPE_CHECKING:
    from app.controllers.customer_controller import CustomerController


class CustomerDialog:
    """Create or edit one customer in a guarded modal dialog."""

    def __init__(self) -> None:
        self._dialog = GuardedDialog()
        self._dialog.setModal(True)
        self._dialog.setMinimumSize(700, 540)
        self._controller: CustomerController | None = None
        self._customer: Customer | None = None
        self._customer_id: int | None = None
        self._loading = False
        self._dirty_state = DirtyStateTracker()
        self._inputs = {
            name: QLineEdit()
            for name in (
                "name",
                "company_code",
                "vat_code",
                "phone",
                "email",
                "address",
                "city",
                "postal_code",
                "country_code",
            )
        }
        self.notes_input = QTextEdit()
        self.company_type = QRadioButton("Juridinis asmuo")
        self.individual_type = QRadioButton("Fizinis asmuo")
        self.type_group = QButtonGroup(self._dialog)
        self.type_group.addButton(self.company_type)
        self.type_group.addButton(self.individual_type)
        self.status_input = QComboBox()
        self.status_input.addItem("Aktyvus", CUSTOMER_STATUS_ACTIVE)
        self.status_input.addItem("Neaktyvus", CUSTOMER_STATUS_INACTIVE)
        self._build_ui()
        self._dialog.guard_close_with(self.close)
        for editor in self._inputs.values():
            editor.textChanged.connect(self._on_changed)
        self.notes_input.textChanged.connect(self._on_changed)
        self.type_group.buttonClicked.connect(self._on_type_changed)
        self.status_input.currentIndexChanged.connect(self._on_changed)

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
        self.tabs.addTab(self._data_tab(), "Duomenys")
        self.tabs.addTab(self._contacts_tab(), "Kontaktai")
        self.tabs.addTab(self._address_tab(), "Adresas")
        self.tabs.addTab(self._notes_tab(), "Pastabos")
        shell.add_reserved_tab("Istorija (greitai)")

    def _data_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        types = QHBoxLayout()
        types.addWidget(self.company_type)
        types.addWidget(self.individual_type)
        types.addStretch()
        layout.addWidget(QLabel("Kliento tipas *"))
        layout.addLayout(types)
        layout.addWidget(form_field("Pavadinimas", self._inputs["name"], True))
        self.company_code_field = form_field(
            "Kodas", self._inputs["company_code"], True
        )
        self.vat_code_field = form_field("PVM kodas", self._inputs["vat_code"])
        layout.addWidget(self.company_code_field)
        layout.addWidget(self.vat_code_field)
        layout.addWidget(form_field("Būsena", self.status_input))
        layout.addStretch()
        return tab

    def _contacts_tab(self) -> QWidget:
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(form_field("Telefonas", self._inputs["phone"]), 0, 0)
        layout.addWidget(form_field("El. paštas", self._inputs["email"]), 0, 1)
        layout.setRowStretch(1, 1)
        return tab

    def _address_tab(self) -> QWidget:
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(form_field("Gatvė", self._inputs["address"]), 0, 0, 1, 2)
        layout.addWidget(form_field("Miestas", self._inputs["city"]), 1, 0)
        layout.addWidget(form_field("Pašto kodas", self._inputs["postal_code"]), 1, 1)
        layout.addWidget(form_field("Šalis", self._inputs["country_code"]), 2, 0)
        layout.setRowStretch(3, 1)
        return tab

    def _notes_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(form_field("Pastabos", self.notes_input), 1)
        return tab

    def bind_controller(self, controller: CustomerController) -> None:
        self._controller = controller

    def display_customer(
        self, customer: Customer | None, values: dict[str, str]
    ) -> None:
        self._loading = True
        self._customer = customer
        self._customer_id = customer.id if customer else None
        self.title_label.setText(
            "Redaguoti klientą" if customer is not None else "Naujas klientas"
        )
        for name, editor in self._inputs.items():
            editor.setText(values[name])
        self.notes_input.setPlainText(values["notes"])
        is_company = values["client_type"] == CUSTOMER_TYPE_COMPANY
        self.company_type.setChecked(is_company)
        self.individual_type.setChecked(not is_company)
        index = self.status_input.findData(values["status"])
        self.status_input.setCurrentIndex(max(index, 0))
        self._update_type_fields()
        self._dirty_state.capture(self.values())
        self._loading = False
        self.message_label.clear()
        self.tabs.setCurrentIndex(0)
        self._set_dirty(False)

    def values(self) -> dict[str, str]:
        values = {name: editor.text() for name, editor in self._inputs.items()}
        values["notes"] = self.notes_input.toPlainText()
        values["client_type"] = (
            CUSTOMER_TYPE_INDIVIDUAL
            if self.individual_type.isChecked()
            else CUSTOMER_TYPE_COMPANY
        )
        values["status"] = str(self.status_input.currentData())
        return values

    def _on_type_changed(self) -> None:
        self._update_type_fields()
        self._on_changed()

    def _update_type_fields(self) -> None:
        visible = self.company_type.isChecked()
        self.company_code_field.setVisible(visible)
        self.vat_code_field.setVisible(visible)

    def _on_changed(self) -> None:
        if not self._loading:
            self.message_label.clear()
            self._success_timer.stop()
            self._set_dirty(self._dirty_state.is_dirty(self.values()))

    def _set_dirty(self, dirty: bool) -> None:
        self.dirty_label.setText("● Neišsaugoti pakeitimai" if dirty else "")
        required = bool(self._inputs["name"].text().strip()) and (
            self.individual_type.isChecked()
            or bool(self._inputs["company_code"].text().strip())
        )
        self.save_button.setEnabled(dirty and required)
        self.cancel_button.setEnabled(dirty)

    def restore_snapshot(self) -> None:
        values = self._dirty_state.snapshot
        self.display_customer(self._customer, values)

    def _save(self) -> None:
        if self._controller is None:
            return
        self.save_button.setEnabled(False)
        try:
            customer = self._controller.save_customer(self._customer_id, self.values())
        except (ValueError, LookupError) as error:
            self.message_label.setObjectName("error")
            self.message_label.setText(str(error))
            self._set_dirty(True)
            return
        self.display_customer(customer, self._controller.customer_values(customer))
        self.message_label.setObjectName("success")
        self.message_label.setText("Klientas išsaugotas")
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
