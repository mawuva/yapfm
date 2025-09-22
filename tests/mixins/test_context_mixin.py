"""
Unit tests for ContextMixin.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from yapfm.mixins.context_mixin import ContextMixin


class TestContextMixin:
    """Test class for ContextMixin."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create a mock class that uses the mixin
        class MockFileManager(ContextMixin):
            def __init__(self, file_path: Path, auto_create: bool = False) -> None:
                super().__init__()
                self.path = file_path
                self.document: dict[str, Any] = {}
                self.strategy = MagicMock()
                self.auto_create = auto_create
                self._loaded = False
                self._dirty = False

            def exists(self) -> bool:
                return self.path.exists()

            def is_loaded(self) -> bool:
                return self._loaded

            def is_dirty(self) -> bool:
                return self._dirty

            def load(self) -> None:
                self.document = self.strategy.load(self.path)
                self._loaded = True

            def save(self) -> None:
                self.strategy.save(self.path, self.document)
                self._dirty = False

            def save_if_dirty(self) -> None:
                if self.is_dirty():
                    self.save()

            def mark_as_dirty(self) -> None:
                self._dirty = True

            def mark_as_clean(self) -> None:
                self._dirty = False

            def create_empty_file(self) -> None:
                self.document = {}
                self._loaded = True
                self._dirty = True

        self.MockFileManager = MockFileManager

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_context_mixin_enter_file_exists_loaded(self) -> None:
        """
        Scenario: Enter context when file exists and is already loaded

        Expected:
            - Context should enter successfully
            - File should not be reloaded
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True

        with fm as context:
            assert context is fm
            assert fm.is_loaded() is True

    def test_context_mixin_enter_file_exists_not_loaded(self) -> None:
        """
        Scenario: Enter context when file exists but is not loaded

        Expected:
            - File should be loaded
            - Context should enter successfully
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"test": "data"}

        with fm as context:
            assert context is fm
            assert fm.is_loaded() is True
            fm.strategy.load.assert_called_once_with(file_path)

    def test_context_mixin_enter_file_not_exists_no_auto_create(self) -> None:
        """
        Scenario: Enter context when file doesn't exist and auto_create is False

        Expected:
            - FileNotFoundError should be raised
        """
        file_path = self.temp_path / "nonexistent.json"

        fm = self.MockFileManager(file_path, auto_create=False)

        with pytest.raises(FileNotFoundError) as exc_info:
            with fm:
                pass

        assert "File not found" in str(exc_info.value)
        assert str(file_path) in str(exc_info.value)

    def test_context_mixin_enter_file_not_exists_auto_create(self) -> None:
        """
        Scenario: Enter context when file doesn't exist and auto_create is True

        Expected:
            - Empty file should be created
            - Context should enter successfully
        """
        file_path = self.temp_path / "new_file.json"

        fm = self.MockFileManager(file_path, auto_create=True)

        with patch.object(fm, "create_empty_file") as mock_create:
            with fm as context:
                assert context is fm
                mock_create.assert_called_once()

    def test_context_mixin_enter_auto_create_file_exists_empty(self) -> None:
        """
        Scenario: Enter context with auto_create when file exists but is empty

        Expected:
            - Empty document should be created
            - Context should enter successfully
        """
        file_path = self.temp_path / "empty.json"
        file_path.write_text("")

        fm = self.MockFileManager(file_path, auto_create=True)
        fm.strategy.load.side_effect = Exception("Empty file")

        with patch.object(fm, "create_empty_file") as mock_create:
            with fm as context:
                assert context is fm
                mock_create.assert_called_once()

    def test_context_mixin_enter_auto_create_file_exists_valid(self) -> None:
        """
        Scenario: Enter context with auto_create when file exists and is valid

        Expected:
            - File should be loaded normally
            - Context should enter successfully
        """
        file_path = self.temp_path / "valid.json"
        file_path.write_text('{"valid": "data"}')

        fm = self.MockFileManager(file_path, auto_create=True)
        fm.strategy.load.return_value = {"valid": "data"}

        with fm as context:
            assert context is fm
            assert fm.is_loaded() is True
            fm.strategy.load.assert_called_once_with(file_path)

    def test_context_mixin_exit_clean(self) -> None:
        """
        Scenario: Exit context when file is clean

        Expected:
            - save_if_dirty should be called
            - No save should occur
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save_if_dirty") as mock_save_if_dirty:
            with fm:
                pass

        mock_save_if_dirty.assert_called_once()

    def test_context_mixin_exit_dirty(self) -> None:
        """
        Scenario: Exit context when file is dirty

        Expected:
            - save_if_dirty should be called
            - File should be saved
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = True

        with patch.object(fm, "save_if_dirty") as mock_save_if_dirty:
            with fm:
                pass

        mock_save_if_dirty.assert_called_once()

    def test_context_mixin_lazy_save_save_on_exit_true_dirty(self) -> None:
        """
        Scenario: Use lazy_save with save_on_exit=True when file becomes dirty

        Expected:
            - File should be saved on exit
            - Original dirty state should be preserved
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.lazy_save(save_on_exit=True):
                fm._dirty = True

        mock_save.assert_called_once()

    def test_context_mixin_lazy_save_save_on_exit_true_clean(self) -> None:
        """
        Scenario: Use lazy_save with save_on_exit=True when file remains clean

        Expected:
            - No save should occur
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.lazy_save(save_on_exit=True):
                pass

        mock_save.assert_not_called()

    def test_context_mixin_lazy_save_save_on_exit_false_dirty(self) -> None:
        """
        Scenario: Use lazy_save with save_on_exit=False when file becomes dirty

        Expected:
            - No save should occur
            - Original dirty state should be restored
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.lazy_save(save_on_exit=False):
                fm._dirty = True

        mock_save.assert_not_called()
        # The original dirty state (False) should be restored
        assert fm.is_dirty() is False

    def test_context_mixin_lazy_save_save_on_exit_false_clean(self) -> None:
        """
        Scenario: Use lazy_save with save_on_exit=False when file remains clean

        Expected:
            - No save should occur
            - Original clean state should be preserved
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.lazy_save(save_on_exit=False):
                pass

        mock_save.assert_not_called()
        assert fm.is_dirty() is False  # Original state preserved

    def test_context_mixin_lazy_save_exception_handling(self) -> None:
        """
        Scenario: Use lazy_save when an exception occurs

        Expected:
            - Exception should be propagated
            - Save should still occur if dirty
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with pytest.raises(ValueError):
                with fm.lazy_save(save_on_exit=True):
                    fm._dirty = True
                    raise ValueError("Test exception")

        mock_save.assert_called_once()

    def test_context_mixin_auto_save_not_loaded(self) -> None:
        """
        Scenario: Use auto_save when file is not loaded

        Expected:
            - File should be loaded first
            - Context should enter successfully
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"test": "data"}

        def mock_load_side_effect() -> None:
            fm._loaded = True
            fm.document = {"test": "data"}

        with patch.object(fm, "load", side_effect=mock_load_side_effect) as mock_load:
            with fm.auto_save():
                assert fm.is_loaded() is True

        mock_load.assert_called_once()

    def test_context_mixin_auto_save_already_loaded(self) -> None:
        """
        Scenario: Use auto_save when file is already loaded

        Expected:
            - No additional load should occur
            - Context should enter successfully
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True

        with patch.object(fm, "load") as mock_load:
            with fm.auto_save():
                pass

        mock_load.assert_not_called()

    def test_context_mixin_auto_save_save_on_exit_true_dirty(self) -> None:
        """
        Scenario: Use auto_save with save_on_exit=True when file becomes dirty

        Expected:
            - File should be saved on exit
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.auto_save(save_on_exit=True):
                fm._dirty = True

        mock_save.assert_called_once()

    def test_context_mixin_auto_save_save_on_exit_true_clean(self) -> None:
        """
        Scenario: Use auto_save with save_on_exit=True when file remains clean

        Expected:
            - No save should occur
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.auto_save(save_on_exit=True):
                pass

        mock_save.assert_not_called()

    def test_context_mixin_auto_save_save_on_exit_false(self) -> None:
        """
        Scenario: Use auto_save with save_on_exit=False

        Expected:
            - No save should occur regardless of dirty state
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = True

        with patch.object(fm, "save") as mock_save:
            with fm.auto_save(save_on_exit=False):
                pass

        mock_save.assert_not_called()

    def test_context_mixin_auto_save_exception_handling(self) -> None:
        """
        Scenario: Use auto_save when an exception occurs

        Expected:
            - Exception should be propagated
            - Save should still occur if dirty
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with pytest.raises(RuntimeError):
                with fm.auto_save(save_on_exit=True):
                    fm._dirty = True
                    raise RuntimeError("Test exception")

        mock_save.assert_called_once()

    def test_context_mixin_nested_context_managers(self) -> None:
        """
        Scenario: Use nested context managers

        Expected:
            - Both context managers should work correctly
            - State should be managed properly
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            with fm.lazy_save(save_on_exit=True):
                with fm.auto_save(save_on_exit=True):
                    fm._dirty = True

        # Should be called twice (once for each context manager)
        assert mock_save.call_count == 2

    def test_context_mixin_integration_workflow(self) -> None:
        """
        Scenario: Test complete integration workflow

        Expected:
            - All context managers should work together
            - File operations should be consistent
        """
        file_path = self.temp_path / "workflow.json"
        file_path.write_text('{"initial": "data"}')

        fm = self.MockFileManager(file_path, auto_create=True)
        fm.strategy.load.return_value = {"initial": "data"}

        # Test basic context manager
        with fm as context:
            assert context is fm
            assert fm.is_loaded() is True

        # Test lazy_save
        with fm.lazy_save(save_on_exit=True):
            fm._dirty = True
            assert fm.is_dirty() is True

        # Test auto_save
        with fm.auto_save(save_on_exit=True):
            fm._dirty = True
            assert fm.is_dirty() is True

        # Verify file operations were called
        fm.strategy.load.assert_called()
        fm.strategy.save.assert_called()

    def test_context_mixin_error_recovery(self) -> None:
        """
        Scenario: Test error recovery in context managers

        Expected:
            - Context managers should handle errors gracefully
            - State should be restored properly
        """
        file_path = self.temp_path / "error.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        # Test lazy_save error recovery
        with patch.object(fm, "save") as mock_save:
            try:
                with fm.lazy_save(save_on_exit=True):
                    fm._dirty = True
                    raise ValueError("Test error")
            except ValueError:
                pass

        mock_save.assert_called_once()

        # Test auto_save error recovery
        with patch.object(fm, "save") as mock_save:
            try:
                with fm.auto_save(save_on_exit=True):
                    fm._dirty = True
                    raise RuntimeError("Test error")
            except RuntimeError:
                pass

        mock_save.assert_called_once()
