"""Tests for the AppState class."""

import pytest
from app.core import AppState


class TestAppStateInitialization:
    """Tests for AppState initialization."""

    def test_new_app_state_is_not_running(self):
        """Test that a new AppState is not running."""
        state = AppState()
        assert state.is_running is False

    def test_new_app_state_has_no_current_user(self):
        """Test that a new AppState has no active user."""
        state = AppState()
        assert state.current_user_id is None

    def test_new_app_state_has_no_active_document(self):
        """Test that a new AppState has no active document."""
        state = AppState()
        assert state.active_document_id is None

    def test_new_app_state_has_no_unsaved_changes(self):
        """Test that a new AppState has no unsaved changes."""
        state = AppState()
        assert state.has_unsaved_changes is False


class TestApplicationRunningState:
    """Tests for application running state management."""

    def test_start_sets_running_state(self):
        """Test that start() sets the running state to True."""
        state = AppState()
        state.start()
        assert state.is_running is True

    def test_start_is_idempotent(self):
        """Test that calling start() multiple times has no adverse effects."""
        state = AppState()
        state.start()
        state.start()
        state.start()
        assert state.is_running is True

    def test_stop_clears_running_state(self):
        """Test that stop() sets the running state to False."""
        state = AppState()
        state.start()
        state.stop()
        assert state.is_running is False

    def test_stop_clears_active_document(self):
        """Test that stop() clears the active document."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.stop()
        assert state.active_document_id is None

    def test_stop_clears_unsaved_changes(self):
        """Test that stop() clears the unsaved changes flag."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.stop()
        assert state.has_unsaved_changes is False

    def test_stop_preserves_current_user(self):
        """Test that stop() preserves the current user."""
        state = AppState()
        state.set_current_user("user1")
        state.start()
        state.stop()
        assert state.current_user_id == "user1"

    def test_stop_is_idempotent(self):
        """Test that calling stop() multiple times has no adverse effects."""
        state = AppState()
        state.start()
        state.stop()
        state.stop()
        state.stop()
        assert state.is_running is False


class TestCurrentUserManagement:
    """Tests for current user state management."""

    def test_set_current_user(self):
        """Test that a user ID can be set as the current user."""
        state = AppState()
        state.set_current_user("user123")
        assert state.current_user_id == "user123"

    def test_set_current_user_preserves_value(self):
        """Test that the user value is stored as provided without modification."""
        state = AppState()
        user_id = "User_ID_123"
        state.set_current_user(user_id)
        assert state.current_user_id == user_id

    def test_set_current_user_empty_string_raises_value_error(self):
        """Test that an empty user_id raises ValueError."""
        state = AppState()
        with pytest.raises(ValueError):
            state.set_current_user("")

    def test_set_current_user_whitespace_only_raises_value_error(self):
        """Test that a user_id with only whitespace raises ValueError."""
        state = AppState()
        with pytest.raises(ValueError):
            state.set_current_user("   ")

    def test_set_current_user_invalid_type_raises_type_error(self):
        """Test that a non-string user_id raises TypeError."""
        state = AppState()
        with pytest.raises(TypeError):
            state.set_current_user(123)  # type: ignore

    def test_clear_current_user(self):
        """Test that the current user can be cleared."""
        state = AppState()
        state.set_current_user("user1")
        state.clear_current_user()
        assert state.current_user_id is None

    def test_clear_current_user_clears_active_document(self):
        """Test that clearing the user also clears the active document."""
        state = AppState()
        state.set_current_user("user1")
        state.start()
        state.set_active_document("doc1")
        state.clear_current_user()
        assert state.active_document_id is None

    def test_clear_current_user_clears_unsaved_changes(self):
        """Test that clearing the user also clears unsaved changes."""
        state = AppState()
        state.set_current_user("user1")
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.clear_current_user()
        assert state.has_unsaved_changes is False


