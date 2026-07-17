"""Lifecycle ports used by the core application."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class ApplicationStatePort(Protocol):
    """Define application state lifecycle operations."""

    def start(self) -> None:
        """Mark the application state as running."""

    def stop(self) -> None:
        """Mark the application state as stopped."""


@runtime_checkable
class ControllerPort(Protocol):
    """Define controller lifecycle operations."""

    def start(self) -> None:
        """Start the controller."""

    def stop(self) -> None:
        """Stop the controller."""


class NavigationPort(Protocol):
    """Define operations for activating and closing controllers."""

    def navigate_to(self, controller: ControllerPort) -> None:
        """Activate the provided controller."""

    def close_current(self) -> None:
        """Close the active controller, if one exists."""


class EventLoopPort(Protocol):
    """Define event loop lifecycle operations."""

    def run(self) -> int:
        """Run the event loop and return its exit code."""

    def quit(self) -> None:
        """Request that the event loop stop."""


__all__ = [
    "ApplicationStatePort",
    "ControllerPort",
    "EventLoopPort",
    "NavigationPort",
]
