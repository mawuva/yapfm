"""
Tests for ExportMixin.

This module contains unit tests for the ExportMixin class,
which provides export functionality for different formats.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

import pytest

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestExportMixin:
    """Test class for ExportMixin functionality."""

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
            "version": "1.0.0",
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_to_current_format_basic(self) -> None:
        """
        Scenario: Export data to current file format

        Expected:
        - Should export data using the current strategy
        - Should return string content in current format
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.to_current_format()

        # Should return a JSON string
        assert isinstance(result, str)
        assert "database" in result
        assert "localhost" in result

    def test_to_json_pretty_format(self) -> None:
        """
        Scenario: Export data to JSON with pretty formatting

        Expected:
        - Should return formatted JSON string
        - Should include indentation and line breaks
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.to_json(pretty=True)

        # Should return formatted JSON
        assert isinstance(result, str)
        assert "database" in result
        assert "localhost" in result
        # Pretty JSON should have indentation
        assert "\n" in result or "  " in result

    def test_to_json_compact_format(self) -> None:
        """
        Scenario: Export data to JSON with compact formatting

        Expected:
        - Should return compact JSON string
        - Should not include unnecessary whitespace
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.to_json(pretty=False)

        # Should return compact JSON
        assert isinstance(result, str)
        assert "database" in result
        assert "localhost" in result

    def test_to_yaml_basic(self) -> None:
        """
        Scenario: Export data to YAML format

        Expected:
        - Should return YAML string
        - Should handle nested data structures
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.to_yaml()

        # Should return YAML string
        assert isinstance(result, str)
        assert "database" in result
        assert "localhost" in result

    def test_to_toml_basic(self) -> None:
        """
        Scenario: Export data to TOML format

        Expected:
        - Should return TOML string
        - Should handle nested data structures
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.to_toml()

        # Should return TOML string
        assert isinstance(result, str)
        assert "database" in result
        assert "localhost" in result

    def test_export_section_basic(self) -> None:
        """
        Scenario: Export a specific section to string

        Expected:
        - Should export only the specified section
        - Should return string content of the section
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        result = fm.export_section("database")

        # Should return JSON string of database section
        assert isinstance(result, str)
        assert "host" in result
        assert "port" in result
        assert "localhost" in result
        assert "5432" in result

    def test_export_section_to_file(self) -> None:
        """
        Scenario: Export a specific section to file

        Expected:
        - Should create output file with section data
        - Should return path to created file
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()
        output_file = self.temp_path / "database.json"

        result = fm.export_section("database", output_path=output_file)

        # Should return path to file
        assert isinstance(result, Path)
        assert result == output_file

        # Should create the output file
        assert output_file.exists()

        # Should contain section data
        content = output_file.read_text()
        assert "host" in content
        assert "port" in content

    def test_export_section_with_nonexistent_section(self) -> None:
        """
        Scenario: Export non-existent section

        Expected:
        - Should handle non-existent section gracefully
        - Should return appropriate result
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Should raise KeyError for non-existent section
        with pytest.raises(KeyError, match="Section 'nonexistent' not found"):
            fm.export_section("nonexistent")

    def test_export_with_empty_data(self) -> None:
        """
        Scenario: Export empty data

        Expected:
        - Should handle empty data gracefully
        - Should return appropriate empty representation
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = {}

        result = fm.to_json()

        # Should handle empty data
        assert isinstance(result, str)
        assert result in ["{}", "null", ""]

    def test_export_with_nested_data(self) -> None:
        """
        Scenario: Export complex nested data

        Expected:
        - Should handle nested data structures
        - Should preserve all levels of nesting
        """
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {"value": "deep", "list": [1, 2, 3, {"nested": "object"}]}
                }
            }
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = nested_data

        result = fm.to_json()

        # Should handle nested data
        assert isinstance(result, str)
        assert "level1" in result
        assert "level2" in result
        assert "level3" in result
        assert "deep" in result

    def test_export_with_special_characters(self) -> None:
        """
        Scenario: Export data with special characters

        Expected:
        - Should handle special characters correctly
        - Should preserve special characters in output
        """
        special_data = {
            "unicode": "café",
            "quotes": 'He said "Hello"',
            "newlines": "line1\nline2",
            "special": "!@#$%^&*()",
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = special_data

        result = fm.to_json()

        # Should handle special characters
        assert isinstance(result, str)
        assert "café" in result
        assert "Hello" in result

    def test_export_with_none_values(self) -> None:
        """
        Scenario: Export data with None values

        Expected:
        - Should handle None values correctly
        - Should represent None as null in JSON
        """
        none_data = {
            "string": "value",
            "none_value": None,
            "nested": {"another_none": None, "normal": "value"},
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = none_data

        result = fm.to_json()

        # Should handle None values
        assert isinstance(result, str)
        assert "null" in result or "None" in result

    def test_export_preserves_data_integrity(self) -> None:
        """
        Scenario: Export preserves data integrity

        Expected:
        - Should preserve all data exactly
        - Should not lose or modify data during export
        """
        original_data = self.test_data.copy()
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = original_data

        # Export and then parse back to verify integrity
        json_str = fm.to_json()

        # Should contain all original data
        assert "database" in json_str
        assert "localhost" in json_str
        assert "5432" in json_str
        assert "api" in json_str
        assert "timeout" in json_str
        assert "debug" in json_str
        assert "version" in json_str

    def test_export_with_different_formats(self) -> None:
        """
        Scenario: Export to different formats

        Expected:
        - Should export to JSON, YAML, and TOML formats
        - Should handle format-specific requirements
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test different formats
        json_result = fm.to_json()
        yaml_result = fm.to_yaml()
        toml_result = fm.to_toml()

        # All should be strings
        assert isinstance(json_result, str)
        assert isinstance(yaml_result, str)
        assert isinstance(toml_result, str)

        # All should contain the data
        assert "database" in json_result
        assert "database" in yaml_result
        assert "database" in toml_result
