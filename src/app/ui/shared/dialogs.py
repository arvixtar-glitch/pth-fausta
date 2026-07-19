"""Shared building blocks for guarded card-style dialogs."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class CardDialogShell:
    """Build the repeated header, tabs, message, and action-bar layout."""

    def __init__(
        self,
        dialog: QWidget,
        *,
        close: Callable[[], None],
        restore: Callable[[], None],
        save: Callable[[], None],
        success_timeout_ms: int = 3_000,
    ) -> None:
        self.title_label = QLabel()
        self.title_label.setObjectName("h1")
        self.dirty_label = QLabel()
        self.dirty_label.setObjectName("warning")
        header = QHBoxLayout()
        header.addWidget(self.title_label)
        header.addWidget(self.dirty_label)
        header.addStretch()
        self.tabs = QTabWidget()
        self.close_button = QPushButton("Uždaryti")
        self.cancel_button = QPushButton("Atšaukti")
        self.save_button = QPushButton("Išsaugoti")
        self.save_button.setObjectName("primary")
        self.message_label = QLabel()
        self.close_button.clicked.connect(close)
        self.cancel_button.clicked.connect(restore)
        self.save_button.clicked.connect(save)
        actions = QHBoxLayout()
        actions.addWidget(self.close_button)
        actions.addWidget(self.message_label)
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.save_button)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addLayout(header)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(actions)
        self.success_timer = QTimer(dialog)
        self.success_timer.setSingleShot(True)
        self.success_timer.setInterval(success_timeout_ms)
        self.success_timer.timeout.connect(self.message_label.clear)

    def add_reserved_tab(self, title: str) -> None:
        index = self.tabs.addTab(QWidget(), title)
        self.tabs.setTabEnabled(index, False)


class ConfirmationDialog:
    """Show a safe-default destructive confirmation dialog."""

    @staticmethod
    def ask(
        parent: QWidget,
        *,
        title: str,
        text: str,
        destructive_text: str,
        cancel_text: str = "Atšaukti",
    ) -> bool:
        message = QMessageBox(parent)
        message.setWindowTitle(title)
        message.setText(text)
        cancel = message.addButton(cancel_text, QMessageBox.ButtonRole.RejectRole)
        destructive = message.addButton(
            destructive_text, QMessageBox.ButtonRole.DestructiveRole
        )
        message.setDefaultButton(cancel)
        message.exec()
        return message.clickedButton() is destructive
