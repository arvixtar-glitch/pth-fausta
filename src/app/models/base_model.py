"""Base model definitions for the application."""

from __future__ import annotations


class BaseModel:
    """Provide simple dirty-state tracking for application models."""

    def __init__(self) -> None:
        """Initialize the model with a clean state."""
        self._is_dirty: bool = False

    @property
    def is_dirty(self) -> bool:
        """Return whether the model has unsaved changes."""
        return self._is_dirty

    def mark_dirty(self) -> None:
        """Mark the model as having unsaved changes."""
        self._is_dirty = True

    def mark_clean(self) -> None:
        """Mark the model as clean."""
        self._is_dirty = False
