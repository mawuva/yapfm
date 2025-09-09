"""
Unit tests for YAML strategy.
"""

from pathlib import Path

import pytest
from yaml import safe_dump

from yapfm.exceptions.file_operations import FileReadError
from yapfm.strategies.yaml_strategy import YamlStrategy


class TestYamlStrategy:
    """Test cases for YamlStrategy class."""

    def test_yaml_strategy_initialization(self) -> None:
        """
        Scenario: Initialize YamlStrategy instance

        Expected:
        - Should create YamlStrategy instance
        - Should be callable and instantiable
        - Should have required methods available
        """
        strategy = YamlStrategy()

        assert isinstance(strategy, YamlStrategy)
        assert hasattr(strategy, "load")
        assert hasattr(strategy, "save")
        assert hasattr(strategy, "navigate")

    def test_yaml_strategy_load_valid_yaml_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from a valid YAML file

        Expected:
        - Should load and parse YAML data correctly
        - Should return parsed data structure
        - Should handle nested structures
        """
        strategy = YamlStrategy()

        yaml_content = """
        title: Test YAML
        version: 1.0.0
        database:
          host: localhost
          port: 5432
          credentials:
            username: admin
            password: secret
        """

        file_path = tmp_path / "test.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        result = strategy.load(file_path)

        assert isinstance(result, dict)
        assert result["title"] == "Test YAML"
        assert result["version"] == "1.0.0"
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        assert result["database"]["credentials"]["username"] == "admin"

    def test_yaml_strategy_load_with_yml_extension(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from a valid YAML file with .yml extension

        Expected:
        - Should load and parse YAML data correctly
        - Should handle .yml extension
        - Should work the same as .yaml extension
        """
        strategy = YamlStrategy()

        yaml_content = """
        yml_extension: test
        value: 42
        """

        file_path = tmp_path / "test.yml"
        file_path.write_text(yaml_content, encoding="utf-8")

        result = strategy.load(file_path)

        assert isinstance(result, dict)
        assert result["yml_extension"] == "test"
        assert result["value"] == 42

    def test_yaml_strategy_load_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Load YAML file using string path instead of Path object

        Expected:
        - Should convert string to Path object internally
        - Should load and parse YAML data correctly
        - Should handle string path conversion properly
        """
        strategy = YamlStrategy()
        yaml_content = """
        string_path: test
        value: 42
        """

        file_path = tmp_path / "string_test.yaml"
        file_path.write_text(yaml_content, encoding="utf-8")

        result = strategy.load(str(file_path))

        assert isinstance(result, dict)
        assert result["string_path"] == "test"
        assert result["value"] == 42

    def test_yaml_strategy_load_invalid_yaml_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from an invalid YAML file

        Expected:
        - Should raise appropriate exception for invalid YAML
        - Should not return partial data
        - Should handle YAML parsing errors gracefully
        """
        strategy = YamlStrategy()
        file_path = tmp_path / "invalid.yaml"
        file_path.write_text("invalid yaml content: [unclosed", encoding="utf-8")

        with pytest.raises(Exception):  # PyYAML raises various exceptions
            strategy.load(file_path)

    def test_yaml_strategy_load_nonexistent_file(self) -> None:
        """
        Scenario: Load data from a nonexistent YAML file

        Expected:
        - Should raise FileReadError
        - Should not create the file
        - Should handle missing file gracefully
        """
        strategy = YamlStrategy()
        nonexistent_path = Path("nonexistent.yaml")

        with pytest.raises(FileReadError):
            strategy.load(nonexistent_path)

    def test_yaml_strategy_save_valid_data(self, tmp_path: Path) -> None:
        """
        Scenario: Save valid data to YAML file

        Expected:
        - Should save data as YAML to file
        - Should create file if it doesn't exist
        - Should handle nested dictionary structures
        """
        strategy = YamlStrategy()

        data = {
            "save_test": "value",
            "number": 123,
            "nested": {"key": "value", "list": [1, 2, 3]},
        }

        file_path = tmp_path / "save_test.yaml"

        strategy.save(file_path, data)

        assert file_path.exists()

        # Load and verify
        loaded_data = strategy.load(file_path)
        assert loaded_data == data

    def test_yaml_strategy_save_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to YAML file using string path

        Expected:
        - Should convert string to Path object internally
        - Should save data correctly
        - Should handle string path conversion properly
        """
        strategy = YamlStrategy()
        data = {"string_save": "test", "value": 456}

        file_path = tmp_path / "string_save.yaml"

        strategy.save(str(file_path), data)

        assert file_path.exists()

        loaded_data = strategy.load(file_path)
        assert loaded_data == data

    def test_yaml_strategy_save_creates_parent_directories(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save YAML file to path with non-existent parent directories

        Expected:
        - Should create all parent directories automatically
        - Should save file in the correct location
        - Should handle directory creation gracefully
        """
        strategy = YamlStrategy()
        data = {"nested": "data"}

        file_path = tmp_path / "level1" / "level2" / "level3" / "test.yaml"

        strategy.save(file_path, data)

        assert file_path.exists()
        assert file_path.parent.exists()

        loaded_data = strategy.load(file_path)
        assert loaded_data == data

    def test_yaml_strategy_save_overwrites_existing_file(self, tmp_path: Path) -> None:
        """
        Scenario: Save YAML data to path that already exists

        Expected:
        - Should overwrite existing file content
        - Should replace old content with new content
        - Should not append to existing file
        """
        strategy = YamlStrategy()
        file_path = tmp_path / "overwrite_test.yaml"

        # Create initial file
        initial_data = {"old": "data"}
        file_path.write_text(safe_dump(initial_data), encoding="utf-8")

        # Save new data
        new_data = {"new": "data", "updated": True}
        strategy.save(file_path, new_data)

        loaded_data = strategy.load(file_path)
        assert loaded_data == new_data
        assert loaded_data != initial_data

    def test_yaml_strategy_navigate_simple_dict(self) -> None:
        """
        Scenario: Navigate through simple dictionary structure

        Expected:
        - Should return value at specified path
        - Should handle single-level navigation correctly
        - Should work with simple key access
        """
        strategy = YamlStrategy()
        document = {"key1": "value1", "key2": "value2"}

        result = strategy.navigate(document, ["key1"])
        assert result == "value1"

        result = strategy.navigate(document, ["key2"])
        assert result == "value2"

    def test_yaml_strategy_navigate_nested_dict(self) -> None:
        """
        Scenario: Navigate through nested dictionary structure

        Expected:
        - Should return value at nested path
        - Should handle multi-level navigation correctly
        - Should work with deep nesting
        """
        strategy = YamlStrategy()
        document = {"level1": {"level2": {"level3": "deep_value"}}}

        result = strategy.navigate(document, ["level1", "level2", "level3"])
        assert result == "deep_value"

    def test_yaml_strategy_navigate_nonexistent_path_without_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist without create flag

        Expected:
        - Should return None when path doesn't exist
        - Should not modify the original document
        - Should handle missing keys gracefully
        """
        strategy = YamlStrategy()
        document = {"key1": "value1"}

        result = strategy.navigate(document, ["nonexistent"])
        assert result is None

        result = strategy.navigate(document, ["key1", "nonexistent"])
        assert result is None

    def test_yaml_strategy_navigate_nonexistent_path_with_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist with create flag enabled

        Expected:
        - Should create intermediate dictionaries
        - Should return the created empty dictionary
        - Should modify the original document
        """
        strategy = YamlStrategy()
        document = {"key1": "value1"}

        result = strategy.navigate(document, ["new", "nested"], create=True)
        assert isinstance(result, dict)
        assert document["new"]["nested"] == result  # type: ignore[index]

    def test_yaml_strategy_navigate_list_structure(self) -> None:
        """
        Scenario: Navigate through list-based structure

        Expected:
        - Should handle list navigation correctly
        - Should work with mixed dict/list structures
        - Should return appropriate values from lists
        """
        strategy = YamlStrategy()
        document = {
            "items": [{"name": "item1", "value": 10}, {"name": "item2", "value": 20}]
        }

        # Navigate to list
        items = strategy.navigate(document, ["items"])
        assert isinstance(items, list)
        assert len(items) == 2

    def test_yaml_strategy_navigate_empty_path(self) -> None:
        """
        Scenario: Navigate with empty path list

        Expected:
        - Should return the original document
        - Should not modify the original document
        - Should handle empty path gracefully
        """
        strategy = YamlStrategy()
        document = {"key": "value"}

        result = strategy.navigate(document, [])
        assert result == document

    def test_yaml_strategy_round_trip_consistency(self, tmp_path: Path) -> None:
        """
        Scenario: Test load-save-load round trip consistency

        Expected:
        - Data should remain unchanged after save-load cycle
        - Should preserve all data types and structures
        - Should maintain YAML formatting consistency
        """
        strategy = YamlStrategy()
        original_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null_value": None,
            "array": [1, 2, 3],
            "nested": {"key": "value", "list": ["a", "b", "c"]},
        }

        file_path = tmp_path / "round_trip.yaml"

        # Save data
        strategy.save(file_path, original_data)

        # Load data back
        loaded_data = strategy.load(file_path)

        assert loaded_data == original_data

    def test_yaml_strategy_with_special_characters(self, tmp_path: Path) -> None:
        """
        Scenario: Test YAML strategy with special characters and Unicode

        Expected:
        - Should handle special characters correctly
        - Should preserve Unicode characters
        - Should maintain encoding consistency
        """
        strategy = YamlStrategy()
        special_data = {
            "unicode": "café naïve résumé",
            "emoji": "🚀 🎉 ✨",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
        }

        file_path = tmp_path / "special_chars.yaml"

        strategy.save(file_path, special_data)
        loaded_data = strategy.load(file_path)

        assert loaded_data == special_data

    def test_yaml_strategy_with_complex_data_types(self, tmp_path: Path) -> None:
        """
        Scenario: Test YAML strategy with complex data types

        Expected:
        - Should handle various Python data types
        - Should preserve type information
        - Should maintain data integrity
        """
        strategy = YamlStrategy()
        complex_data = {
            "string": "test",
            "integer": 42,
            "float": 3.14159,
            "boolean_true": True,
            "boolean_false": False,
            "none_value": None,
            "list_of_strings": ["a", "b", "c"],
            "list_of_numbers": [1, 2, 3, 4, 5],
            "mixed_list": [1, "two", 3.0, True, None],
            "nested_dict": {"level1": {"level2": {"level3": "deep_value"}}},
            "list_of_dicts": [
                {"name": "item1", "value": 10},
                {"name": "item2", "value": 20},
            ],
        }

        file_path = tmp_path / "complex_types.yaml"

        strategy.save(file_path, complex_data)
        loaded_data = strategy.load(file_path)

        assert loaded_data == complex_data

    def test_yaml_strategy_error_handling_integration(self, tmp_path: Path) -> None:
        """
        Scenario: Test YAML strategy error handling integration

        Expected:
        - Should handle various error conditions gracefully
        - Should provide meaningful error messages
        - Should not crash on invalid operations
        """
        strategy = YamlStrategy()

        # Test with invalid file path
        with pytest.raises(FileReadError):
            strategy.load(Path("nonexistent.yaml"))

        # Test with invalid YAML content
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("invalid yaml: [unclosed", encoding="utf-8")

        with pytest.raises(Exception):  # PyYAML raises various exceptions
            strategy.load(invalid_file)

        # Test with valid operations after errors
        valid_data = {"recovery": "test"}
        valid_file = tmp_path / "valid.yaml"
        strategy.save(valid_file, valid_data)

        loaded_data = strategy.load(valid_file)
        assert loaded_data == valid_data

    def test_yaml_strategy_with_multiline_strings(self, tmp_path: Path) -> None:
        """
        Scenario: Test YAML strategy with multiline strings

        Expected:
        - Should handle multiline strings correctly
        - Should preserve line breaks and formatting
        - Should maintain string integrity
        """
        strategy = YamlStrategy()
        multiline_data = {
            "description": (
                """This is a multiline string
            that spans multiple lines
            and should be preserved
            exactly as written."""
            ),
            "code_block": (
                """def hello():
                print("Hello, World!")
                return True"""
            ),
            "empty_lines": (
                """Line 1

            Line 3

            Line 5"""
            ),
        }

        file_path = tmp_path / "multiline.yaml"

        strategy.save(file_path, multiline_data)
        loaded_data = strategy.load(file_path)

        assert loaded_data == multiline_data
        assert "spans multiple lines" in loaded_data["description"]
        assert "def hello():" in loaded_data["code_block"]
        assert "Line 1" in loaded_data["empty_lines"]
        assert "Line 3" in loaded_data["empty_lines"]
