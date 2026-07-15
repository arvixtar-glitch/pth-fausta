"""Base view abstractions for the application."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseView(ABC):
    """Define the interface for application views."""

    @abstractmethod
    def show(self) -> None:
        """Display the view to the user."""

    @abstractmethod
    def close(self) -> None:
        """Close or hide the view."""
