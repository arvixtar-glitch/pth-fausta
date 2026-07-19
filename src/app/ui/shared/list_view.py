"""Reusable list-workspace widgets for CRUD modules."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.views.base_view import BaseView

FilterOption = tuple[str, object]
FilterSpec = tuple[str, Sequence[FilterOption]]
ActionSpec = tuple[str, str, str | None]


class SortableHeader(QHeaderView):
    """Make table sorting accessible with Left/Right and Enter/Space."""

    def __init__(self) -> None:
        super().__init__(Qt.Orientation.Horizontal)
        self._keyboard_section = 0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self._keyboard_section = max(0, self._keyboard_section - 1)
            return
        if event.key() == Qt.Key.Key_Right:
            self._keyboard_section = min(self.count() - 1, self._keyboard_section + 1)
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.sectionClicked.emit(self._keyboard_section)
            return
        super().keyPressEvent(event)


class ActionTable(QTableWidget):
    """Standard single-select table with keyboard edit/delete actions."""

    def __init__(self, columns: int, headers: Sequence[str]) -> None:
        super().__init__(0, columns)
        self.on_activate: Callable[[], None] | None = None
        self.on_delete: Callable[[], None] | None = None
        self.setHorizontalHeader(SortableHeader())
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.on_activate:
            self.on_activate()
            return
        if event.key() == Qt.Key.Key_Delete and self.on_delete:
            self.on_delete()
            return
        super().keyPressEvent(event)


class CrudToolbar(QWidget):
    """Render named CRUD actions in a consistent horizontal row."""

    def __init__(self, actions: Sequence[ActionSpec]) -> None:
        super().__init__()
        self.buttons: dict[str, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for key, label, object_name in actions:
            button = QPushButton(label)
            if object_name:
                button.setObjectName(object_name)
            self.buttons[key] = button
            layout.addWidget(button)


class FilterBar(QWidget):
    """Combine an instant search input with controlled combo-box filters."""

    def __init__(self, placeholder: str, filters: Sequence[FilterSpec]) -> None:
        super().__init__()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.filters: dict[str, QComboBox] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_input, 1)
        for key, options in filters:
            combo = QComboBox()
            for label, value in options:
                combo.addItem(label, value)
            self.filters[key] = combo
            layout.addWidget(combo)

    def set_controls_enabled(self, enabled: bool) -> None:
        self.search_input.setEnabled(enabled)
        for combo in self.filters.values():
            combo.setEnabled(enabled)


class EmptyStateWidget(QWidget):
    """Display empty/no-results messages with an optional primary action."""

    def __init__(self, action_text: str, icon: str = "○") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()
        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("h1")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label = QLabel()
        self.description_label.setObjectName("secondary")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_button = QPushButton(action_text)
        self.action_button.setObjectName("primary")
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.description_label)
        layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def display(self, message: str, description: str, show_action: bool) -> None:
        self.message_label.setText(message)
        self.description_label.setText(description)
        self.action_button.setVisible(show_action)


class LoadingStateWidget(QWidget):
    """Display one consistent indeterminate loading state."""

    def __init__(self, message: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.indicator = QProgressBar()
        self.indicator.setRange(0, 0)
        layout.addWidget(label)
        layout.addWidget(self.indicator)
        layout.addStretch()


class StatusBarWidget(QWidget):
    """Display the current visible record count."""

    def __init__(self, initial_text: str) -> None:
        super().__init__()
        self.count_label = QLabel(initial_text)
        self.count_label.setObjectName("secondary")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.count_label)


class BaseListView(BaseView):
    """Provide the shared visual shell and states for module list views."""

    def __init__(
        self,
        *,
        title: str,
        description: str,
        table: ActionTable,
        actions: Sequence[ActionSpec],
        search_placeholder: str,
        filters: Sequence[FilterSpec],
        loading_text: str,
        first_action_text: str,
        initial_count_text: str,
    ) -> None:
        self._widget = QWidget()
        self.table = table
        self.toolbar = CrudToolbar(actions)
        self.filter_bar = FilterBar(search_placeholder, filters)
        self.search_input = self.filter_bar.search_input
        self.filters = self.filter_bar.filters
        self.content = QStackedWidget()
        self.content.addWidget(self.table)
        self.loading_page = LoadingStateWidget(loading_text)
        self.loading_indicator = self.loading_page.indicator
        self.content.addWidget(self.loading_page)
        self.empty_page = EmptyStateWidget(first_action_text)
        self.empty_icon = self.empty_page.icon_label
        self.empty_label = self.empty_page.message_label
        self.empty_description = self.empty_page.description_label
        self.first_action_button = self.empty_page.action_button
        self.content.addWidget(self.empty_page)
        self.status_bar = StatusBarWidget(initial_count_text)
        self.count_label = self.status_bar.count_label
        self._build_shell(title, description)

    def _build_shell(self, title_text: str, description_text: str) -> None:
        title = QLabel(title_text)
        title.setObjectName("h1")
        description = QLabel(description_text)
        description.setObjectName("secondary")
        heading_text = QVBoxLayout()
        heading_text.addWidget(title)
        heading_text.addWidget(description)
        heading = QHBoxLayout()
        heading.addLayout(heading_text)
        heading.addStretch()
        heading.addWidget(self.toolbar)
        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(16)
        layout.addLayout(heading)
        layout.addWidget(self.filter_bar)
        layout.addWidget(self.content, 1)
        layout.addWidget(self.status_bar)

    @property
    def widget(self) -> QWidget:
        return self._widget

    def set_loading(self, loading: bool) -> None:
        if loading:
            self.content.setCurrentWidget(self.loading_page)
            self.filter_bar.set_controls_enabled(False)
            for button in self.toolbar.buttons.values():
                button.setEnabled(False)
        elif self.content.currentWidget() is self.loading_page:
            self.content.setCurrentWidget(self.table)

    def display_state(
        self,
        *,
        visible_count: int,
        total_count: int,
        empty_message: str,
        empty_description: str,
        no_results_message: str,
        no_results_description: str,
    ) -> None:
        if visible_count:
            self.content.setCurrentWidget(self.table)
        else:
            is_empty = total_count == 0
            self.empty_page.display(
                empty_message if is_empty else no_results_message,
                empty_description if is_empty else no_results_description,
                is_empty,
            )
            self.content.setCurrentWidget(self.empty_page)
        self.filter_bar.set_controls_enabled(total_count > 0)

    def show(self) -> None:
        self._widget.show()

    def close(self) -> None:
        self._widget.hide()
