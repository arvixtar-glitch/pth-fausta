"""Reusable labelled form fields."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def form_field(label: str, editor: QWidget, required: bool = False) -> QWidget:
    """Build a vertically labelled form field."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    caption = QLabel(f"{label}{' *' if required else ''}")
    layout.addWidget(caption)
    layout.addWidget(editor)
    return container
