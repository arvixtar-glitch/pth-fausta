"""Qt event loop adapter."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication


class QtEventLoop:
    """Adapt an existing QApplication to the core event loop port."""

    def __init__(self, application: QApplication) -> None:
        """Store the existing Qt application instance."""
        self._application = application

    def run(self) -> int:
        """Run the Qt event loop and return its exit code."""
        return self._application.exec()

    def quit(self) -> None:
        """Request that the Qt event loop stop."""
        self._application.quit()


__all__ = ["QtEventLoop"]
