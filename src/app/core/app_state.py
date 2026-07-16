"""Application state management.

This module provides a minimal general application state object that tracks
the core execution state of the application, including running status, current
user, active document, and unsaved changes.
"""


class AppState:
    """Manages the core application state.

    This class is responsible for tracking and managing the general execution
    state of the application. It maintains information about:
    - Whether the application is currently running
    - The currently active user
    - The currently active document
    - Whether there are unsaved changes to the active document

    This class is designed to be:
    - Non-abstract and concrete
    - Not a singleton
    - Independent of any GUI framework
    - Free of dependencies on controllers, services, models, EventBus, or ServiceContainer
    """

    def __init__(self) -> None:
        """Initialize a new AppState instance with default values."""
        self._is_running: bool = False
        self._current_user_id: str | None = None
        self._active_document_id: str | None = None
        self._has_unsaved_changes: bool = False

    @property
    def is_running(self) -> bool:
        """Return whether the application is currently running."""
        return self._is_running

    @property
    def current_user_id(self) -> str | None:
        """Return the ID of the currently active user, or None if no user is active."""
        return self._current_user_id

    @property
    def active_document_id(self) -> str | None:
        """Return the ID of the currently active document, or None if no document is active."""
        return self._active_document_id

    @property
    def has_unsaved_changes(self) -> bool:
        """Return whether the active document has unsaved changes."""
        return self._has_unsaved_changes

    def start(self) -> None:
        """Start the application.

        Sets the running state to True. This method is idempotent and calling
        it multiple times has no adverse effects.
        """
        self._is_running = True

    def stop(self) -> None:
        """Stop the application.

        Sets the running state to False and clears the active document state
        and unsaved changes flag. The current user state is preserved.
        This method is idempotent.
        """
        self._is_running = False
        self._active_document_id = None
        self._has_unsaved_changes = False

    def set_current_user(self, user_id: str) -> None:
        """Set the current active user.

        Args:
            user_id: The ID of the user to set as active.

        Raises:
            TypeError: If user_id is not a string.
            ValueError: If user_id is empty or contains only whitespace.
        """
        if not isinstance(user_id, str):
            raise TypeError(f"user_id must be a string, got {type(user_id).__name__}")

        if not user_id.strip():
            raise ValueError("user_id cannot be empty or contain only whitespace")

        self._current_user_id = user_id

    def clear_current_user(self) -> None:
        """Clear the current active user.

        Also clears the active document and unsaved changes state.
        This method is idempotent.
        """
        self._current_user_id = None
        self._active_document_id = None
        self._has_unsaved_changes = False

    def set_active_document(self, document_id: str) -> None:
        """Set the active document.

        The application must be running to set an active document.

        Args:
            document_id: The ID of the document to set as active.

        Raises:
            RuntimeError: If the application is not running.
            TypeError: If document_id is not a string.
            ValueError: If document_id is empty or contains only whitespace.
        """
        if not self._is_running:
            raise RuntimeError("Cannot set active document: application is not running")

        if not isinstance(document_id, str):
            raise TypeError(f"document_id must be a string, got {type(document_id).__name__}")

        if not document_id.strip():
            raise ValueError("document_id cannot be empty or contain only whitespace")

        self._active_document_id = document_id
        self._has_unsaved_changes = False

    def clear_active_document(self) -> None:
        """Clear the active document.

        Clears both the active document and the unsaved changes flag.
        This method is idempotent and does not raise an error if no document
        is currently active.
        """
        self._active_document_id = None
        self._has_unsaved_changes = False

    def mark_unsaved_changes(self) -> None:
        """Mark the active document as having unsaved changes.

        The active document must exist to mark changes as unsaved.

        Raises:
            RuntimeError: If no document is currently active.
        """
        if self._active_document_id is None:
            raise RuntimeError("Cannot mark unsaved changes: no active document")

        self._has_unsaved_changes = True

    def mark_changes_saved(self) -> None:
        """Mark the active document as having no unsaved changes.

        This method is idempotent and does not raise an error if no document
        is currently active.
        """
        self._has_unsaved_changes = False

    def reset(self) -> None:
        """Reset the application state to its initial state.

        Restores all attributes to their default values. This method does not
        create a new AppState object. This method is idempotent.
        """
        self._is_running = False
        self._current_user_id = None
        self._active_document_id = None
        self._has_unsaved_changes = False
