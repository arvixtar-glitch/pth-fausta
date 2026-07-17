"""Company settings user interface based on the approved design system."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.company import Company, CompanyBankAccount
from app.views.base_view import BaseView

if TYPE_CHECKING:
    from app.controllers.company_controller import CompanyController


def _field(label: str, editor: QWidget, required: bool = False) -> QWidget:
    """Build a vertically labelled form field."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    caption = QLabel(f"{label}{' *' if required else ''}")
    layout.addWidget(caption)
    layout.addWidget(editor)
    return container


class BankAccountDialog(QDialog):
    """Collect and validate bank account values."""

    def __init__(self, account: CompanyBankAccount | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Banko sąskaita")
        self.setMinimumWidth(480)
        self.bank_name = QLineEdit(account.bank_name if account else "")
        self.iban = QLineEdit(account.iban if account else "")
        self.swift_bic = QLineEdit(account.swift_bic if account else "")
        self.account_holder = QLineEdit(account.account_holder if account else "")
        self.currency = QLineEdit(account.currency if account else "EUR")
        self.is_default = QCheckBox("Numatytoji sąskaita")
        self.is_default.setChecked(account.is_default if account else False)
        self.status = QComboBox()
        self.status.addItems(("active", "inactive"))
        self.status.setCurrentText(account.status if account else "active")
        self.error_label = QLabel()
        self.error_label.setObjectName("error")
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.addWidget(_field("Banko pavadinimas", self.bank_name, True), 0, 0)
        grid.addWidget(_field("IBAN", self.iban, True), 0, 1)
        grid.addWidget(_field("BIC / SWIFT", self.swift_bic), 1, 0)
        grid.addWidget(_field("Sąskaitos turėtojas", self.account_holder), 1, 1)
        grid.addWidget(_field("Valiuta", self.currency), 2, 0)
        grid.addWidget(_field("Būsena", self.status), 2, 1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primary")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(grid)
        layout.addWidget(self.is_default)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        missing = []
        if not self.bank_name.text().strip():
            missing.append("banko pavadinimą")
        if not self.iban.text().strip():
            missing.append("IBAN")
        if missing:
            self.error_label.setText("Įveskite " + " ir ".join(missing) + ".")
            return
        self.accept()

    def values(self) -> dict[str, object]:
        return {
            "bank_name": self.bank_name.text(),
            "swift_bic": self.swift_bic.text(),
            "iban": self.iban.text(),
            "account_holder": self.account_holder.text(),
            "currency": self.currency.text(),
            "is_default": self.is_default.isChecked(),
            "status": self.status.currentText(),
        }


class CompanyView(BaseView):
    """Edit company details and manage bank accounts."""

    FIELDS = (
        ("name", "Įmonės pavadinimas", True),
        ("company_code", "Įmonės kodas", False),
        ("vat_code", "PVM mokėtojo kodas", False),
        ("address", "Adresas", False),
        ("city", "Miestas", False),
        ("postal_code", "Pašto kodas", False),
        ("country_code", "Šalies kodas", False),
        ("phone", "Telefonas", False),
        ("email", "El. paštas", False),
        ("website", "Interneto svetainė", False),
    )

    def __init__(self) -> None:
        self._dialog = QDialog()
        self._dialog.setWindowTitle("Įmonės rekvizitai")
        self._dialog.setMinimumSize(760, 600)
        self._dialog.resize(900, 680)
        self._controller: CompanyController | None = None
        self._accounts: list[CompanyBankAccount] = []
        self._inputs = {name: QLineEdit() for name, _label, _required in self.FIELDS}
        self._status = QComboBox()
        self._status.addItems(("active", "inactive"))
        self._snapshot: dict[str, str] = {}
        self._loading = False
        self._build_ui()
        for editor in self._inputs.values():
            editor.textChanged.connect(self._update_dirty_state)
        self._status.currentTextChanged.connect(self._update_dirty_state)

    def _build_ui(self) -> None:
        title = QLabel("Įmonės rekvizitai")
        title.setObjectName("h1")
        self.dirty_label = QLabel()
        self.dirty_label.setObjectName("secondary")
        tabs = QTabWidget()
        tabs.addTab(self._company_tab(), "Bendra informacija")
        tabs.addTab(self._accounts_tab(), "Banko sąskaitos")
        self.cancel_button = QPushButton("Atšaukti")
        self.save_button = QPushButton("Išsaugoti")
        self.save_button.setObjectName("primary")
        self.cancel_button.clicked.connect(self.restore_snapshot)
        self.save_button.clicked.connect(self._save_company)
        self.message_label = QLabel()
        action_bar = QHBoxLayout()
        action_bar.addWidget(self.message_label)
        action_bar.addStretch()
        action_bar.addWidget(self.cancel_button)
        action_bar.addWidget(self.save_button)
        layout = QVBoxLayout(self._dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(self.dirty_label)
        layout.addWidget(tabs, 1)
        layout.addLayout(action_bar)
        self._set_dirty(False)

    def _company_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.addLayout(self._group("Rekvizitai", self.FIELDS[:7]))
        layout.addLayout(self._group("Kontaktai", self.FIELDS[7:]))
        layout.addWidget(_field("Būsena", self._status))
        layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(content)
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll)
        return wrapper

    def _group(self, title: str, fields: tuple[tuple[str, str, bool], ...]) -> QVBoxLayout:
        group = QVBoxLayout()
        heading = QLabel(title)
        heading.setObjectName("h3")
        group.addWidget(heading)
        grid = QGridLayout()
        grid.setSpacing(16)
        for index, (name, label, required) in enumerate(fields):
            grid.addWidget(_field(label, self._inputs[name], required), index // 2, index % 2)
        group.addLayout(grid)
        return group

    def _accounts_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        buttons = QHBoxLayout()
        self.add_button = QPushButton("Pridėti")
        self.edit_button = QPushButton("Redaguoti")
        self.delete_button = QPushButton("Šalinti")
        self.delete_button.setObjectName("danger")
        self.default_button = QPushButton("Nustatyti numatytąją")
        for button, callback in (
            (self.add_button, self._add_account),
            (self.edit_button, self._edit_account),
            (self.delete_button, self._delete_account),
            (self.default_button, self._set_default),
        ):
            button.clicked.connect(callback)
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)
        self.empty_label = QLabel(
            "Banko sąskaitų dar nėra.\nPridėkite pirmąją sąskaitą."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("secondary")
        layout.addWidget(self.empty_label)
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ("Bankas", "IBAN", "BIC / SWIFT", "Valiuta", "Numatytoji", "Būsena")
        )
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._update_account_actions)
        self._table.itemDoubleClicked.connect(lambda _item: self._edit_account())
        layout.addWidget(self._table, 1)
        self._update_account_actions()
        return tab

    def bind_controller(self, controller: CompanyController) -> None:
        self._controller = controller

    def _values(self) -> dict[str, str]:
        values = {name: editor.text() for name, editor in self._inputs.items()}
        values["status"] = self._status.currentText()
        return values

    def display_company(self, company: Company | None) -> None:
        self._loading = True
        for name, _label, _required in self.FIELDS:
            self._inputs[name].setText(getattr(company, name, "") if company else "")
        self._status.setCurrentText(company.status if company else "active")
        self._snapshot = self._values()
        self._loading = False
        self._set_dirty(False)

    def display_bank_accounts(self, accounts: list[CompanyBankAccount]) -> None:
        self._accounts = accounts
        self._table.setRowCount(len(accounts))
        self.empty_label.setVisible(not accounts)
        self._table.setVisible(bool(accounts))
        for row, account in enumerate(accounts):
            values = (
                account.bank_name,
                account.iban,
                account.swift_bic,
                account.currency,
                "Taip" if account.is_default else "Ne",
                account.status,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, account.id)
                self._table.setItem(row, column, item)
        self._update_account_actions()

    def _update_dirty_state(self) -> None:
        if not self._loading:
            self._set_dirty(self._values() != self._snapshot)

    def _set_dirty(self, dirty: bool) -> None:
        self.dirty_label.setText("Yra neišsaugotų pakeitimų" if dirty else "")
        self.save_button.setEnabled(dirty)
        self.cancel_button.setEnabled(dirty)

    def restore_snapshot(self) -> None:
        self._loading = True
        for name, value in self._snapshot.items():
            if name == "status":
                self._status.setCurrentText(value)
            else:
                self._inputs[name].setText(value)
        self._loading = False
        self._set_dirty(False)

    def _run(self, operation: Callable[..., None], *args: object) -> bool:
        try:
            operation(*args)
            return True
        except (ValueError, LookupError) as error:
            self.message_label.setObjectName("error")
            self.message_label.setText(str(error))
            return False

    def _save_company(self) -> None:
        if not self._controller or not self._inputs["name"].text().strip():
            self.message_label.setObjectName("error")
            self.message_label.setText("Įmonės pavadinimas yra privalomas.")
            return
        self.save_button.setEnabled(False)
        if self._run(self._controller.save_company, self._values()):
            self.message_label.setObjectName("success")
            self.message_label.setText("Įmonės duomenys išsaugoti.")

    def _selected_account(self) -> CompanyBankAccount | None:
        row = self._table.currentRow()
        return self._accounts[row] if 0 <= row < len(self._accounts) else None

    def _update_account_actions(self) -> None:
        selected = self._selected_account() is not None
        for button in (self.edit_button, self.delete_button, self.default_button):
            button.setEnabled(selected)

    def _add_account(self) -> None:
        if self._controller:
            dialog = BankAccountDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._run(self._controller.add_bank_account, dialog.values())

    def _edit_account(self) -> None:
        account = self._selected_account()
        if self._controller and account:
            dialog = BankAccountDialog(account)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._run(
                    self._controller.update_bank_account, account.id, dialog.values()
                )

    def _delete_account(self) -> None:
        account = self._selected_account()
        if self._controller and account:
            answer = QMessageBox.question(
                self._dialog, "Patvirtinimas", "Pašalinti sąskaitą?"
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run(self._controller.delete_bank_account, account.id)

    def _set_default(self) -> None:
        account = self._selected_account()
        if self._controller and account:
            self._run(self._controller.set_default_bank_account, account.id)

    def show(self) -> None:
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def close(self) -> None:
        if self._values() != self._snapshot:
            answer = QMessageBox.question(
                self._dialog,
                "Neišsaugoti pakeitimai",
                "Yra neišsaugotų pakeitimų. Ar tikrai norite uždaryti?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Cancel:
                return
            if answer == QMessageBox.StandardButton.Save:
                self._save_company()
                if self._values() != self._snapshot:
                    return
        self._dialog.close()
