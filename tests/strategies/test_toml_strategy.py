"""
Unit tests for TOML strategy.
"""

# mypy: disable-error-code=index

from pathlib import Path

import pytest
from tomlkit import TOMLDocument, table
from tomlkit.items import Table

from yapfm.exceptions.file_operations import FileReadError
from yapfm.strategies.toml_strategy import TomlStrategy


class TestTomlStrategy:
    """Test cases for TomlStrategy class."""

    def test_toml_strategy_initialization(self) -> None:
        """
        Scenario: Initialize TomlStrategy instance

        Expected:
        - Should create TomlStrategy instance
        - Should be callable and instantiable
        - Should have required methods available
        """
        strategy = TomlStrategy()

        assert isinstance(strategy, TomlStrategy)
        assert hasattr(strategy, "load")
        assert hasattr(strategy, "save")
        assert hasattr(strategy, "navigate")

    def test_toml_strategy_load_valid_toml_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from a valid TOML file

        Expected:
        - Should load and parse TOML data correctly
        - Should return TOMLDocument instance
        - Should handle nested table structures
        """
        strategy = TomlStrategy()

        toml_content = """
        title = "Test TOML"
        version = "1.0.0"

        [database]
        host = "localhost"
        port = 5432

        [database.credentials]
        username = "admin"
        password = "secret"
        """

        file_path = tmp_path / "test.toml"
        file_path.write_text(toml_content, encoding="utf-8")

        result = strategy.load(file_path)

        assert isinstance(result, TOMLDocument)
        assert result["title"] == "Test TOML"
        assert result["version"] == "1.0.0"
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        assert result["database"]["credentials"]["username"] == "admin"

    def test_toml_strategy_load_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Load TOML file using string path instead of Path object

        Expected:
        - Should convert string to Path object internally
        - Should load and parse TOML data correctly
        - Should handle string path conversion properly
        """
        strategy = TomlStrategy()
        toml_content = """
        string_path = "test"
        value = 42
        """

        file_path = tmp_path / "string_test.toml"
        file_path.write_text(toml_content, encoding="utf-8")

        result = strategy.load(str(file_path))

        assert isinstance(result, TOMLDocument)
        assert result["string_path"] == "test"
        assert result["value"] == 42

    def test_toml_strategy_load_invalid_toml_file(self, tmp_path: Path) -> None:
        """
        Scenario: Load data from an invalid TOML file

        Expected:
        - Should raise appropriate exception for invalid TOML
        - Should not return partial data
        - Should handle TOML parsing errors gracefully
        """
        strategy = TomlStrategy()
        file_path = tmp_path / "invalid.toml"
        file_path.write_text("invalid toml content [unclosed", encoding="utf-8")

        with pytest.raises(Exception):  # tomlkit raises various exceptions
            strategy.load(file_path)

    def test_toml_strategy_load_nonexistent_file(self) -> None:
        """
        Scenario: Load data from a nonexistent TOML file

        Expected:
        - Should raise FileReadError
        - Should not create the file
        - Should handle missing file gracefully
        """
        strategy = TomlStrategy()
        nonexistent_path = Path("nonexistent.toml")

        with pytest.raises(FileReadError):
            strategy.load(nonexistent_path)

    def test_toml_strategy_save_valid_data(self, tmp_path: Path) -> None:
        """
        Scenario: Save valid data to TOML file

        Expected:
        - Should save data as TOML to file
        - Should create file if it doesn't exist
        - Should handle TOMLDocument and Table structures
        """
        strategy = TomlStrategy()

        # Create TOML document
        doc = TOMLDocument()
        doc["title"] = "Test Document"
        doc["version"] = "1.0.0"

        # Add nested table
        doc["database"] = table()
        doc["database"]["host"] = "localhost"
        doc["database"]["port"] = 5432

        file_path = tmp_path / "save_test.toml"

        strategy.save(file_path, doc)

        assert file_path.exists()

        # Load and verify
        loaded_doc = strategy.load(file_path)
        assert loaded_doc["title"] == "Test Document"
        assert loaded_doc["version"] == "1.0.0"
        assert loaded_doc["database"]["host"] == "localhost"
        assert loaded_doc["database"]["port"] == 5432

    def test_toml_strategy_save_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to TOML file using string path

        Expected:
        - Should convert string to Path object internally
        - Should save data correctly
        - Should handle string path conversion properly
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["string_save"] = "test"
        doc["value"] = 456

        file_path = tmp_path / "string_save.toml"

        strategy.save(str(file_path), doc)

        assert file_path.exists()

        loaded_doc = strategy.load(file_path)
        assert loaded_doc["string_save"] == "test"
        assert loaded_doc["value"] == 456

    def test_toml_strategy_save_creates_parent_directories(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save TOML file to path with non-existent parent directories

        Expected:
        - Should create all parent directories automatically
        - Should save file in the correct location
        - Should handle directory creation gracefully
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["nested"] = "data"

        file_path = tmp_path / "level1" / "level2" / "level3" / "test.toml"

        strategy.save(file_path, doc)

        assert file_path.exists()
        assert file_path.parent.exists()

        loaded_doc = strategy.load(file_path)
        assert loaded_doc["nested"] == "data"

    def test_toml_strategy_save_overwrites_existing_file(self, tmp_path: Path) -> None:
        """
        Scenario: Save TOML data to path that already exists

        Expected:
        - Should overwrite existing file content
        - Should replace old content with new content
        - Should not append to existing file
        """
        strategy = TomlStrategy()
        file_path = tmp_path / "overwrite_test.toml"

        # Create initial file
        initial_doc = TOMLDocument()
        initial_doc["old"] = "data"
        file_path.write_text(str(initial_doc), encoding="utf-8")

        # Save new data
        new_doc = TOMLDocument()
        new_doc["new"] = "data"
        new_doc["updated"] = True

        strategy.save(file_path, new_doc)

        loaded_doc = strategy.load(file_path)
        assert loaded_doc["new"] == "data"
        assert loaded_doc["updated"] is True
        assert "old" not in loaded_doc

    def test_toml_strategy_navigate_simple_toml_document(self) -> None:
        """
        Scenario: Navigate through simple TOML document structure

        Expected:
        - Should return None for simple values (navigate only works with tables)
        - Should handle single-level navigation correctly
        - Should work with simple key access
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["key1"] = "value1"
        doc["key2"] = "value2"

        # navigate only works with tables, not simple values
        result = strategy.navigate(doc, ["key1"])
        assert result is None  # key1 is a string, not a table

        result = strategy.navigate(doc, ["key2"])
        assert result is None  # key2 is a string, not a table

    def test_toml_strategy_navigate_nested_toml_document(self) -> None:
        """
        Scenario: Navigate through nested TOML document structure

        Expected:
        - Should return table at nested path
        - Should handle multi-level navigation correctly
        - Should work with nested tables
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["level1"] = table()
        doc["level1"]["level2"] = table()
        doc["level1"]["level2"]["level3"] = "deep_value"

        # navigate returns the table, not the value
        result = strategy.navigate(doc, ["level1", "level2"])
        assert isinstance(result, Table)
        assert result["level3"] == "deep_value"

    def test_toml_strategy_navigate_nonexistent_path_without_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist without create flag

        Expected:
        - Should return None when path doesn't exist
        - Should not modify the original document
        - Should handle missing keys gracefully
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["key1"] = "value1"

        result = strategy.navigate(doc, ["nonexistent"])
        assert result is None

        result = strategy.navigate(doc, ["key1", "nonexistent"])
        assert result is None

    def test_toml_strategy_navigate_nonexistent_path_with_create(self) -> None:
        """
        Scenario: Navigate to path that doesn't exist with create flag enabled

        Expected:
        - Should create intermediate tables
        - Should return the created empty table
        - Should modify the original document
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["key1"] = "value1"

        result = strategy.navigate(doc, ["new", "nested"], create=True)
        assert isinstance(result, Table)
        assert isinstance(doc["new"], Table)
        assert isinstance(doc["new"]["nested"], Table)

    def test_toml_strategy_navigate_empty_path(self) -> None:
        """
        Scenario: Navigate with empty path list

        Expected:
        - Should return the original document
        - Should not modify the original document
        - Should handle empty path gracefully
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["key"] = "value"

        result = strategy.navigate(doc, [])
        assert result == doc

    def test_toml_strategy_round_trip_consistency(self, tmp_path: Path) -> None:
        """
        Scenario: Test load-save-load round trip consistency

        Expected:
        - Data should remain unchanged after save-load cycle
        - Should preserve all data types and structures
        - Should maintain TOML formatting consistency
        """
        strategy = TomlStrategy()

        # Create original document
        original_doc = TOMLDocument()
        original_doc["string"] = "test"
        original_doc["number"] = 42
        original_doc["boolean"] = True
        original_doc["array"] = [1, 2, 3]

        # Add nested table
        original_doc["nested"] = table()
        original_doc["nested"]["key"] = "value"
        original_doc["nested"]["list"] = ["a", "b", "c"]

        file_path = tmp_path / "round_trip.toml"

        # Save data
        strategy.save(file_path, original_doc)

        # Load data back
        loaded_doc = strategy.load(file_path)

        # Compare key values (exact structure comparison may vary due to TOML formatting)
        assert loaded_doc["string"] == original_doc["string"]
        assert loaded_doc["number"] == original_doc["number"]
        assert loaded_doc["boolean"] == original_doc["boolean"]
        assert loaded_doc["array"] == original_doc["array"]
        assert loaded_doc["nested"]["key"] == original_doc["nested"]["key"]
        assert loaded_doc["nested"]["list"] == original_doc["nested"]["list"]

    def test_toml_strategy_with_special_characters(self, tmp_path: Path) -> None:
        """
        Scenario: Test TOML strategy with special characters and Unicode

        Expected:
        - Should handle special characters correctly
        - Should preserve Unicode characters
        - Should maintain encoding consistency
        """
        strategy = TomlStrategy()
        doc = TOMLDocument()
        doc["unicode"] = "café naïve résumé"
        doc["emoji"] = "🚀 🎉 ✨"
        doc["special_chars"] = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        doc["chinese"] = "你好世界"
        doc["arabic"] = "مرحبا بالعالم"

        file_path = tmp_path / "special_chars.toml"

        strategy.save(file_path, doc)
        loaded_doc = strategy.load(file_path)

        assert loaded_doc["unicode"] == doc["unicode"]
        assert loaded_doc["emoji"] == doc["emoji"]
        assert loaded_doc["special_chars"] == doc["special_chars"]
        assert loaded_doc["chinese"] == doc["chinese"]
        assert loaded_doc["arabic"] == doc["arabic"]

    def test_toml_strategy_error_handling_integration(self, tmp_path: Path) -> None:
        """
        Scenario: Test TOML strategy error handling integration

        Expected:
        - Should handle various error conditions gracefully
        - Should provide meaningful error messages
        - Should not crash on invalid operations
        """
        strategy = TomlStrategy()

        # Test with invalid file path
        with pytest.raises(FileReadError):
            strategy.load(Path("nonexistent.toml"))

        # Test with invalid TOML content
        invalid_file = tmp_path / "invalid.toml"
        invalid_file.write_text("invalid toml [unclosed", encoding="utf-8")

        with pytest.raises(Exception):  # tomlkit raises various exceptions
            strategy.load(invalid_file)

        # Test with valid operations after errors
        valid_doc = TOMLDocument()
        valid_doc["recovery"] = "test"
        valid_file = tmp_path / "valid.toml"
        strategy.save(valid_file, valid_doc)

        loaded_doc = strategy.load(valid_file)
        assert loaded_doc["recovery"] == "test"

    def test_toml_strategy_with_complex_nested_structure(self, tmp_path: Path) -> None:
        """
        Scenario: Test TOML strategy with complex nested structure

        Expected:
        - Should handle deeply nested tables
        - Should preserve complex data structures
        - Should maintain navigation functionality
        """
        strategy = TomlStrategy()

        # Create complex nested structure
        doc = TOMLDocument()
        doc["app"] = table()
        doc["app"]["name"] = "Test App"
        doc["app"]["version"] = "1.0.0"

        doc["app"]["database"] = table()
        doc["app"]["database"]["host"] = "localhost"
        doc["app"]["database"]["port"] = 5432

        doc["app"]["database"]["credentials"] = table()
        doc["app"]["database"]["credentials"]["username"] = "admin"
        doc["app"]["database"]["credentials"]["password"] = "secret"

        doc["app"]["features"] = table()
        doc["app"]["features"]["enabled"] = ["auth", "logging", "caching"]
        doc["app"]["features"]["disabled"] = ["debug", "profiling"]

        file_path = tmp_path / "complex.toml"

        # Save and load
        strategy.save(file_path, doc)
        loaded_doc = strategy.load(file_path)

        # Test navigation - navigate returns tables, not values
        app_table = strategy.navigate(loaded_doc, ["app"])
        assert isinstance(app_table, Table)
        assert app_table["name"] == "Test App"

        db_table = strategy.navigate(loaded_doc, ["app", "database"])
        assert isinstance(db_table, Table)
        assert db_table["host"] == "localhost"

        credentials_table = strategy.navigate(
            loaded_doc, ["app", "database", "credentials"]
        )
        assert isinstance(credentials_table, Table)
        assert credentials_table["username"] == "admin"

        features_table = strategy.navigate(loaded_doc, ["app", "features"])
        assert isinstance(features_table, Table)
        assert features_table["enabled"] == ["auth", "logging", "caching"]
