"""Base controller abstractions for the application."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.views.base_view import BaseView


class BaseController(ABC):
    """Define the interface for controller classes."""

    def __init__(self, view: BaseView) -> None:
        """Store the view used by the controller."""
        self._view: BaseView = view

    @property
    def view(self) -> BaseView:
        """Return the associated view."""
        return self._view

    @abstractmethod
    def start(self) -> None:
        """Start the controller's workflow."""

    def stop(self) -> None:
        """Stop the controller and close its view."""
        self._view.close()
