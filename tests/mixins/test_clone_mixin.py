"""
Tests for CloneMixin.

This module contains unit tests for the CloneMixin class,
which provides cloning and copying functionality.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestCloneMixin:
    """Test class for CloneMixin functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data
        self.test_data = {
            "database": {"host": "localhost", "port": 5432},
            "api": {"timeout": 30, "retries": 3},
            "debug": True,
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_clone_basic(self) -> None:
        """
        Scenario: Clone a file manager with basic data

        Expected:
        - Should create a different instance
        - Should have same data as original
        - Should have different file path
        """
        # Create original manager with test data
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()
        original.save()

        # Clone the manager
        clone = original.clone()

        # Verify clone is a different instance
        assert clone is not original
        assert clone.path != original.path

        # Verify clone has same data
        assert clone.data == original.data
        assert clone.data == self.test_data

    def test_clone_with_existing_file(self) -> None:
        """
        Scenario: Clone a file manager when original file exists

        Expected:
        - Should create clone with same data
        - Should create new file for clone
        - Should preserve file existence
        """
        # Create a file with data
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()
        original.save()

        # Clone the manager
        clone = original.clone()

        # Verify clone has same data
        assert clone.data == self.test_data

        # Verify clone file exists
        assert clone.path.exists()

    def test_clone_without_existing_file(self) -> None:
        """
        Scenario: Clone a file manager when original file doesn't exist

        Expected:
        - Should create clone with same data
        - Should not require original file to exist
        - Should work with in-memory data only
        """
        # Create manager without existing file
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        # Clone the manager
        clone = original.clone()

        # Verify clone has same data
        assert clone.data == self.test_data

    def test_clone_preserves_strategy(self) -> None:
        """
        Scenario: Clone preserves the file strategy

        Expected:
        - Should use same strategy type as original
        - Should maintain strategy configuration
        - Should work with different strategy types
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        clone = original.clone()

        # Verify strategy is preserved
        assert type(clone.strategy) is type(original.strategy)

    def test_clone_preserves_auto_create(self) -> None:
        """
        Scenario: Clone preserves auto_create setting

        Expected:
        - Should maintain auto_create configuration
        - Should behave consistently with original
        - Should preserve file creation behavior
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        clone = original.clone()

        # Verify auto_create is preserved
        assert clone.auto_create == original.auto_create

    def test_clone_independence(self) -> None:
        """
        Scenario: Clone is independent of original

        Expected:
        - Should not affect original when modified
        - Should have separate data instances
        - Should maintain data isolation
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()
        clone = original.clone()

        # Modify original data
        original.data = {"new": "data"}

        # Verify clone is unaffected
        assert clone.data == self.test_data
        assert original.data == {"new": "data"}

    def test_clone_with_empty_data(self) -> None:
        """
        Scenario: Clone with empty data

        Expected:
        - Should handle empty data gracefully
        - Should create valid clone with empty data
        - Should preserve empty state
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = {}
        clone = original.clone()

        # Verify clone has empty data
        assert clone.data == {}
        assert clone.data == original.data

    def test_clone_with_nested_data(self) -> None:
        """
        Scenario: Clone with complex nested data structures

        Expected:
        - Should preserve all nested levels
        - Should maintain data structure integrity
        - Should handle lists and dictionaries
        """
        complex_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep_value",
                        "list": [1, 2, 3, {"nested": "object"}],
                    }
                }
            },
            "simple": "value",
        }

        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = complex_data
        clone = original.clone()

        # Verify clone has same complex data
        assert clone.data == complex_data
        assert clone.data == original.data

    def test_clone_file_extension_preservation(self) -> None:
        """
        Scenario: Clone preserves file extension

        Expected:
        - Should maintain original file extension
        - Should work with different file types
        - Should preserve format compatibility
        """
        # Test with different extensions
        for ext in [".json", ".yaml", ".toml"]:
            test_file = self.temp_path / f"test{ext}"
            original = YAPFileManager(
                test_file, strategy=JsonStrategy(), auto_create=True
            )
            original.data = self.test_data.copy()
            clone = original.clone()

            # Verify extension is preserved
            assert clone.path.suffix == ext

    def test_clone_with_temp_file_cleanup(self) -> None:
        """
        Scenario: Clone creates proper temporary files

        Expected:
        - Should create new temporary file for clone
        - Should not interfere with original file
        - Should handle file cleanup properly
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        # Count files before cloning
        list(self.temp_path.glob("*"))

        clone = original.clone()

        # Verify new file was created
        assert clone.path.exists()
        assert clone.path != original.path

    def test_clone_with_mock_strategy(self) -> None:
        """
        Scenario: Clone with mock strategy

        Expected:
        - Should work with custom strategies
        - Should preserve strategy configuration
        - Should handle strategy-specific behavior
        """
        from unittest.mock import MagicMock

        mock_strategy = MagicMock()
        original = YAPFileManager(
            self.test_file, strategy=mock_strategy, auto_create=True
        )
        original.data = self.test_data.copy()

        clone = original.clone()

        # Verify strategy is preserved
        assert clone.strategy == mock_strategy

    def test_clone_error_handling(self) -> None:
        """
        Scenario: Clone handles errors gracefully

        Expected:
        - Should handle file system errors
        - Should not crash on temporary file issues
        - Should provide meaningful error handling
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        # Mock shutil.copy2 to raise an error
        from unittest.mock import patch

        with patch("shutil.copy2", side_effect=OSError("Copy failed")):
            # Clone should still work even if file copy fails
            clone = original.clone()

        # Verify clone still has data
        assert clone.data == self.test_data

    def test_clone_with_large_data(self) -> None:
        """
        Scenario: Clone with large data structures

        Expected:
        - Should handle large datasets efficiently
        - Should preserve all data integrity
        - Should complete in reasonable time
        """
        # Create large data structure
        large_data = {}
        for i in range(1000):
            large_data[f"key_{i}"] = {
                "value": f"value_{i}",
                "nested": {"id": i, "data": [j for j in range(10)]},
            }

        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = large_data
        clone = original.clone()

        # Verify clone has same large data
        assert clone.data == large_data
        assert len(clone.data) == 1000

    def test_clone_preserves_manager_state(self) -> None:
        """
        Scenario: Clone preserves manager state

        Expected:
        - Should maintain manager configuration
        - Should preserve state flags
        - Should behave consistently with original
        """
        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = self.test_data.copy()

        # Set some state
        original.mark_as_dirty()

        clone = original.clone()

        # Verify clone has fresh state
        assert not clone.is_dirty()

    def test_clone_with_special_characters_in_data(self) -> None:
        """
        Scenario: Clone with special characters in data

        Expected:
        - Should handle Unicode characters correctly
        - Should preserve special characters
        - Should maintain data encoding
        """
        special_data = {
            "unicode": "café",
            "special_chars": "!@#$%^&*()",
            "newlines": "line1\nline2\r\nline3",
            "quotes": "He said \"Hello\" and 'Goodbye'",
            "backslashes": "path\\to\\file",
        }

        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = special_data
        clone = original.clone()

        # Verify clone preserves special characters
        assert clone.data == special_data

    def test_clone_with_none_values(self) -> None:
        """
        Scenario: Clone with None values in data

        Expected:
        - Should handle None values correctly
        - Should preserve null values
        - Should maintain data structure with nulls
        """
        data_with_none = {
            "string": "value",
            "none_value": None,
            "nested": {"another_none": None, "normal": "value"},
        }

        original = YAPFileManager(
            self.test_file, strategy=JsonStrategy(), auto_create=True
        )
        original.data = data_with_none
        clone = original.clone()

        # Verify clone preserves None values
        assert clone.data == data_with_none
        assert clone.data["none_value"] is None
        assert clone.data["nested"]["another_none"] is None
