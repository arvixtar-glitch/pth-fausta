"""Main application window view."""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from app.views.base_view import BaseView


class MainView(BaseView):
    """Minimal main application window."""

    def __init__(self, title: str = "PTH Fausta") -> None:
        self._window = QMainWindow()

        central_widget = QWidget(self._window)
        central_widget.setLayout(QVBoxLayout())
        self._window.setCentralWidget(central_widget)
        self.set_title(title)

    def set_title(self, title: str) -> None:
        """Set the application window title."""
        self._window.setWindowTitle(title)

    def window_title(self) -> str:
        """Return the application window title."""
        return self._window.windowTitle()

    def is_visible(self) -> bool:
        """Return whether the application window is visible."""
        return self._window.isVisible()

    def show(self) -> None:
        """Show the application window."""
        self._window.show()

    def close(self) -> None:
        """Close the application window."""
        self._window.close()
