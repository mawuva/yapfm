"""
Unit tests for toml_merger module.
"""

from typing import Any, Dict, Mapping

from tomlkit import TOMLDocument, table
from tomlkit.items import Table

from yapfm.helpers.toml_merger import merge_toml


class TestMergeToml:
    """Test cases for merge_toml function."""

    def test_merge_simple_values_into_toml_document(self) -> None:
        """
        Scenario: Merge simple key-value pairs into a TOMLDocument

        Expected:
        - Should add new keys to the TOML document
        - Should overwrite existing keys by default
        - Should return the modified TOML document
        """
        base = TOMLDocument()
        base["existing_key"] = "existing_value"

        new = {"existing_key": "new_value", "new_key": "new_value"}
        result = merge_toml(base, new)

        assert result == base  # Should modify base in place
        assert base["existing_key"] == "new_value"  # Overwritten
        assert base["new_key"] == "new_value"  # Added

    def test_merge_simple_values_into_table(self) -> None:
        """
        Scenario: Merge simple key-value pairs into a Table

        Expected:
        - Should add new keys to the Table
        - Should overwrite existing keys by default
        - Should return the modified Table
        """
        base = table()
        base["existing_key"] = "existing_value"

        new = {"existing_key": "new_value", "new_key": "new_value"}
        result = merge_toml(base, new)

        assert result == base  # Should modify base in place
        assert base["existing_key"] == "new_value"  # Overwritten
        assert base["new_key"] == "new_value"  # Added

    def test_merge_nested_dictionaries_into_toml_document(self) -> None:
        """
        Scenario: Merge nested dictionaries into a TOMLDocument

        Expected:
        - Should create nested Table structures
        - Should recursively merge nested dictionaries
        - Should preserve existing nested values when merging
        """
        base = TOMLDocument()
        base["level1"] = table()
        base["level1"]["existing"] = "value"

        new = {
            "level1": {"existing": "new_value", "new_nested": "value"},
            "level2": {"nested": "value"},
        }
        result = merge_toml(base, new)

        assert result == base
        assert base["level1"]["existing"] == "new_value"  # Overwritten
        assert base["level1"]["new_nested"] == "value"  # Added
        assert base["level2"]["nested"] == "value"  # Added

    def test_merge_nested_dictionaries_into_table(self) -> None:
        """
        Scenario: Merge nested dictionaries into a Table

        Expected:
        - Should create nested Table structures
        - Should recursively merge nested dictionaries
        - Should handle Table-to-Table merging correctly
        """
        base = table()
        base["level1"] = table()
        base["level1"]["existing"] = "value"

        new = {"level1": {"existing": "new_value", "new_nested": "value"}}
        result = merge_toml(base, new)

        assert result == base
        assert base["level1"]["existing"] == "new_value"  # Overwritten
        assert base["level1"]["new_nested"] == "value"  # Added

    def test_merge_with_overwrite_false(self) -> None:
        """
        Scenario: Merge with overwrite=False

        Expected:
        - Should not overwrite existing keys
        - Should only add new keys that don't exist
        - Should preserve all existing values
        """
        base = TOMLDocument()
        base["key1"] = "original"
        base["key2"] = "original2"

        new = {"key1": "new_value", "key2": "new_value2", "key3": "new_value3"}
        result = merge_toml(base, new, overwrite=False)

        assert result == base
        assert base["key1"] == "original"  # Not overwritten
        assert base["key2"] == "original2"  # Not overwritten
        assert base["key3"] == "new_value3"  # Added

    def test_merge_nested_with_overwrite_false(self) -> None:
        """
        Scenario: Merge nested dictionaries with overwrite=False

        Expected:
        - Should recursively apply overwrite=False to nested levels
        - Should preserve existing nested values
        - Should add new nested keys
        """
        base = TOMLDocument()
        base["level1"] = table()
        base["level1"]["nested1"] = "original"
        base["level1"]["nested2"] = "original2"

        new = {
            "level1": {
                "nested1": "new_value",
                "nested2": "new_value2",
                "nested3": "new_value3",
            }
        }
        result = merge_toml(base, new, overwrite=False)

        assert result == base
        assert base["level1"]["nested1"] == "original"  # Not overwritten
        assert base["level1"]["nested2"] == "original2"  # Not overwritten
        assert base["level1"]["nested3"] == "new_value3"  # Added

    def test_merge_with_none_values(self) -> None:
        """
        Scenario: Merge with None values in the new dictionary

        Expected:
        - Should create empty Table for None values when key exists
        - Should handle None values correctly
        - Should not overwrite existing values with None
        """
        base = TOMLDocument()
        base["existing_key"] = "existing_value"

        new = {"existing_key": None, "new_key": None}
        result = merge_toml(base, new, overwrite=False)

        assert result == base
        assert base["existing_key"] == "existing_value"  # Not overwritten
        assert isinstance(base["new_key"], Table)  # Created as empty table

    def test_merge_with_none_values_overwrite_true(self) -> None:
        """
        Scenario: Merge with None values and overwrite=True

        Expected:
        - Should overwrite existing values with None (creating empty table)
        - Should create empty tables for new None values
        - Should handle None values with overwrite correctly
        """
        base = TOMLDocument()
        base["existing_key"] = "existing_value"

        new = {"existing_key": None, "new_key": None}
        result = merge_toml(base, new, overwrite=True)

        assert result == base
        assert isinstance(base["existing_key"], Table)  # Overwritten with empty table
        assert isinstance(base["new_key"], Table)  # Created as empty table

    def test_merge_with_non_dict_values(self) -> None:
        """
        Scenario: Merge when new value is not a dictionary

        Expected:
        - Should overwrite the base value with the new value
        - Should handle non-dict values correctly
        - Should not create nested structures for non-dict values
        """
        base = TOMLDocument()
        base["key1"] = table()
        base["key1"]["nested"] = "value"

        new = {"key1": "string_value"}
        result = merge_toml(base, new)

        assert result == base
        assert base["key1"] == "string_value"

    def test_merge_with_missing_nested_key_in_base(self) -> None:
        """
        Scenario: Merge when base doesn't have the nested key

        Expected:
        - Should create the nested Table structure in base
        - Should add all nested values from new dict
        - Should handle missing nested keys gracefully
        """
        base = TOMLDocument()
        base["key1"] = "value1"

        new = {"key2": {"nested1": "value1", "nested2": "value2"}}
        result = merge_toml(base, new)

        assert result == base
        assert base["key1"] == "value1"  # Preserved
        assert isinstance(base["key2"], Table)  # Created as table
        assert base["key2"]["nested1"] == "value1"  # Added
        assert base["key2"]["nested2"] == "value2"  # Added

    def test_merge_with_existing_non_table_value(self) -> None:
        """
        Scenario: Merge when base has a non-table value at the key

        Expected:
        - Should replace the non-table value with a new table
        - Should add nested values to the new table
        - Should handle type conversion correctly
        """
        base = TOMLDocument()
        base["key1"] = "string_value"

        new = {"key1": {"nested": "value"}}
        result = merge_toml(base, new)

        assert result == base
        assert isinstance(base["key1"], Table)  # Replaced with table
        assert base["key1"]["nested"] == "value"  # Added

    def test_merge_empty_dictionaries(self) -> None:
        """
        Scenario: Merge empty dictionaries

        Expected:
        - Should return the base TOML document unchanged
        - Should handle empty new dictionary gracefully
        - Should not modify the base document
        """
        base = TOMLDocument()
        base["key1"] = "value1"

        new: Dict[str, Any] = {}
        result = merge_toml(base, new)

        assert result == base
        assert base["key1"] == "value1"

    def test_merge_empty_base_toml_document(self) -> None:
        """
        Scenario: Merge into an empty TOML document

        Expected:
        - Should add all keys from new dictionary to base
        - Should return the modified base document
        - Should handle empty base gracefully
        """
        base = TOMLDocument()
        new: Dict[str, Any] = {"key1": "value1", "key2": {"nested": "value"}}
        result = merge_toml(base, new)

        assert result == base
        assert base["key1"] == "value1"
        assert isinstance(base["key2"], Table)
        assert base["key2"]["nested"] == "value"

    def test_merge_deeply_nested_structures(self) -> None:
        """
        Scenario: Merge deeply nested dictionary structures

        Expected:
        - Should handle multiple levels of nesting correctly
        - Should preserve existing values at all levels
        - Should add new values at all levels
        """
        base = TOMLDocument()
        base["level1"] = table()
        base["level1"]["level2"] = table()
        base["level1"]["level2"]["level3"] = table()
        base["level1"]["level2"]["level3"]["existing"] = "value"
        base["level1"]["level2"]["level3"]["to_keep"] = "keep_this"

        new = {
            "level1": {
                "level2": {
                    "level3": {"existing": "new_value", "new_key": "new_value"},
                    "new_level2": "value",
                }
            }
        }
        result = merge_toml(base, new)

        assert result == base
        assert base["level1"]["level2"]["level3"]["existing"] == "new_value"
        assert base["level1"]["level2"]["level3"]["to_keep"] == "keep_this"
        assert base["level1"]["level2"]["level3"]["new_key"] == "new_value"
        assert base["level1"]["level2"]["new_level2"] == "value"

    def test_merge_with_mapping_interface(self) -> None:
        """
        Scenario: Merge using a Mapping interface instead of dict

        Expected:
        - Should work with any Mapping-like object
        - Should iterate over the mapping correctly
        - Should handle non-dict mapping types
        """
        base = TOMLDocument()

        class CustomMapping(Mapping[str, Any]):
            def __init__(self, data: Dict[str, Any]) -> None:
                self._data = data

            def items(self) -> Any:
                return self._data.items()

            def __getitem__(self, key: str) -> Any:
                return self._data[key]

            def __iter__(self) -> Any:
                return iter(self._data)

            def __len__(self) -> int:
                return len(self._data)

        new_mapping: Mapping[str, Any] = CustomMapping(
            {"key1": "value1", "key2": {"nested": "value"}}
        )
        result = merge_toml(base, new_mapping)

        assert result == base
        assert base["key1"] == "value1"
        assert isinstance(base["key2"], Table)
        assert base["key2"]["nested"] == "value"

    def test_merge_preserves_toml_document_type(self) -> None:
        """
        Scenario: Merge preserves the original TOML document type

        Expected:
        - Should return the same type as the input base
        - Should maintain TOML document structure
        - Should preserve TOML-specific features
        """
        base = TOMLDocument()
        new = {"key": "value"}
        result = merge_toml(base, new)

        assert isinstance(result, TOMLDocument)
        assert result is base

    def test_merge_preserves_table_type(self) -> None:
        """
        Scenario: Merge preserves the original Table type

        Expected:
        - Should return the same type as the input base
        - Should maintain Table structure
        - Should preserve Table-specific features
        """
        base = table()
        new = {"key": "value"}
        result = merge_toml(base, new)

        assert isinstance(result, Table)
        assert result is base
