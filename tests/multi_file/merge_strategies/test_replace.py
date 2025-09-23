"""
Tests for ReplaceMergeStrategy.

This module contains tests for the replace merge strategy that completely replaces
the result with the last file's data.
"""

# mypy: ignore-errors

from pathlib import Path

from yapfm.multi_file.merge_strategies.replace import ReplaceMergeStrategy


class TestReplaceMergeStrategy:
    """Test cases for ReplaceMergeStrategy."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        strategy = ReplaceMergeStrategy()

        assert strategy.options == {}

    def test_init_with_options(self):
        """Test initialization with options."""
        strategy = ReplaceMergeStrategy(test_option=True, another_option="value")

        assert strategy.options == {"test_option": True, "another_option": "value"}

    def test_get_name(self):
        """Test get_name method."""
        strategy = ReplaceMergeStrategy()

        assert strategy.get_name() == "replace"

    def test_get_description(self):
        """Test get_description method."""
        strategy = ReplaceMergeStrategy()

        description = strategy.get_description()
        assert (
            "Merges files by completely replacing with the last file's data"
            in description
        )

    def test_merge_empty_files(self):
        """Test merge with empty file list."""
        strategy = ReplaceMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merge with single file."""
        strategy = ReplaceMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"key": "value"}

    def test_merge_multiple_files(self):
        """Test merge with multiple files."""
        strategy = ReplaceMergeStrategy()

        files = [
            (Path("file1.json"), {"key1": "value1", "key2": "value2"}),
            (Path("file2.json"), {"key3": "value3"}),
            (Path("file3.json"), {"key4": "value4", "key5": "value5"}),
        ]
        result = strategy.merge(files)

        # Should return only the last file's data
        assert result == {"key4": "value4", "key5": "value5"}

    def test_merge_with_nested_data(self):
        """Test merge with nested data structures."""
        strategy = ReplaceMergeStrategy()

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
                {
                    "cache": {"redis": {"host": "redis-server", "port": 6379}},
                    "features": ["auth", "logging"],
                },
            ),
        ]
        result = strategy.merge(files)

        # Should return only the last file's data
        expected = {
            "cache": {"redis": {"host": "redis-server", "port": 6379}},
            "features": ["auth", "logging"],
        }
        assert result == expected

    def test_merge_with_mixed_data_types(self):
        """Test merge with mixed data types."""
        strategy = ReplaceMergeStrategy()

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

        # Should return only the last file's data
        assert result == {
            "string": "value2",
            "number": 100,
            "boolean": False,
            "list": [4, 5, 6],
            "null": "not_null",
        }

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = ReplaceMergeStrategy()

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
        ]
        result = strategy.merge(files, test_kwarg="test_value")

        # Should return only the last file's data, kwargs are ignored
        assert result == {"key2": "value2"}

    def test_merge_preserves_data_integrity(self):
        """Test that merge preserves data integrity of the last file."""
        strategy = ReplaceMergeStrategy()

        # Create complex nested structure
        complex_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "deep_key": "deep_value",
                        "list": [1, 2, {"nested": "object"}],
                        "mixed": {"string": "value", "number": 42, "boolean": True},
                    }
                }
            },
            "top_level": "value",
        }

        files = [
            (Path("file1.json"), {"simple": "data"}),
            (Path("file2.json"), complex_data),
        ]
        result = strategy.merge(files)

        # Should return exact copy of complex_data
        assert result == complex_data

        # Verify it's a deep copy (modifying result shouldn't affect original)
        result["level1"]["level2"]["level3"]["deep_key"] = "modified"
        assert complex_data["level1"]["level2"]["level3"]["deep_key"] == "deep_value"

    def test_merge_with_empty_last_file(self):
        """Test merge when the last file has empty data."""
        strategy = ReplaceMergeStrategy()

        files = [
            (Path("file1.json"), {"key1": "value1", "key2": "value2"}),
            (Path("file2.json"), {}),
        ]
        result = strategy.merge(files)

        assert result == {}

    def test_merge_with_single_key_last_file(self):
        """Test merge when the last file has only one key."""
        strategy = ReplaceMergeStrategy()

        files = [
            (
                Path("file1.json"),
                {"key1": "value1", "key2": "value2", "key3": "value3"},
            ),
            (Path("file2.json"), {"single_key": "single_value"}),
        ]
        result = strategy.merge(files)

        assert result == {"single_key": "single_value"}

    def test_get_merge_info(self):
        """Test get_merge_info method."""
        strategy = ReplaceMergeStrategy()

        files = [
            (Path("file1.json"), {"key1": "value1"}),
            (Path("file2.json"), {"key2": "value2"}),
            (Path("file3.json"), {"key3": "value3"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "replace"
        assert info["final_file"] == "file3.json"
        assert info["file_count_processed"] == 3
        assert info["merge_type"] == "complete_replacement"
        assert info["file_count"] == 3
        assert info["files"] == ["file1.json", "file2.json", "file3.json"]

    def test_get_merge_info_empty_files(self):
        """Test get_merge_info with empty file list."""
        strategy = ReplaceMergeStrategy()

        info = strategy.get_merge_info([])

        assert info["strategy"] == "replace"
        assert "final_file" not in info
        assert "file_count_processed" not in info  # This key is not set when no files
        assert info["merge_type"] == "complete_replacement"
        assert info["file_count"] == 0
        assert info["files"] == []

    def test_str_representation(self):
        """Test string representation."""
        strategy = ReplaceMergeStrategy()

        assert str(strategy) == "ReplaceMergeStrategy(replace)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = ReplaceMergeStrategy(test_option=True)

        expected = "ReplaceMergeStrategy(name='replace', options={'test_option': True})"
        assert repr(strategy) == expected
