"""
Unit tests for dict_utils module.
"""

from typing import Any, Dict, List, cast

from yapfm.helpers.dict_utils import deep_merge, navigate_dict_like


class TestNavigateDictLike:
    """Test cases for navigate_dict_like function."""

    def test_navigate_simple_dict_path(self) -> None:
        """
        Scenario: Navigate through a simple dictionary with a valid path

        Expected:
        - Should return the value at the specified path
        - Should handle single-level navigation correctly
        """
        document = {"key1": "value1", "key2": {"nested": "nested_value"}}
        result = navigate_dict_like(document, ["key1"])
        assert result == "value1"

    def test_navigate_nested_dict_path(self) -> None:
        """
        Scenario: Navigate through a nested dictionary structure

        Expected:
        - Should return the value at the nested path
        - Should handle multi-level navigation correctly
        """
        document = {"level1": {"level2": {"level3": "deep_value"}}}
        result = navigate_dict_like(document, ["level1", "level2", "level3"])
        assert result == "deep_value"

    def test_navigate_nonexistent_path_without_create(self) -> None:
        """
        Scenario: Navigate to a path that doesn't exist without create flag

        Expected:
        - Should return None when path doesn't exist
        - Should not modify the original document
        """
        document = {"key1": "value1"}
        result = navigate_dict_like(document, ["nonexistent"])
        assert result is None
        assert "nonexistent" not in document

    def test_navigate_nonexistent_path_with_create(self) -> None:
        """
        Scenario: Navigate to a path that doesn't exist with create flag enabled

        Expected:
        - Should create intermediate dictionaries
        - Should return the created empty dictionary
        - Should modify the original document
        """
        document: Dict[str, Any] = {"key1": "value1"}
        result = navigate_dict_like(document, ["new", "nested"], create=True)
        assert isinstance(result, dict)
        # mypy friendly
        nested_dict = cast(Dict[str, Any], document["new"])
        assert nested_dict["nested"] == result
        # mypy friendly
        nested_dict = cast(Dict[str, Any], document["new"])
        assert nested_dict["nested"] == result

    def test_navigate_list_with_valid_index(self) -> None:
        """
        Scenario: Navigate through a list using valid numeric index

        Expected:
        - Should return the element at the specified index
        - Should handle list navigation correctly
        """
        document = {"items": ["first", "second", "third"]}
        result = navigate_dict_like(document, ["items", "1"])
        assert result == "second"

    def test_navigate_list_with_invalid_index(self) -> None:
        """
        Scenario: Navigate through a list using invalid non-numeric index

        Expected:
        - Should return None for non-numeric indices
        - Should not modify the original document
        """
        document = {"items": ["first", "second", "third"]}
        result = navigate_dict_like(document, ["items", "invalid"])
        assert result is None

    def test_navigate_list_with_out_of_bounds_index_without_create(self) -> None:
        """
        Scenario: Navigate to list index that's out of bounds without create flag

        Expected:
        - Should return None for out-of-bounds indices
        - Should not modify the original list
        """
        document = {"items": ["first"]}
        result = navigate_dict_like(document, ["items", "5"])
        assert result is None
        assert len(document["items"]) == 1

    def test_navigate_list_with_out_of_bounds_index_with_create(self) -> None:
        """
        Scenario: Navigate to list index that's out of bounds with create flag

        Expected:
        - Should extend the list with empty dictionaries
        - Should return the created empty dictionary
        - Should modify the original list
        """
        document = {"items": ["first"]}
        result = navigate_dict_like(document, ["items", "2"], create=True)
        assert isinstance(result, dict)
        assert len(document["items"]) == 3
        assert document["items"][2] == result

    def test_navigate_with_custom_create_function(self) -> None:
        """
        Scenario: Navigate with a custom function to create new containers

        Expected:
        - Should use the custom function to create new containers
        - Should return the created container
        - Should modify the original document
        """
        document: Dict[str, Any] = {}

        def create_list() -> List[Any]:
            return []

        result = navigate_dict_like(
            document, ["new", "0"], create=True, create_dict_func=create_list
        )
        assert isinstance(result, list)
        assert isinstance(document["new"], list)

    def test_navigate_non_dict_non_list_node(self) -> None:
        """
        Scenario: Navigate when current node is neither dict nor list

        Expected:
        - Should return None when trying to navigate from non-container type
        - Should not modify the original document
        """
        document: Dict[str, Any] = {"key": "string_value"}
        result = navigate_dict_like(document, ["key", "subkey"])
        assert result is None

    def test_navigate_empty_path(self) -> None:
        """
        Scenario: Navigate with an empty path list

        Expected:
        - Should return the original document
        - Should not modify the original document
        """
        document = {"key": "value"}
        result = navigate_dict_like(document, [])
        assert result == document


