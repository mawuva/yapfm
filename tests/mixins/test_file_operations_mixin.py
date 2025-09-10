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
            - mark_as_loaded should be called internally
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

    def test_file_operations_mixin_mark_as_loaded(self) -> None:
        """
        Scenario: Mark file as loaded

        Expected:
            - _loaded should be True
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)

        fm.mark_as_loaded()

        assert fm.is_loaded() is True

    def test_file_operations_mixin_unload(self) -> None:
        """
        Scenario: Unload file

        Expected:
            - _loaded should be False
            - _dirty should be False
            - document should be empty dict
        """
        file_path = self.temp_path / "test.json"

        fm = self.MockFileManager(file_path)
        fm._loaded = True
        fm._dirty = True
        fm.document = {"test": "data"}

        fm.unload()

        assert fm.is_loaded() is False
        assert fm.is_dirty() is False
        assert fm.document == {}

    def test_file_operations_mixin_create_empty_file(self) -> None:
        """
        Scenario: Create empty file

        Expected:
            - File should be created
            - Parent directory should be created if needed
            - _loaded should be True
            - Save should be called
        """
        file_path = self.temp_path / "subdir" / "empty.json"

        fm = self.MockFileManager(file_path)

        with patch.object(fm, "save") as mock_save:
            fm.create_empty_file()

        assert file_path.exists()
        assert file_path.parent.exists()
        assert file_path.read_text() == ""
        assert fm.is_loaded() is True
        mock_save.assert_called_once()

    def test_file_operations_mixin_create_empty_file_existing_directory(self) -> None:
        """
        Scenario: Create empty file when parent directory already exists

        Expected:
            - File should be created
            - _loaded should be True
            - Save should be called
        """
        file_path = self.temp_path / "empty.json"

        fm = self.MockFileManager(file_path)

        with patch.object(fm, "save") as mock_save:
            fm.create_empty_file()

        assert file_path.exists()
        assert file_path.read_text() == ""
        assert fm.is_loaded() is True
        mock_save.assert_called_once()

    def test_file_operations_mixin_load_behavior_with_new_methods(self) -> None:
        """
        Scenario: Test load behavior with new mark_as_loaded method

        Expected:
            - Load should use mark_as_loaded internally
            - State should be consistent
        """
        file_path = self.temp_path / "test.json"
        file_path.write_text('{"test": "data"}')

        fm = self.MockFileManager(file_path)
        fm.strategy.load.return_value = {"test": "data"}

        # Test load with existing file
        fm.load()

        assert fm.document == {"test": "data"}
        assert fm.is_loaded() is True
        fm.strategy.load.assert_called_once_with(file_path)

        # Test load with non-existing file (should create empty document)
        file_path2 = self.temp_path / "nonexistent.json"
        fm2 = self.MockFileManager(file_path2)

        fm2.load()

        assert fm2.document == {}
        assert fm2.is_loaded() is True
        fm2.strategy.load.assert_not_called()

    def test_file_operations_mixin_complete_lifecycle(self) -> None:
        """
        Scenario: Test complete file lifecycle with new methods

        Expected:
            - All methods should work together
            - State transitions should be correct
        """
        file_path = self.temp_path / "lifecycle.json"

        fm = self.MockFileManager(file_path)

        # Initial state
        assert fm.is_loaded() is False
        assert fm.is_dirty() is False
        assert fm.document == {}

        # Create empty file
        with patch.object(fm, "save") as mock_save:
            fm.create_empty_file()

        assert file_path.exists()
        assert fm.is_loaded() is True
        assert fm.is_dirty() is False
        mock_save.assert_called_once()

        # Load existing file
        file_path.write_text('{"loaded": "data"}')
        fm.strategy.load.return_value = {"loaded": "data"}
        fm.load()

        assert fm.document == {"loaded": "data"}
        assert fm.is_loaded() is True
        assert fm.is_dirty() is False

        # Modify and mark as dirty
        fm.document = {"modified": "data"}
        fm.mark_as_dirty()
        assert fm.is_dirty() is True

        # Save
        fm.save()
        assert fm.is_dirty() is False

        # Unload
        fm.unload()
        assert fm.is_loaded() is False
        assert fm.is_dirty() is False
        assert fm.document == {}

        # Reload
        fm.strategy.load.return_value = {"reloaded": "data"}
        fm.reload()
        assert fm.is_loaded() is True
        assert fm.document == {"reloaded": "data"}
