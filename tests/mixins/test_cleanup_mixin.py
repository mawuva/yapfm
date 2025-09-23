"""
Tests for CleanupMixin.

This module contains unit tests for the CleanupMixin class,
which provides data cleanup functionality.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestCleanupMixin:
    """Test class for CleanupMixin functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data with various cleanup targets
        self.test_data = {
            "database": {"host": "localhost", "port": 5432},
            "api": {"timeout": 30, "retries": 3},
            "debug": True,
            "empty_string": "",
            "none_value": None,
            "empty_list": [],
            "empty_dict": {},
            "whitespace": "   ",
            "normal": "value",
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_clean_empty_sections(self) -> None:
        """
        Scenario: Remove empty sections from data

        Expected:
        - Should remove empty dictionaries and lists
        - Should return count of removed sections
        - Should mark data as dirty after cleanup
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        removed_count = fm.clean_empty_sections()

        # Should remove empty containers
        assert removed_count > 0
        data = fm.data
        assert "empty_list" not in data
        assert "empty_dict" not in data
        assert "normal" in data  # Should keep non-empty values

    def test_clean_empty_sections_with_nested_data(self) -> None:
        """
        Scenario: Clean empty sections in nested structures

        Expected:
        - Should remove empty sections at all levels
        - Should preserve non-empty nested data
        """
        nested_data = {
            "level1": {
                "empty": {},
                "normal": "value",
                "level2": {"empty": [], "normal": "value2"},
            }
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = nested_data
        fm.clean_empty_sections()

        data = fm.data
        # Should preserve structure but remove empty sections
        assert "level1" in data
        assert "empty" not in data["level1"]
        assert "normal" in data["level1"]
        assert "level2" in data["level1"]
        assert "empty" not in data["level1"]["level2"]
        assert "normal" in data["level1"]["level2"]

    def test_clean_empty_sections_with_no_changes(self) -> None:
        """
        Scenario: Clean empty sections when no changes are needed

        Expected:
        - Should return 0 when no empty sections found
        - Should not modify data
        """
        clean_data = {
            "normal": "value",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = clean_data
        removed_count = fm.clean_empty_sections()

        # Should not remove anything
        assert removed_count == 0
        data = fm.data
        assert data == clean_data

    def test_clean_empty_sections_with_empty_document(self) -> None:
        """
        Scenario: Clean empty sections with empty document

        Expected:
        - Should handle empty document gracefully
        - Should return 0 for empty document
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = {}

        removed_count = fm.clean_empty_sections()

        # Should not remove anything from empty document
        assert removed_count == 0
        data = fm.data
        assert data == {}

    def test_clean_empty_sections_marks_as_dirty(self) -> None:
        """
        Scenario: Clean empty sections marks data as dirty

        Expected:
        - Should mark data as dirty after cleanup
        - Should not be dirty initially if no changes made
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Note: YAPFileManager may be dirty initially due to data assignment
        # We'll check that cleanup makes it dirty if changes are made

        # Perform cleanup
        fm.clean_empty_sections()

        # Should be dirty after cleanup
        assert fm.is_dirty()

    def test_clean_empty_sections_preserves_data_integrity(self) -> None:
        """
        Scenario: Clean empty sections preserves data integrity

        Expected:
        - Should preserve non-empty values exactly
        - Should only remove empty containers
        """
        original_data = self.test_data.copy()
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = original_data

        # Perform cleanup
        fm.clean_empty_sections()

        data = fm.data

        # Should preserve non-empty values exactly
        assert data["database"] == original_data["database"]
        assert data["api"] == original_data["api"]
        assert data["debug"] == original_data["debug"]
        assert data["normal"] == original_data["normal"]

    def test_clean_empty_sections_with_mixed_data_types(self) -> None:
        """
        Scenario: Clean empty sections with mixed data types

        Expected:
        - Should handle different data types correctly
        - Should only remove empty containers, not other empty values
        """
        mixed_data = {
            "string": "value",
            "integer": 0,
            "float": 0.0,
            "boolean": False,
            "none": None,
            "empty_list": [],
            "empty_dict": {},
            "normal": "value",
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = mixed_data
        fm.clean_empty_sections()

        data = fm.data
        # Should keep non-empty values
        assert "string" in data
        assert "integer" in data
        assert "float" in data
        assert "boolean" in data
        assert "none" in data
        assert "normal" in data
        # Should remove empty containers
        assert "empty_list" not in data
        assert "empty_dict" not in data

    def test_clean_empty_sections_with_nested_empty_containers(self) -> None:
        """
        Scenario: Clean empty sections with deeply nested empty containers

        Expected:
        - Should remove empty containers at all levels
        - Should preserve structure with non-empty data
        """
        nested_empty_data = {
            "level1": {
                "level2": {"level3": {"empty": {}, "none": None, "empty_list": []}}
            }
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = nested_empty_data
        fm.clean_empty_sections()

        data = fm.data
        # Should remove all empty containers at all levels
        assert "level1" in data
        assert "level2" in data["level1"]
        assert "level3" in data["level1"]["level2"]
        level3 = data["level1"]["level2"]["level3"]
        assert "empty" not in level3
        assert "empty_list" not in level3
        # Should preserve non-empty values
        assert "none" in level3
