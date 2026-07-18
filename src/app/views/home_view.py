"""Minimal home page with real available actions."""

from collections.abc import Callable

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class HomeView(QWidget):
    """Present the application start page without fabricated metrics."""

    def __init__(self) -> None:
        super().__init__()
        title = QLabel("PTH Fausta")
        title.setObjectName("h1")
        description = QLabel("Lietuviška dokumentų valdymo sistema")
        description.setObjectName("secondary")
        self.company_button = QPushButton("Įmonės rekvizitai")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(16)
        layout.addWidget(self.company_button)
        layout.addStretch()

    def on_open_company(self, callback: Callable[[], None]) -> None:
        self.company_button.clicked.connect(callback)

    def set_company_exists(self, exists: bool) -> None:
        """Only offer company setup while no company profile exists."""
        self.company_button.setVisible(not exists)
