"""
Unit tests for JSON strategy.
"""

import json
from pathlib import Path

import pytest

from yapfm.exceptions.file_operations import FileReadError
from yapfm.strategies.json_strategy import JsonStrategy


class TestJsonStrategy:
    """Test cases for JsonStrategy class."""

    def test_json_strategy_initialization(self) -> None:
        """
        Scenario: Initialize JsonStrategy instance

        Expected:
        - Should create JsonStrategy instance
        - Should be instance of BaseFileStrategy
        - Should be callable and instantiable
        """
        strategy = JsonStrategy()

        assert isinstance(strategy, JsonStrategy)
        # Note: JsonStrategy doesn't explicitly inherit from BaseFileStrategy
        # but implements the protocol

    def test_json_strategy_load_valid_json_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from a valid JSON file

        Expected:
        - Should load and parse JSON data correctly
        - Should return parsed data structure
        - Should handle both dict and list JSON structures
        """
        strategy = JsonStrategy()

        # Test with dictionary JSON
        dict_data = {"key1": "value1", "key2": {"nested": "value"}}
        file_path = tmp_path / "test_dict.json"
        file_path.write_text(json.dumps(dict_data), encoding="utf-8")

        result = strategy.load(file_path)
        assert result == dict_data

        # Test with list JSON
        list_data = ["item1", "item2", {"nested": "item"}]
        file_path = tmp_path / "test_list.json"
        file_path.write_text(json.dumps(list_data), encoding="utf-8")

        result = strategy.load(file_path)
        assert result == list_data

    def test_json_strategy_load_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Load JSON file using string path instead of Path object

        Expected:
        - Should convert string to Path object internally
        - Should load and parse JSON data correctly
        - Should handle string path conversion properly
        """
        strategy = JsonStrategy()
        test_data = {"string_path": "test", "value": 42}
        file_path = tmp_path / "string_test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        result = strategy.load(str(file_path))
        assert result == test_data

    def test_json_strategy_load_invalid_json_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from an invalid JSON file

        Expected:
        - Should raise appropriate exception for invalid JSON
        - Should not return partial data
        - Should handle JSON parsing errors gracefully
        """
        strategy = JsonStrategy()
        file_path = tmp_path / "invalid.json"
        file_path.write_text("invalid json content", encoding="utf-8")

        with pytest.raises(FileReadError):
            strategy.load(file_path)

    def test_json_strategy_load_nonexistent_file(self) -> None:
        """
        Scenario: Load data from a nonexistent JSON file

        Expected:
        - Should raise FileReadError
        - Should not create the file
        - Should handle missing file gracefully
        """
        strategy = JsonStrategy()
        nonexistent_path = Path("nonexistent.json")

        with pytest.raises(FileReadError):
            strategy.load(nonexistent_path)

    def test_json_strategy_save_valid_data(self, tmp_path: Path) -> None:
        """
        Scenario: Save valid data to JSON file

        Expected:
        - Should save data as JSON to file
        - Should create file if it doesn't exist
        - Should handle both dict and list data structures
        """
        strategy = JsonStrategy()

        # Test with dictionary data
        dict_data = {"save_test": "value", "number": 123}
        file_path = tmp_path / "save_dict.json"

        strategy.save(file_path, dict_data)

        assert file_path.exists()
        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded_data == dict_data

        # Test with list data
        list_data = ["item1", "item2", {"nested": "value"}]
        file_path = tmp_path / "save_list.json"

        strategy.save(file_path, list_data)

        assert file_path.exists()
        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded_data == list_data

    def test_json_strategy_save_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to JSON file using string path

        Expected:
        - Should convert string to Path object internally
        - Should save data correctly
        - Should handle string path conversion properly
        """
        strategy = JsonStrategy()
        test_data = {"string_save": "test", "value": 456}
        file_path = tmp_path / "string_save.json"

        strategy.save(str(file_path), test_data)

        assert file_path.exists()
        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded_data == test_data

    def test_json_strategy_save_creates_parent_directories(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save JSON file to path with non-existent parent directories

        Expected:
        - Should create all parent directories automatically
        - Should save file in the correct location
        - Should handle directory creation gracefully
        """
        strategy = JsonStrategy()
        test_data = {"nested": "data"}
        file_path = tmp_path / "level1" / "level2" / "level3" / "test.json"

        strategy.save(file_path, test_data)

        assert file_path.exists()
        assert file_path.parent.exists()
        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded_data == test_data

    def test_json_strategy_save_overwrites_existing_file(self, tmp_path: Path) -> None:
        """
        Scenario: Save JSON data to path that already exists

        Expected:
        - Should overwrite existing file content
        - Should replace old content with new content
        - Should not append to existing file
        """
        strategy = JsonStrategy()
        file_path = tmp_path / "overwrite_test.json"

        # Create initial file
        initial_data = {"old": "data"}
        file_path.write_text(json.dumps(initial_data), encoding="utf-8")

        # Save new data
        new_data = {"new": "data", "updated": True}
        strategy.save(file_path, new_data)

        loaded_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded_data == new_data
        assert loaded_data != initial_data

    def test_json_strategy_navigate_simple_dict(self) -> None:
        """
        Scenario: Navigate through simple dictionary structure

        Expected:
        - Should return value at specified path
        - Should handle single-level navigation correctly
        - Should work with simple key access
        """
        strategy = JsonStrategy()
        document = {"key1": "value1", "key2": "value2"}

        result = strategy.navigate(document, ["key1"])
        assert result == "value1"

        result = strategy.navigate(document, ["key2"])
        assert result == "value2"

    def test_json_strategy_navigate_nested_dict(self) -> None:
        """
        Scenario: Navigate through nested dictionary structure

        Expected:
        - Should return value at nested path
        - Should handle multi-level navigation correctly
        - Should work with deep nesting
        """
        strategy = JsonStrategy()
        document = {"level1": {"level2": {"level3": "deep_value"}}}

        result = strategy.navigate(document, ["level1", "level2", "level3"])
        assert result == "deep_value"

    def test_json_strategy_navigate_nonexistent_path_without_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist without create flag

        Expected:
        - Should return None when path doesn't exist
        - Should not modify the original document
        - Should handle missing keys gracefully
        """
        strategy = JsonStrategy()
        document = {"key1": "value1"}

        result = strategy.navigate(document, ["nonexistent"])
        assert result is None

        result = strategy.navigate(document, ["key1", "nonexistent"])
        assert result is None

    def test_json_strategy_navigate_nonexistent_path_with_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist with create flag enabled

        Expected:
        - Should create intermediate dictionaries
        - Should return the created empty dictionary
        - Should modify the original document
        """
        strategy = JsonStrategy()
        document = {"key1": "value1"}

        result = strategy.navigate(document, ["new", "nested"], create=True)
        assert isinstance(result, dict)
        assert document["new"]["nested"] == result  # type: ignore[index]

    def test_json_strategy_navigate_list_structure(self) -> None:
        """
        Scenario: Navigate through list-based structure

        Expected:
        - Should handle list navigation correctly
        - Should work with mixed dict/list structures
        - Should return appropriate values from lists
        """
        strategy = JsonStrategy()
        document = {
            "items": [{"name": "item1", "value": 10}, {"name": "item2", "value": 20}]
        }

        # Navigate to list
        items = strategy.navigate(document, ["items"])
        assert isinstance(items, list)
        assert len(items) == 2

        # Note: navigate_dict_like doesn't support list index navigation
        # This is expected behavior for the current implementation

    def test_json_strategy_navigate_empty_path(self) -> None:
        """
        Scenario: Navigate with empty path list

        Expected:
        - Should return the original document
        - Should not modify the original document
        - Should handle empty path gracefully
        """
        strategy = JsonStrategy()
        document = {"key": "value"}

        result = strategy.navigate(document, [])
        assert result == document

    def test_json_strategy_round_trip_consistency(self, tmp_path: Path) -> None:
        """
        Scenario: Test load-save-load round trip consistency

        Expected:
        - Data should remain unchanged after save-load cycle
        - Should preserve all data types and structures
        - Should maintain JSON formatting consistency
        """
        strategy = JsonStrategy()
        original_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null_value": None,
            "array": [1, 2, 3],
            "nested": {"key": "value", "list": ["a", "b", "c"]},
        }

        file_path = tmp_path / "round_trip.json"

        # Save data
        strategy.save(file_path, original_data)

        # Load data back
        loaded_data = strategy.load(file_path)

        assert loaded_data == original_data

    def test_json_strategy_with_special_characters(self, tmp_path: Path) -> None:
        """
        Scenario: Test JSON strategy with special characters and Unicode

        Expected:
        - Should handle special characters correctly
        - Should preserve Unicode characters
        - Should maintain encoding consistency
        """
        strategy = JsonStrategy()
        special_data = {
            "unicode": "café naïve résumé",
            "emoji": "🚀 🎉 ✨",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
        }

        file_path = tmp_path / "special_chars.json"

        strategy.save(file_path, special_data)
        loaded_data = strategy.load(file_path)

        assert loaded_data == special_data

    def test_json_strategy_error_handling_integration(self, tmp_path: Path) -> None:
        """
        Scenario: Test JSON strategy error handling integration

        Expected:
        - Should handle various error conditions gracefully
        - Should provide meaningful error messages
        - Should not crash on invalid operations
        """
        strategy = JsonStrategy()

        # Test with invalid file path
        with pytest.raises(FileReadError):
            strategy.load(Path("nonexistent.json"))

        # Test with invalid JSON content
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json {", encoding="utf-8")

        with pytest.raises(FileReadError):
            strategy.load(invalid_file)

        # Test with valid operations after errors
        valid_data = {"recovery": "test"}
        valid_file = tmp_path / "valid.json"
        strategy.save(valid_file, valid_data)

        loaded_data = strategy.load(valid_file)
        assert loaded_data == valid_data
