"""High-level application controller for managing a view lifecycle."""

from __future__ import annotations

from app.controllers.base_controller import BaseController
from app.views.base_view import BaseView


class AppController(BaseController):
    """Coordinate a view lifecycle without coupling to concrete UI code."""

    def __init__(self, view: BaseView) -> None:
        """Initialize the controller with a view and a stopped state."""
        super().__init__(view)
        self._is_running: bool = False

    @property
    def is_running(self) -> bool:
        """Return whether the controller is currently running."""
        return self._is_running

    def start(self) -> None:
        """Show the view once if the controller is not already running."""
        if self._is_running:
            return

        self.view.show()
        self._is_running = True

    def stop(self) -> None:
        """Close the view once if the controller is currently running."""
        if not self._is_running:
            return

        super().stop()
        self._is_running = False
