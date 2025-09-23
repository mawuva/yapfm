"""
Tests for BaseMergeStrategy.

This module contains tests for the abstract base class that all merge strategies inherit from.
"""

# mypy: ignore-errors

from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from yapfm.multi_file.merge_strategies.base import BaseMergeStrategy


class TestMergeStrategy(BaseMergeStrategy):
    """Test implementation of BaseMergeStrategy for testing purposes."""

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Test implementation of merge method."""
        if not loaded_files:
            return {}

        result = {}
        for _, data in loaded_files:
            result.update(data)
        return result

    def get_name(self) -> str:
        """Test implementation of get_name method."""
        return "test"


class TestBaseMergeStrategy:
    """Test cases for BaseMergeStrategy."""

    def test_init_with_options(self):
        """Test initialization with options."""
        strategy = TestMergeStrategy(test_option=True, another_option="value")

        assert strategy.options == {"test_option": True, "another_option": "value"}

    def test_get_description(self):
        """Test get_description method."""
        strategy = TestMergeStrategy()

        description = strategy.get_description()
        assert description == "Merge strategy: test"

    def test_validate_options(self):
        """Test validate_options method."""
        strategy = TestMergeStrategy()

        # Test with valid options
        validated = strategy.validate_options(test_option=True)
        assert validated == {"test_option": True}

        # Test with no options
        validated = strategy.validate_options()
        assert validated == {}

    def test_can_handle_empty_files(self):
        """Test can_handle with empty file list."""
        strategy = TestMergeStrategy()

        assert not strategy.can_handle([])

    def test_can_handle_valid_files(self):
        """Test can_handle with valid files."""
        strategy = TestMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        assert strategy.can_handle(files)

    def test_get_required_options(self):
        """Test get_required_options method."""
        strategy = TestMergeStrategy()

        required = strategy.get_required_options()
        assert required == []

    def test_get_optional_options(self):
        """Test get_optional_options method."""
        strategy = TestMergeStrategy()

        optional = strategy.get_optional_options()
        assert optional == {}

    def test_preprocess_files(self):
        """Test preprocess_files method."""
        strategy = TestMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        processed = strategy.preprocess_files(files)

        assert processed == files

    def test_postprocess_result(self):
        """Test postprocess_result method."""
        strategy = TestMergeStrategy()

        result = {"key": "value"}
        files = [(Path("test.json"), {"key": "value"})]
        processed = strategy.postprocess_result(result, files)

        assert processed == result

    def test_get_merge_info(self):
        """Test get_merge_info method."""
        strategy = TestMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "test"
        assert info["file_count"] == 1
        assert info["files"] == ["test.json"]
        assert info["options"] == {}

    def test_str_representation(self):
        """Test string representation."""
        strategy = TestMergeStrategy()

        assert str(strategy) == "TestMergeStrategy(test)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = TestMergeStrategy(test_option=True)

        expected = "TestMergeStrategy(name='test', options={'test_option': True})"
        assert repr(strategy) == expected

    def test_merge_with_empty_files(self):
        """Test merge with empty file list."""
        strategy = TestMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_with_single_file(self):
        """Test merge with single file."""
        strategy = TestMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"key": "value"}

    def test_merge_with_multiple_files(self):
        """Test merge with multiple files."""
        strategy = TestMergeStrategy()

        files = [
            (Path("test1.json"), {"key1": "value1"}),
            (Path("test2.json"), {"key2": "value2"}),
        ]
        result = strategy.merge(files)

        assert result == {"key1": "value1", "key2": "value2"}

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = TestMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, test_kwarg="test_value")

        assert result == {"key": "value"}

    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods must be implemented."""
        with pytest.raises(TypeError):
            BaseMergeStrategy()