class TestActiveDocumentManagement:
    """Tests for active document state management."""

    def test_cannot_set_active_document_when_not_running(self):
        """Test that setting active document when app is not running raises RuntimeError."""
        state = AppState()
        with pytest.raises(RuntimeError):
            state.set_active_document("doc1")

    def test_can_set_active_document_when_running(self):
        """Test that an active document can be set when the app is running."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        assert state.active_document_id == "doc1"

    def test_set_active_document_preserves_value(self):
        """Test that the document value is stored as provided without modification."""
        state = AppState()
        state.start()
        doc_id = "Doc_ID_123"
        state.set_active_document(doc_id)
        assert state.active_document_id == doc_id

    def test_set_active_document_empty_string_raises_value_error(self):
        """Test that an empty document_id raises ValueError."""
        state = AppState()
        state.start()
        with pytest.raises(ValueError):
            state.set_active_document("")

    def test_set_active_document_whitespace_only_raises_value_error(self):
        """Test that a document_id with only whitespace raises ValueError."""
        state = AppState()
        state.start()
        with pytest.raises(ValueError):
            state.set_active_document("   ")

    def test_set_active_document_invalid_type_raises_type_error(self):
        """Test that a non-string document_id raises TypeError."""
        state = AppState()
        state.start()
        with pytest.raises(TypeError):
            state.set_active_document(456)  # type: ignore

    def test_set_active_document_clears_unsaved_changes(self):
        """Test that setting a new document clears the unsaved changes flag."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.set_active_document("doc2")
        assert state.has_unsaved_changes is False

    def test_clear_active_document(self):
        """Test that the active document can be cleared."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.clear_active_document()
        assert state.active_document_id is None

    def test_clear_active_document_clears_unsaved_changes(self):
        """Test that clearing the document also clears unsaved changes."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.clear_active_document()
        assert state.has_unsaved_changes is False

    def test_clear_active_document_is_idempotent(self):
        """Test that clear_active_document() can be called multiple times."""
        state = AppState()
        state.clear_active_document()
        state.clear_active_document()
        state.clear_active_document()
        assert state.active_document_id is None


class TestUnsavedChangesManagement:
    """Tests for unsaved changes state management."""

    def test_mark_unsaved_changes(self):
        """Test that unsaved changes can be marked."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        assert state.has_unsaved_changes is True

    def test_mark_unsaved_changes_without_active_document_raises_runtime_error(self):
        """Test that marking changes without active document raises RuntimeError."""
        state = AppState()
        with pytest.raises(RuntimeError):
            state.mark_unsaved_changes()

    def test_mark_unsaved_changes_is_idempotent(self):
        """Test that calling mark_unsaved_changes() multiple times has no adverse effects."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.mark_unsaved_changes()
        state.mark_unsaved_changes()
        assert state.has_unsaved_changes is True

    def test_mark_changes_saved(self):
        """Test that unsaved changes can be cleared."""
        state = AppState()
        state.start()
        state.set_active_document("doc1")
        state.mark_unsaved_changes()
        state.mark_changes_saved()
        assert state.has_unsaved_changes is False

    def test_mark_changes_saved_without_active_document_no_error(self):
        """Test that mark_changes_saved() without active document doesn't raise error."""
        state = AppState()
        state.mark_changes_saved()
        assert state.has_unsaved_changes is False

    def test_mark_changes_saved_is_idempotent(self):
        """Test that calling mark_changes_saved() multiple times has no adverse effects."""
        state = AppState()
        state.mark_changes_saved()
        state.mark_changes_saved()
        state.mark_changes_saved()
        assert state.has_unsaved_changes is False


class TestReset:
    """Tests for the reset() method."""

    def test_reset_restores_initial_state(self):
        """Test that reset() restores all attributes to their initial state."""
        state = AppState()
        state.start()
        state.set_current_user("user1")
        state.set_active_document("doc1")
        state.mark_unsaved_changes()

        state.reset()

        assert state.is_running is False
        assert state.current_user_id is None
        assert state.active_document_id is None
        assert state.has_unsaved_changes is False

    def test_reset_is_idempotent(self):
        """Test that reset() can be called multiple times."""
        state = AppState()
        state.reset()
        state.reset()
        state.reset()
        assert state.is_running is False


class TestReadOnlyProperties:
    """Tests for read-only properties."""

    def test_is_running_is_read_only(self):
        """Test that is_running property is read-only."""
        state = AppState()
        with pytest.raises(AttributeError):
            state.is_running = True  # type: ignore

    def test_current_user_id_is_read_only(self):
        """Test that current_user_id property is read-only."""
        state = AppState()
        with pytest.raises(AttributeError):
            state.current_user_id = "user1"  # type: ignore

    def test_active_document_id_is_read_only(self):
        """Test that active_document_id property is read-only."""
        state = AppState()
        with pytest.raises(AttributeError):
            state.active_document_id = "doc1"  # type: ignore

    def test_has_unsaved_changes_is_read_only(self):
        """Test that has_unsaved_changes property is read-only."""
        state = AppState()
        with pytest.raises(AttributeError):
            state.has_unsaved_changes = True  # type: ignore


class TestImport:
    """Tests for AppState import."""

    def test_app_state_can_be_imported_from_app_core(self):
        """Test that AppState can be imported from app.core."""
        from app.core import AppState  # noqa: F401
        assert AppState is not None
