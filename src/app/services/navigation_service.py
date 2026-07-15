"""Simple navigation service for switching the active controller."""

from __future__ import annotations

from app.controllers.base_controller import BaseController


class NavigationService:
    """Manage the currently active controller with simple lifecycle transitions."""

    def __init__(self) -> None:
        """Initialize the service without an active controller."""
        self._current_controller: BaseController | None = None

    @property
    def current_controller(self) -> BaseController | None:
        """Return the currently active controller or None."""
        return self._current_controller

    @property
    def has_active_controller(self) -> bool:
        """Return whether there is an active controller."""
        return self._current_controller is not None

    def navigate_to(self, controller: BaseController) -> None:
        """Switch to another controller by stopping the current one and starting the new one."""
        if not isinstance(controller, BaseController):
            raise TypeError("controller must be an instance of BaseController")

        if self._current_controller is controller:
            return

        previous_controller = self._current_controller
        if previous_controller is not None:
            previous_controller.stop()

        try:
            controller.start()
        except Exception:
            self._current_controller = None
            raise

        self._current_controller = controller

    def close_current(self) -> None:
        """Stop the active controller and clear the current controller reference."""
        if self._current_controller is None:
            return

        controller = self._current_controller
        controller.stop()
        self._current_controller = None
