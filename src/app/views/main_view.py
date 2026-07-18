"""Main application shell with accessible sidebar navigation."""

from collections.abc import Callable

from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout,
    QWidget,
)

from app.core.version import APP_VERSION
from app.views.base_view import BaseView
from app.views.home_view import HomeView

SIDEBAR_EXPANDED_WIDTH = 273
SIDEBAR_COLLAPSED_WIDTH = 64


class MainView(BaseView):
    """Display the application header, navigation, workspace and status."""

    def __init__(self, title: str = "PTH Fausta") -> None:
        self._window = QMainWindow()
        self._window.setMinimumSize(860, 600)
        self._sidebar_collapsed = False
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        header = QLabel("PTH Fausta")
        header.setObjectName("h2")
        header.setContentsMargins(24, 14, 24, 14)
        root_layout.addWidget(header)
        body = QHBoxLayout()
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED_WIDTH)
        self._sidebar_layout = QVBoxLayout(self.sidebar)
        self.collapse_button = QPushButton("☰  Suskleisti")
        self.collapse_button.setToolTip("Suskleisti navigaciją")
        self.collapse_button.setAccessibleName("Suskleisti navigaciją")
        self.collapse_button.clicked.connect(self.toggle_sidebar)
        self._sidebar_layout.addWidget(self.collapse_button)
        self.home_button = self._nav_button("⌂", "Pradžia", True)
        self.company_button = self._nav_button("⚙", "Įmonė")
        self.home_button.clicked.connect(lambda: self.set_active_navigation("home"))
        self.company_button.clicked.connect(
            lambda: self.set_active_navigation("company")
        )
        self._sidebar_layout.addWidget(self.home_button)
        self._sidebar_layout.addStretch()
        self._sidebar_layout.addWidget(self.company_button)
        self.workspace = QStackedWidget()
        self.home_view = HomeView()
        self.workspace.addWidget(self.home_view)
        body.addWidget(self.sidebar)
        body.addWidget(self.workspace, 1)
        root_layout.addLayout(body, 1)
        status = QLabel(f"Duomenų bazė: prijungta  |  PTH Fausta {APP_VERSION}")
        status.setObjectName("secondary")
        status.setContentsMargins(16, 6, 16, 6)
        self.status_label = status
        root_layout.addWidget(status)
        self._window.setCentralWidget(root)
        self.set_title(title)

    def _nav_button(self, icon: str, text: str, checked: bool = False) -> QPushButton:
        button = QPushButton(f"{icon}  {text}")
        button.setObjectName("nav")
        button.setCheckable(True)
        button.setChecked(checked)
        button.setToolTip(text)
        button.setAccessibleName(text)
        button.setProperty("iconText", icon)
        button.setProperty("fullText", f"{icon}  {text}")
        return button

    def on_open_company(self, callback: Callable[[], None]) -> None:
        self.company_button.clicked.connect(callback)
        self.home_view.on_open_company(callback)

    def set_company_exists(self, exists: bool) -> None:
        """Update actions whose availability depends on a company profile."""
        if hasattr(self, "home_view"):
            self.home_view.set_company_exists(exists)

    def set_active_navigation(self, name: str) -> None:
        self.home_button.setChecked(name == "home")
        self.company_button.setChecked(name == "company")

    def toggle_sidebar(self) -> None:
        self._sidebar_collapsed = not self._sidebar_collapsed
        self.sidebar.setFixedWidth(
            SIDEBAR_COLLAPSED_WIDTH
            if self._sidebar_collapsed
            else SIDEBAR_EXPANDED_WIDTH
        )
        for button in (self.home_button, self.company_button):
            text = (
                button.property("iconText")
                if self._sidebar_collapsed
                else button.property("fullText")
            )
            button.setText(text)
        self.collapse_button.setText(
            "☰" if self._sidebar_collapsed else "☰  Suskleisti"
        )

    def set_title(self, title: str) -> None:
        self._window.setWindowTitle(title)

    def window_title(self) -> str:
        return self._window.windowTitle()

    def is_visible(self) -> bool:
        return self._window.isVisible()

    def show(self) -> None:
        self._window.show()

    def close(self) -> None:
        self._window.close()
