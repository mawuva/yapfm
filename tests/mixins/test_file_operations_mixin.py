"""
Unit tests for FileOperationsMixin.
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from yapfm.exceptions import FileWriteError, LoadFileError
from yapfm.mixins.file_operations_mixin import FileOperationsMixin


class TestFileOperationsMixin:
    """Test class for FileOperationsMixin."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create a mock class that uses the mixin
        class MockFileManager(FileOperationsMixin):
            def __init__(self, file_path: Path) -> None:
                super().__init__()
                self.path = file_path
                self.document: dict[str, Any] = {}
                self.strategy = MagicMock()

        self.MockFileManager = MockFileManager

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_operations_mixin_init(self) -> None:
        """
        Scenario: Initialize FileOperationsMixin

        Expected:
            - _loaded should be False
            - _dirty should be False
        """
        mixin = FileOperationsMixin()

        assert mixin._loaded is False
        assert mixin._dirty is False

    def test_file_operations_mixin_exists_true(self) -> None:
        """
        Scenario: Check if file exists when it does exist

        Expected:
            - exists() should return True
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)

        assert fm.exists() is True

    def test_file_operations_mixin_exists_false(self) -> None:
        """
        Scenario: Check if file exists when it doesn't exist

        Expected:
            - exists() should return False
        """
        file_path = self.temp_path / "nonexistent.json"

        fm = self.MockFileManager(file_path)

        assert fm.exists() is False

    def test_file_operations_mixin_is_dirty_false(self) -> None:
        """
        Scenario: Check dirty state when file is clean

        Expected:
            - is_dirty() should return False
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)

        assert fm.is_dirty() is False

    def test_file_operations_mixin_is_dirty_true(self) -> None:
        """
        Scenario: Check dirty state when file is marked as dirty

        Expected:
            - is_dirty() should return True
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm.mark_as_dirty()

        assert fm.is_dirty() is True

    def test_file_operations_mixin_is_loaded_false(self) -> None:
        """
        Scenario: Check loaded state when file is not loaded

        Expected:
            - is_loaded() should return False
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)

        assert fm.is_loaded() is False

    def test_file_operations_mixin_is_loaded_true(self) -> None:
        """
        Scenario: Check loaded state when file is loaded

        Expected:
            - is_loaded() should return True
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True

        assert fm.is_loaded() is True

    def test_file_operations_mixin_load_file_exists(self) -> None:
        """
        Scenario: Load file when it exists

        Expected:
            - Document should be loaded from strategy
            - _loaded should be True
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"test": "data"}

        fm.load()

        assert fm.document == {"test": "data"}
        assert fm.is_loaded() is True
        fm.strategy.load.assert_called_once_with(file_path)

    def test_file_operations_mixin_load_file_not_exists(self) -> None:
        """
        Scenario: Load file when it doesn't exist

        Expected:
            - Document should be empty dict
            - _loaded should be True
        """
        file_path = self.temp_path / "nonexistent.json"

        fm = self.MockFileManager(file_path)

        fm.load()

        assert fm.document == {}
        assert fm.is_loaded() is True
        fm.strategy.load.assert_not_called()

    def test_file_operations_mixin_load_strategy_error(self) -> None:
        """
        Scenario: Load file when strategy raises an exception

        Expected:
            - LoadFileError should be raised
            - Error message should contain file path
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.side_effect = Exception("Parse error")

        with pytest.raises(LoadFileError) as exc_info:
            fm.load()

        assert "Failed to load file" in str(exc_info.value)
        assert str(file_path) in str(exc_info.value)

    def test_file_operations_mixin_save_success(self) -> None:
        """
        Scenario: Save file successfully

        Expected:
            - Strategy save should be called
            - _dirty should be False
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm.document = {"test": "data"}
        fm._dirty = True

        fm.save()

        fm.strategy.save.assert_called_once_with(file_path, {"test": "data"})
        assert fm.is_dirty() is False

    def test_file_operations_mixin_save_not_loaded(self) -> None:
        """
        Scenario: Save file when not loaded

        Expected:
            - FileWriteError should be raised
            - Error message should indicate no data to save
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = False

        with pytest.raises(FileWriteError) as exc_info:
            fm.save()

        assert "No data to save" in str(exc_info.value)
        assert str(file_path) in str(exc_info.value)

    def test_file_operations_mixin_save_strategy_error(self) -> None:
        """
        Scenario: Save file when strategy raises an exception

        Expected:
            - FileWriteError should be raised
            - Error message should contain file path
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm.document = {"test": "data"}
        fm.strategy.save.side_effect = Exception("Write error")

        with pytest.raises(FileWriteError) as exc_info:
            fm.save()

        assert "Failed to save file" in str(exc_info.value)
        assert str(file_path) in str(exc_info.value)

    def test_file_operations_mixin_save_if_dirty_true(self) -> None:
        """
        Scenario: Save if dirty when file is dirty

        Expected:
            - Save should be called
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = True

        with patch.object(fm, "save") as mock_save:
            fm.save_if_dirty()
            mock_save.assert_called_once()

    def test_file_operations_mixin_save_if_dirty_false(self) -> None:
        """
        Scenario: Save if dirty when file is not dirty

        Expected:
            - Save should not be called
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = False

        with patch.object(fm, "save") as mock_save:
            fm.save_if_dirty()
            mock_save.assert_not_called()

    def test_file_operations_mixin_reload(self) -> None:
        """
        Scenario: Reload file

        Expected:
            - _loaded should be False before load
            - Load should be called
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm.strategy.load.return_value = {"reloaded": "data"}

        fm.reload()

        assert fm.is_loaded() is True
        fm.strategy.load.assert_called_once_with(file_path)

    def test_file_operations_mixin_mark_as_dirty(self) -> None:
        """
        Scenario: Mark file as dirty

        Expected:
            - _dirty should be True
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)

        fm.mark_as_dirty()

        assert fm.is_dirty() is True

    def test_file_operations_mixin_mark_as_clean(self) -> None:
        """
        Scenario: Mark file as clean

        Expected:
            - _dirty should be False
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._dirty = True

        fm.mark_as_clean()

        assert fm.is_dirty() is False

    def test_file_operations_mixin_ensure_file_exists_file_exists(self) -> None:
        """
        Scenario: Ensure file exists when file already exists

        Expected:
            - File path should be returned
            - File should not be modified
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"existing": "data"}')

        fm = self.MockFileManager(file_path)

        result = fm.ensure_file_exists("new content")

        assert result == file_path
        assert file_path.read_text() == '{"existing": "data"}'

    def test_file_operations_mixin_ensure_file_exists_file_not_exists(self) -> None:
        """
        Scenario: Ensure file exists when file doesn't exist

        Expected:
            - File should be created with content
            - _loaded should be True
            - Save should be called
        """
        file_path = self.temp_path / "new_file.json"

        fm = self.MockFileManager(file_path)

        with patch.object(fm, "save") as mock_save:
            result = fm.ensure_file_exists("new content")

        assert result == file_path
        assert file_path.exists()
        assert file_path.read_text() == "new content"
        assert fm.is_loaded() is True
        mock_save.assert_called_once()

    def test_file_operations_mixin_ensure_file_exists_create_directory(self) -> None:
        """
        Scenario: Ensure file exists when parent directory doesn't exist

        Expected:
            - Parent directory should be created
            - File should be created
        """
        file_path = self.temp_path / "subdir" / "test.json"

        fm = self.MockFileManager(file_path)

        with patch.object(fm, "save"):
            result = fm.ensure_file_exists("content")

        assert result == file_path
        assert file_path.exists()
        assert file_path.parent.exists()
        assert file_path.read_text() == "content"

    def test_file_operations_mixin_state_transitions(self) -> None:
        """
        Scenario: Test various state transitions

        Expected:
            - States should change correctly
            - Methods should work in sequence
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"initial": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"initial": "data"}

        # Initial state
        assert fm.is_loaded() is False
        assert fm.is_dirty() is False

        # Load file
        fm.load()
        assert fm.is_loaded() is True
        assert fm.is_dirty() is False

        # Mark as dirty
        fm.mark_as_dirty()
        assert fm.is_loaded() is True
        assert fm.is_dirty() is True

        # Save file
        fm.save()
        assert fm.is_loaded() is True
        assert fm.is_dirty() is False

        # Mark as clean
        fm.mark_as_clean()
        assert fm.is_loaded() is True
        assert fm.is_dirty() is False

    def test_file_operations_mixin_integration_workflow(self) -> None:
        """
        Scenario: Test complete workflow integration

        Expected:
            - All methods should work together
            - File operations should be consistent
        """
        file_path = self.temp_path / "workflow.json"
        file_path.write_text('{"initial": "data"}')  # Create file first

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"workflow": "test"}

        # Start with existing file
        assert fm.exists() is True
        assert fm.is_loaded() is False

        # Load file
        fm.load()
        assert fm.is_loaded() is True
        assert fm.document == {"workflow": "test"}
        fm.strategy.load.assert_called_once_with(file_path)

        # Reset mock for next call
        fm.strategy.load.reset_mock()

        # Modify document
        fm.document = {"modified": "data"}
        fm.mark_as_dirty()
        assert fm.is_dirty() is True

        # Save
        fm.save()
        assert fm.is_dirty() is False
        fm.strategy.save.assert_called_once_with(file_path, {"modified": "data"})

        # Reload
        fm.reload()
        assert fm.is_loaded() is True
        fm.strategy.load.assert_called_once_with(file_path)
