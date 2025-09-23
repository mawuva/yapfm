"""
Tests for AppendMergeStrategy.

This module contains tests for the append merge strategy that merges files by appending values to lists.
"""

# mypy: ignore-errors

from pathlib import Path

import pytest

from yapfm.multi_file.merge_strategies.append import AppendMergeStrategy


class TestAppendMergeStrategy:
    """Test cases for AppendMergeStrategy."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        strategy = AppendMergeStrategy()

        assert strategy.create_lists_for_singles is True
        assert strategy.options == {"create_lists_for_singles": True}

    def test_init_with_create_lists_false(self):
        """Test initialization with create_lists_for_singles=False."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        assert strategy.create_lists_for_singles is False
        assert strategy.options == {"create_lists_for_singles": False}

    def test_get_name(self):
        """Test get_name method."""
        strategy = AppendMergeStrategy()

        assert strategy.get_name() == "append"

    def test_get_description(self):
        """Test get_description method."""
        strategy = AppendMergeStrategy()

        description = strategy.get_description()
        assert "Merges files by appending values to lists" in description

    def test_get_optional_options(self):
        """Test get_optional_options method."""
        strategy = AppendMergeStrategy()

        options = strategy.get_optional_options()
        assert options == {"create_lists_for_singles": True}

    def test_validate_options_valid(self):
        """Test validate_options with valid options."""
        strategy = AppendMergeStrategy()

        validated = strategy.validate_options(create_lists_for_singles=False)
        assert validated == {"create_lists_for_singles": False}

    def test_validate_options_invalid_type(self):
        """Test validate_options with invalid option type."""
        strategy = AppendMergeStrategy()

        with pytest.raises(
            ValueError, match="create_lists_for_singles must be a boolean"
        ):
            strategy.validate_options(create_lists_for_singles="invalid")

    def test_merge_empty_files(self):
        """Test merge with empty file list."""
        strategy = AppendMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merge with single file."""
        strategy = AppendMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"key": ["value"]}

    def test_merge_with_existing_lists(self):
        """Test merge with existing lists."""
        strategy = AppendMergeStrategy()

        files = [
            (Path("file1.json"), {"items": ["a", "b"]}),
            (Path("file2.json"), {"items": ["c", "d"]}),
        ]
        result = strategy.merge(files)

        assert result == {"items": ["a", "b", "c", "d"]}

    def test_merge_mixed_lists_and_singles(self):
        """Test merge with mixed lists and single values."""
        strategy = AppendMergeStrategy()

        files = [
            (Path("file1.json"), {"items": ["a", "b"], "value": "single"}),
            (Path("file2.json"), {"items": ["c"], "value": "another"}),
        ]
        result = strategy.merge(files)

        assert result == {"items": ["a", "b", "c"], "value": ["single", "another"]}

    def test_merge_with_create_lists_for_singles_true(self):
        """Test merge with create_lists_for_singles=True (default)."""
        strategy = AppendMergeStrategy(create_lists_for_singles=True)

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
        ]
        result = strategy.merge(files)

        assert result == {"key1": ["value1"], "key2": ["value2"]}

    def test_merge_with_create_lists_for_singles_false(self):
        """Test merge with create_lists_for_singles=False."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
        ]
        result = strategy.merge(files)

        assert result == {"key1": "value1", "key2": "value2"}

    def test_merge_list_to_single_value(self):
        """Test merge when first file has list and second has single value."""
        strategy = AppendMergeStrategy()

        files = [
            (Path("file1.json"), {"items": ["a", "b"]}),
            (Path("file2.json"), {"items": "c"}),
        ]
        result = strategy.merge(files)

        assert result == {"items": ["a", "b", "c"]}

    def test_merge_single_value_to_list(self):
        """Test merge when first file has single value and second has list."""
        strategy = AppendMergeStrategy()

        files = [
            (Path("file1.json"), {"items": "a"}),
            (Path("file2.json"), {"items": ["b", "c"]}),
        ]
        result = strategy.merge(files)

        assert result == {"items": ["a", "b", "c"]}

    def test_merge_single_to_single(self):
        """Test merge when both files have single values."""
        strategy = AppendMergeStrategy()

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
        ]
        result = strategy.merge(files)

        assert result == {"key": ["value1", "value2"]}

    def test_merge_with_create_lists_false_single_to_single(self):
        """Test merge single to single with create_lists_for_singles=False."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
        ]
        result = strategy.merge(files)

        # Should create list when merging single values
        assert result == {"key": ["value1", "value2"]}

    def test_merge_with_nested_data(self):
        """Test merge with nested data structures."""
        strategy = AppendMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {"config": {"features": ["auth", "logging"], "debug": True}},
            ),
            (Path("file2.json"), {"config": {"features": ["caching"], "debug": False}}),
        ]
        result = strategy.merge(files)

        # Nested structures are not merged, only top-level keys
        assert result == {
            "config": [
                {"features": ["auth", "logging"], "debug": True},
                {"features": ["caching"], "debug": False},
            ]
        }

    def test_merge_with_mixed_data_types(self):
        """Test merge with mixed data types."""
        strategy = AppendMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {
                    "string": "value1",
                    "number": 42,
                    "boolean": True,
                    "list": [1, 2, 3],
                    "null": None,
                },
            ),
            (
                Path("file2.json"),
                {
                    "string": "value2",
                    "number": 100,
                    "boolean": False,
                    "list": [4, 5, 6],
                    "null": "not_null",
                },
            ),
        ]
        result = strategy.merge(files)

        assert result == {
            "string": ["value1", "value2"],
            "number": [42, 100],
            "boolean": [True, False],
            "list": [1, 2, 3, 4, 5, 6],
            "null": [None, "not_null"],
        }

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = AppendMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, test_kwarg="test_value")

        assert result == {"key": ["value"]}

    def test_get_merge_info(self):
        """Test get_merge_info method."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "append"
        assert info["create_lists_for_singles"] is False
        assert info["merge_type"] == "append_to_lists"
        assert info["file_count"] == 2
        assert info["files"] == ["file1.json", "file2.json"]

    def test_str_representation(self):
        """Test string representation."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        assert str(strategy) == "AppendMergeStrategy(append)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = AppendMergeStrategy(create_lists_for_singles=False)

        expected = "AppendMergeStrategy(name='append', options={'create_lists_for_singles': False})"
        assert repr(strategy) == expected
