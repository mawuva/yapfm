"""
Tests for PriorityMergeStrategy.

This module contains tests for the priority merge strategy that merges files based on priority order.
"""

# mypy: ignore-errors

from pathlib import Path

import pytest

from yapfm.multi_file.merge_strategies.priority import PriorityMergeStrategy


class TestPriorityMergeStrategy:
    """Test cases for PriorityMergeStrategy."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        strategy = PriorityMergeStrategy()

        assert strategy.priority_order is None
        assert strategy.overwrite is True
        assert strategy.options == {"priority_order": None, "overwrite": True}

    def test_init_with_priority_order(self):
        """Test initialization with priority order."""
        priority_order = [1, 0, 2]
        strategy = PriorityMergeStrategy(priority_order=priority_order)

        assert strategy.priority_order == priority_order
        assert strategy.overwrite is True

    def test_init_with_overwrite_false(self):
        """Test initialization with overwrite=False."""
        strategy = PriorityMergeStrategy(overwrite=False)

        assert strategy.overwrite is False
        assert strategy.options == {"priority_order": None, "overwrite": False}

    def test_get_name(self):
        """Test get_name method."""
        strategy = PriorityMergeStrategy()

        assert strategy.get_name() == "priority"

    def test_get_description(self):
        """Test get_description method."""
        strategy = PriorityMergeStrategy()

        description = strategy.get_description()
        assert "Merges files based on priority order" in description

    def test_get_optional_options(self):
        """Test get_optional_options method."""
        strategy = PriorityMergeStrategy()

        options = strategy.get_optional_options()
        assert options == {"priority_order": None, "overwrite": True}

    def test_validate_options_valid(self):
        """Test validate_options with valid options."""
        strategy = PriorityMergeStrategy()

        validated = strategy.validate_options(priority_order=[1, 0, 2], overwrite=False)

        assert validated["priority_order"] == [1, 0, 2]
        assert validated["overwrite"] is False

    def test_validate_options_invalid_priority_order_type(self):
        """Test validate_options with invalid priority order type."""
        strategy = PriorityMergeStrategy()

        with pytest.raises(ValueError, match="priority_order must be a list or None"):
            strategy.validate_options(priority_order="invalid")

    def test_validate_options_invalid_priority_order_values(self):
        """Test validate_options with invalid priority order values."""
        strategy = PriorityMergeStrategy()

        with pytest.raises(
            ValueError, match="All priority_order values must be integers"
        ):
            strategy.validate_options(priority_order=[1, "invalid", 2])

    def test_validate_options_invalid_overwrite_type(self):
        """Test validate_options with invalid overwrite type."""
        strategy = PriorityMergeStrategy()

        with pytest.raises(ValueError, match="overwrite option must be a boolean"):
            strategy.validate_options(overwrite="invalid")

    def test_merge_empty_files(self):
        """Test merge with empty file list."""
        strategy = PriorityMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merge with single file."""
        strategy = PriorityMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"key": "value"}

    def test_merge_without_priority_order(self):
        """Test merge without explicit priority order (default: reverse order)."""
        strategy = PriorityMergeStrategy()

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
            (Path("file3.json"), {"key": "value3"}),
        ]
        result = strategy.merge(files)

        # Without priority order, files are reversed and merged in order
        # Order: file3 (reversed first) -> file2 -> file1 (reversed last)
        # Result: file1 overwrites file2 which overwrites file3
        assert result == {"key": "value1"}

    def test_merge_with_priority_order(self):
        """Test merge with explicit priority order."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0, 2])

        files = [
            (Path("file1.json"), {"key": "value1"}),  # Priority 1
            (Path("file2.json"), {"key": "value2"}),  # Priority 0 (lowest)
            (Path("file3.json"), {"key": "value3"}),  # Priority 2 (highest)
        ]
        result = strategy.merge(files)

        # File with highest priority (2) should be the base, then lower priority files merge into it
        # Since overwrite=True by default, lower priority files overwrite the base
        # Order: file3 (priority 2) -> file1 (priority 1) -> file2 (priority 0)
        # Result: file2 overwrites file1 which overwrites file3
        assert result == {"key": "value2"}  # Priority 0 (lowest) overwrites everything

    def test_merge_with_priority_order_overwrite_true(self):
        """Test merge with priority order and overwrite=True."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0], overwrite=True)

        files = [
            (Path("file1.json"), {"key1": "value1", "key2": "value2"}),  # Priority 1
            (
                Path("file2.json"),
                {"key2": "value2_updated", "key3": "value3"},
            ),  # Priority 0 (higher)
        ]
        result = strategy.merge(files)

        # Order: file1 (priority 1) -> file2 (priority 0)
        # Start with file1: {"key1": "value1", "key2": "value2"}
        # Merge file2: {"key2": "value2_updated", "key3": "value3"}
        # Result: {"key1": "value1", "key2": "value2_updated", "key3": "value3"}
        expected = {"key1": "value1", "key2": "value2_updated", "key3": "value3"}
        assert result == expected

    def test_merge_with_priority_order_overwrite_false(self):
        """Test merge with priority order and overwrite=False."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0], overwrite=False)

        files = [
            (Path("file1.json"), {"key1": "value1", "key2": "value2"}),  # Priority 1
            (
                Path("file2.json"),
                {"key2": "value2_updated", "key3": "value3"},
            ),  # Priority 0 (higher)
        ]
        result = strategy.merge(files)

        # Order: file1 (priority 1) -> file2 (priority 0)
        # Start with file1: {"key1": "value1", "key2": "value2"}
        # Merge file2: {"key2": "value2_updated", "key3": "value3"}
        # With overwrite=False, only add new keys, don't overwrite existing ones
        # Result: {"key1": "value1", "key2": "value2", "key3": "value3"}
        expected = {"key1": "value1", "key2": "value2", "key3": "value3"}
        assert result == expected

    def test_merge_with_nested_data(self):
        """Test merge with nested data structures."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0])

        files = [
            (
                Path("file1.json"),
                {
                    "database": {"host": "localhost", "port": 5432},
                    "app": {"name": "MyApp"},
                },
            ),  # Priority 1
            (
                Path("file2.json"),
                {
                    "database": {"host": "prod-server", "password": "secret"},
                    "app": {"debug": True},
                },
            ),  # Priority 0 (higher)
        ]
        result = strategy.merge(files)

        # Order: file1 (priority 1) -> file2 (priority 0)
        # Start with file1: {"database": {"host": "localhost", "port": 5432}, "app": {"name": "MyApp"}}
        # Merge file2: {"database": {"host": "prod-server", "password": "secret"}, "app": {"debug": True}}
        # Result: file2 completely overwrites file1 (shallow merge)
        expected = {
            "database": {"host": "prod-server", "password": "secret"},
            "app": {"debug": True},
        }
        assert result == expected

    def test_apply_priority_ordering_valid(self):
        """Test _apply_priority_ordering with valid priority order."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0, 2])

        files = [
            (Path("file1.json"), {"key": "value1"}),  # Priority 1
            (Path("file2.json"), {"key": "value2"}),  # Priority 0 (lowest)
            (Path("file3.json"), {"key": "value3"}),  # Priority 2 (highest)
        ]
        ordered = strategy._apply_priority_ordering(files)

        # Should be ordered by priority (highest first)
        assert ordered[0] == files[2]  # Priority 2
        assert ordered[1] == files[0]  # Priority 1
        assert ordered[2] == files[1]  # Priority 0

    def test_apply_priority_ordering_none(self):
        """Test _apply_priority_ordering with None priority order."""
        strategy = PriorityMergeStrategy(priority_order=None)

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
            (Path("file3.json"), {"key": "value3"}),
        ]
        ordered = strategy._apply_priority_ordering(files)

        # Should be in reverse order (last file first)
        assert ordered[0] == files[2]
        assert ordered[1] == files[1]
        assert ordered[2] == files[0]

    def test_apply_priority_ordering_invalid_length(self):
        """Test _apply_priority_ordering with invalid priority order length."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0])  # Only 2 elements

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
            (Path("file3.json"), {"key": "value3"}),  # 3 files
        ]

        with pytest.raises(
            ValueError,
            match="Priority order length \\(2\\) must match number of files \\(3\\)",
        ):
            strategy._apply_priority_ordering(files)

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = PriorityMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, test_kwarg="test_value")

        assert result == {"key": "value"}

    def test_get_merge_info_with_priority_order(self):
        """Test get_merge_info with priority order."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0, 2])

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
            (Path("file3.json"), {"key": "value3"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "priority"
        assert info["priority_order"] == [1, 0, 2]
        assert info["overwrite"] is True
        assert info["merge_type"] == "priority_based"
        assert info["file_count"] == 3

        # Check priority info
        priority_info = info["priority_info"]
        assert len(priority_info) == 3

        # Should be sorted by priority (highest first)
        assert priority_info[0]["priority"] == 2  # file3
        assert priority_info[1]["priority"] == 1  # file1
        assert priority_info[2]["priority"] == 0  # file2

    def test_get_merge_info_without_priority_order(self):
        """Test get_merge_info without priority order."""
        strategy = PriorityMergeStrategy(priority_order=None)

        files = [
            (Path("file1.json"), {"key": "value1"}),
            (Path("file2.json"), {"key": "value2"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["priority_order"] is None

        # Check priority info (should be reverse order)
        priority_info = info["priority_info"]
        assert len(priority_info) == 2
        assert priority_info[0]["priority"] == 1  # file2 (reverse order)
        assert priority_info[1]["priority"] == 0  # file1

    def test_str_representation(self):
        """Test string representation."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0])

        assert str(strategy) == "PriorityMergeStrategy(priority)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = PriorityMergeStrategy(priority_order=[1, 0], overwrite=False)

        expected = "PriorityMergeStrategy(name='priority', options={'priority_order': [1, 0], 'overwrite': False})"
        assert repr(strategy) == expected
