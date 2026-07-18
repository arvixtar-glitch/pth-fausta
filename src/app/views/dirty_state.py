"""Shared dirty-state primitives for card-style dialogs."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog


class DirtyStateTracker:
    """Compare current form values with the last persisted snapshot."""

    def __init__(self) -> None:
        self._snapshot: dict[str, str] = {}

    @property
    def snapshot(self) -> dict[str, str]:
        return dict(self._snapshot)

    def capture(self, values: Mapping[str, str]) -> None:
        self._snapshot = dict(values)

    def is_dirty(self, values: Mapping[str, str]) -> bool:
        return dict(values) != self._snapshot


class GuardedDialog(QDialog):
    """Route window-manager and Esc close attempts through one callback."""

    def __init__(self) -> None:
        super().__init__()
        self._close_callback: Callable[[], None] | None = None
        self._force_closing = False

    def guard_close_with(self, callback: Callable[[], None]) -> None:
        self._close_callback = callback

    def force_close(self) -> None:
        self._force_closing = True
        self.close()
        self._force_closing = False

    def reject(self) -> None:
        if self._force_closing or self._close_callback is None:
            super().reject()
            return
        self._close_callback()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._force_closing or self._close_callback is None:
            event.accept()
            return
        event.ignore()
        self._close_callback()
