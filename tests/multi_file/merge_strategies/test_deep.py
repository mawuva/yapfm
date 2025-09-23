"""
Tests for DeepMergeStrategy.

This module contains tests for the deep merge strategy that recursively merges dictionaries.
"""

# mypy: ignore-errors

from pathlib import Path

import pytest

from yapfm.multi_file.merge_strategies.deep import DeepMergeStrategy


class TestDeepMergeStrategy:
    """Test cases for DeepMergeStrategy."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        strategy = DeepMergeStrategy()

        assert strategy.overwrite is True
        assert strategy.options == {"overwrite": True}

    def test_init_with_overwrite_false(self):
        """Test initialization with overwrite=False."""
        strategy = DeepMergeStrategy(overwrite=False)

        assert strategy.overwrite is False
        assert strategy.options == {"overwrite": False}

    def test_get_name(self):
        """Test get_name method."""
        strategy = DeepMergeStrategy()

        assert strategy.get_name() == "deep"

    def test_get_description(self):
        """Test get_description method."""
        strategy = DeepMergeStrategy()

        description = strategy.get_description()
        assert "Recursively merges nested dictionaries" in description

    def test_get_optional_options(self):
        """Test get_optional_options method."""
        strategy = DeepMergeStrategy()

        options = strategy.get_optional_options()
        assert options == {"overwrite": True}

    def test_validate_options_valid(self):
        """Test validate_options with valid options."""
        strategy = DeepMergeStrategy()

        validated = strategy.validate_options(overwrite=False)
        assert validated == {"overwrite": False}

    def test_validate_options_invalid_type(self):
        """Test validate_options with invalid option type."""
        strategy = DeepMergeStrategy()

        with pytest.raises(ValueError, match="overwrite option must be a boolean"):
            strategy.validate_options(overwrite="invalid")

    def test_merge_empty_files(self):
        """Test merge with empty file list."""
        strategy = DeepMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merge with single file."""
        strategy = DeepMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"key": "value"}

    def test_merge_flat_dictionaries(self):
        """Test merge with flat dictionaries."""
        strategy = DeepMergeStrategy()

        files = [
            (Path("file1.json"), {"key1": "value1", "key2": "value2"}),
            (Path("file2.json"), {"key3": "value3"}),
        ]
        result = strategy.merge(files)

        expected = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert result == expected

    def test_merge_nested_dictionaries(self):
        """Test merge with nested dictionaries."""
        strategy = DeepMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {
                    "database": {"host": "localhost", "port": 5432},
                    "app": {"name": "MyApp"},
                },
            ),
            (
                Path("file2.json"),
                {"database": {"password": "secret"}, "app": {"debug": True}},
            ),
        ]
        result = strategy.merge(files)

        expected = {
            "database": {"host": "localhost", "port": 5432, "password": "secret"},
            "app": {"name": "MyApp", "debug": True},
        }
        assert result == expected

    def test_merge_with_overwrite_true(self):
        """Test merge with overwrite=True (default)."""
        strategy = DeepMergeStrategy(overwrite=True)

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
        ]
        result = strategy.merge(files)

        # Last file should overwrite
        assert result == {"key": "value2"}

    def test_merge_with_overwrite_false(self):
        """Test merge with overwrite=False."""
        strategy = DeepMergeStrategy(overwrite=False)

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
        ]
        result = strategy.merge(files)

        # First file should be preserved
        assert result == {"key": "value1"}

    def test_merge_deeply_nested(self):
        """Test merge with deeply nested dictionaries."""
        strategy = DeepMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {"level1": {"level2": {"level3": {"key1": "value1"}}}},
            ),
            (
                Path("file2.json"),
                {"level1": {"level2": {"level3": {"key2": "value2"}}}},
            ),
        ]
        result = strategy.merge(files)

        expected = {
            "level1": {"level2": {"level3": {"key1": "value1", "key2": "value2"}}}
        }
        assert result == expected

    def test_merge_mixed_types(self):
        """Test merge with mixed data types."""
        strategy = DeepMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {
                    "string": "value",
                    "number": 42,
                    "boolean": True,
                    "list": [1, 2, 3],
                    "null": None,
                },
            ),
            (
                Path("file2.json"),
                {"string": "updated", "number": 100, "list": [4, 5, 6]},
            ),
        ]
        result = strategy.merge(files)

        expected = {
            "string": "updated",
            "number": 100,
            "boolean": True,
            "list": [4, 5, 6],
            "null": None,
        }
        assert result == expected

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = DeepMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, test_kwarg="test_value")

        assert result == {"key": "value"}

    def test_get_merge_info(self):
        """Test get_merge_info method."""
        strategy = DeepMergeStrategy(overwrite=False)

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "deep"
        assert info["overwrite"] is False
        assert info["merge_type"] == "recursive_deep"
        assert info["file_count"] == 2
        assert info["files"] == ["file1.json", "file2.json"]

    def test_str_representation(self):
        """Test string representation."""
        strategy = DeepMergeStrategy(overwrite=False)

        assert str(strategy) == "DeepMergeStrategy(deep)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = DeepMergeStrategy(overwrite=False)

        expected = "DeepMergeStrategy(name='deep', options={'overwrite': False})"
        assert repr(strategy) == expected