class TestDeepMerge:
    """Test cases for deep_merge function."""

    def test_merge_simple_dictionaries(self) -> None:
        """
        Scenario: Merge two simple dictionaries with no nested structures

        Expected:
        - Should merge all keys from new dict into base dict
        - Should overwrite existing keys by default
        - Should return the modified base dictionary
        """
        base = {"key1": "value1", "key2": "value2"}
        new = {"key2": "new_value2", "key3": "value3"}
        result = deep_merge(base, new)

        assert result == base  # Should modify base in place
        assert base["key1"] == "value1"
        assert base["key2"] == "new_value2"  # Overwritten
        assert base["key3"] == "value3"  # Added

    def test_merge_nested_dictionaries(self) -> None:
        """
        Scenario: Merge dictionaries with nested structures

        Expected:
        - Should recursively merge nested dictionaries
        - Should preserve existing nested values when merging
        - Should add new nested keys
        """
        base = {"level1": {"nested1": "value1", "nested2": "value2"}}
        new = {"level1": {"nested2": "new_value2", "nested3": "value3"}}
        result = deep_merge(base, new)

        assert result == base
        assert base["level1"]["nested1"] == "value1"  # Preserved
        assert base["level1"]["nested2"] == "new_value2"  # Overwritten
        assert base["level1"]["nested3"] == "value3"  # Added

    def test_merge_with_overwrite_false(self) -> None:
        """
        Scenario: Merge dictionaries with overwrite=False

        Expected:
        - Should not overwrite existing keys
        - Should only add new keys that don't exist in base
        - Should preserve all existing values
        """
        base = {"key1": "original", "key2": "original2"}
        new = {"key1": "new_value", "key2": "new_value2", "key3": "new_value3"}
        result = deep_merge(base, new, overwrite=False)

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
        base = {"level1": {"nested1": "original", "nested2": "original2"}}
        new = {
            "level1": {
                "nested1": "new_value",
                "nested2": "new_value2",
                "nested3": "new_value3",
            }
        }
        result = deep_merge(base, new, overwrite=False)

        assert result == base
        assert base["level1"]["nested1"] == "original"  # Not overwritten
        assert base["level1"]["nested2"] == "original2"  # Not overwritten
        assert base["level1"]["nested3"] == "new_value3"  # Added

    def test_merge_with_non_dict_values(self) -> None:
        """
        Scenario: Merge when new value is not a dictionary

        Expected:
        - Should overwrite the base value with the new value
        - Should handle non-dict values correctly
        """
        base = {"key1": {"nested": "value"}}
        new = {"key1": "string_value"}
        result = deep_merge(base, new)

        assert result == base
        assert base["key1"] == "string_value"

    def test_merge_with_missing_nested_key_in_base(self) -> None:
        """
        Scenario: Merge when base doesn't have the nested key

        Expected:
        - Should create the nested structure in base
        - Should add all nested values from new dict
        """
        base: Dict[str, Any] = {"key1": "value1"}
        new: Dict[str, Any] = {"key2": {"nested1": "value1", "nested2": "value2"}}
        result = deep_merge(base, new)

        assert result == base
        assert base["key1"] == "value1"  # Preserved
        assert base["key2"]["nested1"] == "value1"  # Added
        assert base["key2"]["nested2"] == "value2"  # Added

    def test_merge_empty_dictionaries(self) -> None:
        """
        Scenario: Merge empty dictionaries

        Expected:
        - Should return the base dictionary unchanged
        - Should handle empty new dictionary gracefully
        """
        base = {"key1": "value1"}
        new: Dict[str, Any] = {}
        result = deep_merge(base, new)

        assert result == base
        assert base == {"key1": "value1"}

    def test_merge_empty_base_dictionary(self) -> None:
        """
        Scenario: Merge into an empty base dictionary

        Expected:
        - Should add all keys from new dictionary to base
        - Should return the modified base dictionary
        """
        base: Dict[str, Any] = {}
        new: Dict[str, Any] = {"key1": "value1", "key2": {"nested": "value"}}
        result = deep_merge(base, new)

        assert result == base
        assert base == new

    def test_merge_deeply_nested_structures(self) -> None:
        """
        Scenario: Merge deeply nested dictionary structures

        Expected:
        - Should handle multiple levels of nesting correctly
        - Should preserve existing values at all levels
        - Should add new values at all levels
        """
        base = {
            "level1": {
                "level2": {"level3": {"existing": "value", "to_keep": "keep_this"}}
            }
        }
        new = {
            "level1": {
                "level2": {
                    "level3": {"existing": "new_value", "new_key": "new_value"},
                    "new_level2": "value",
                }
            }
        }
        result = deep_merge(base, new)

        assert result == base
        assert base["level1"]["level2"]["level3"]["existing"] == "new_value"
        assert base["level1"]["level2"]["level3"]["to_keep"] == "keep_this"
        assert base["level1"]["level2"]["level3"]["new_key"] == "new_value"
        assert base["level1"]["level2"]["new_level2"] == "value"
