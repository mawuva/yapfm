"""
Tests for MergeStrategy enum.

This module contains tests for the MergeStrategy enum that provides
type-safe access to merge strategy names.
"""

# mypy: ignore-errors

import pytest

from yapfm.multi_file.strategies import MergeStrategy


class TestMergeStrategy:
    """Test cases for MergeStrategy enum."""

    def test_enum_values(self):
        """Test that all expected enum values are present."""
        expected_values = [
            "deep",
            "namespace",
            "priority",
            "append",
            "replace",
            "conditional",
        ]

        actual_values = [member.value for member in MergeStrategy]

        assert len(actual_values) == len(expected_values)
        for expected in expected_values:
            assert expected in actual_values

    def test_enum_members(self):
        """Test that all enum members are accessible."""
        assert MergeStrategy.DEEP.value == "deep"
        assert MergeStrategy.NAMESPACE.value == "namespace"
        assert MergeStrategy.PRIORITY.value == "priority"
        assert MergeStrategy.APPEND.value == "append"
        assert MergeStrategy.REPLACE.value == "replace"
        assert MergeStrategy.CONDITIONAL.value == "conditional"

    def test_from_string_valid(self):
        """Test from_string with valid strategy names."""
        assert MergeStrategy.from_string("deep") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("DEEP") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("Deep") == MergeStrategy.DEEP

        assert MergeStrategy.from_string("namespace") == MergeStrategy.NAMESPACE
        assert MergeStrategy.from_string("NAMESPACE") == MergeStrategy.NAMESPACE

        assert MergeStrategy.from_string("priority") == MergeStrategy.PRIORITY
        assert MergeStrategy.from_string("append") == MergeStrategy.APPEND
        assert MergeStrategy.from_string("replace") == MergeStrategy.REPLACE
        assert MergeStrategy.from_string("conditional") == MergeStrategy.CONDITIONAL

    def test_from_string_invalid(self):
        """Test from_string with invalid strategy names."""
        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("invalid")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("deep_merge")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("123")

    def test_from_string_case_insensitive(self):
        """Test that from_string is case insensitive."""
        assert MergeStrategy.from_string("DEEP") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("Deep") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("deep") == MergeStrategy.DEEP

        assert MergeStrategy.from_string("NAMESPACE") == MergeStrategy.NAMESPACE
        assert MergeStrategy.from_string("Namespace") == MergeStrategy.NAMESPACE
        assert MergeStrategy.from_string("namespace") == MergeStrategy.NAMESPACE

    def test_get_all_values(self):
        """Test get_all_values method."""
        all_values = MergeStrategy.get_all_values()

        assert isinstance(all_values, list)
        assert len(all_values) == 6

        expected_values = [
            "deep",
            "namespace",
            "priority",
            "append",
            "replace",
            "conditional",
        ]

        for expected in expected_values:
            assert expected in all_values

        # Check that all values are strings
        for value in all_values:
            assert isinstance(value, str)

    def test_get_all_values_immutable(self):
        """Test that get_all_values returns a new list each time."""
        values1 = MergeStrategy.get_all_values()
        values2 = MergeStrategy.get_all_values()

        assert values1 == values2
        assert values1 is not values2  # Different objects

    def test_is_valid_true(self):
        """Test is_valid with valid strategy names."""
        assert MergeStrategy.is_valid("deep") is True
        assert MergeStrategy.is_valid("DEEP") is True
        assert MergeStrategy.is_valid("Deep") is True

        assert MergeStrategy.is_valid("namespace") is True
        assert MergeStrategy.is_valid("NAMESPACE") is True

        assert MergeStrategy.is_valid("priority") is True
        assert MergeStrategy.is_valid("append") is True
        assert MergeStrategy.is_valid("replace") is True
        assert MergeStrategy.is_valid("conditional") is True

    def test_is_valid_false(self):
        """Test is_valid with invalid strategy names."""
        assert MergeStrategy.is_valid("invalid") is False
        assert MergeStrategy.is_valid("") is False
        assert MergeStrategy.is_valid("deep_merge") is False
        assert MergeStrategy.is_valid("123") is False
        assert MergeStrategy.is_valid("None") is False
        assert MergeStrategy.is_valid("True") is False

    def test_is_valid_case_insensitive(self):
        """Test that is_valid is case insensitive."""
        assert MergeStrategy.is_valid("DEEP") is True
        assert MergeStrategy.is_valid("Deep") is True
        assert MergeStrategy.is_valid("deep") is True

        assert MergeStrategy.is_valid("NAMESPACE") is True
        assert MergeStrategy.is_valid("Namespace") is True
        assert MergeStrategy.is_valid("namespace") is True

    def test_enum_comparison(self):
        """Test enum member comparison."""
        assert MergeStrategy.DEEP == MergeStrategy.DEEP
        assert MergeStrategy.DEEP != MergeStrategy.NAMESPACE

        # Test with string values
        assert MergeStrategy.DEEP.value == "deep"
        assert MergeStrategy.DEEP.value != "namespace"

    def test_enum_iteration(self):
        """Test iterating over enum members."""
        members = list(MergeStrategy)

        assert len(members) == 6
        assert MergeStrategy.DEEP in members
        assert MergeStrategy.NAMESPACE in members
        assert MergeStrategy.PRIORITY in members
        assert MergeStrategy.APPEND in members
        assert MergeStrategy.REPLACE in members
        assert MergeStrategy.CONDITIONAL in members

    def test_enum_membership(self):
        """Test membership testing."""
        assert "deep" in [member.value for member in MergeStrategy]
        assert "namespace" in [member.value for member in MergeStrategy]
        assert "invalid" not in [member.value for member in MergeStrategy]

    def test_enum_string_representation(self):
        """Test string representation of enum members."""
        assert str(MergeStrategy.DEEP) == "deep"
        assert str(MergeStrategy.NAMESPACE) == "namespace"
        assert str(MergeStrategy.PRIORITY) == "priority"

    def test_enum_repr(self):
        """Test repr of enum members."""
        assert repr(MergeStrategy.DEEP) == "MergeStrategy.DEEP"
        assert repr(MergeStrategy.NAMESPACE) == "MergeStrategy.NAMESPACE"

    def test_enum_hash(self):
        """Test that enum members are hashable."""
        # This is important for using enum members as dictionary keys
        strategy_dict = {
            MergeStrategy.DEEP: "Deep merge strategy",
            MergeStrategy.NAMESPACE: "Namespace merge strategy",
        }

        assert strategy_dict[MergeStrategy.DEEP] == "Deep merge strategy"
        assert strategy_dict[MergeStrategy.NAMESPACE] == "Namespace merge strategy"

    def test_enum_equality_with_strings(self):
        """Test equality comparison with strings."""
        # Enum members should not be equal to their string values
        assert MergeStrategy.DEEP != "deep"
        assert MergeStrategy.DEEP.value == "deep"

        # But they should be equal to themselves
        assert MergeStrategy.DEEP == MergeStrategy.DEEP

    def test_enum_ordering(self):
        """Test that enum members can be ordered."""
        strategies = [MergeStrategy.APPEND, MergeStrategy.DEEP, MergeStrategy.NAMESPACE]
        sorted_strategies = sorted(strategies, key=lambda x: x.value)

        # Note: This test assumes alphabetical ordering by value
        assert sorted_strategies[0] == MergeStrategy.APPEND
        assert sorted_strategies[1] == MergeStrategy.DEEP
        assert sorted_strategies[2] == MergeStrategy.NAMESPACE

    def test_enum_immutability(self):
        """Test that enum members are immutable."""
        # This test ensures that enum members cannot be modified
        original_value = MergeStrategy.DEEP.value

        # Attempting to modify the value should not work
        try:
            MergeStrategy.DEEP.value = "modified"
        except AttributeError:
            pass  # Expected behavior

        # Value should remain unchanged
        assert MergeStrategy.DEEP.value == original_value

    def test_enum_type_annotation(self):
        """Test that enum can be used in type annotations."""

        def process_strategy(strategy: MergeStrategy) -> str:
            return strategy.value

        assert process_strategy(MergeStrategy.DEEP) == "deep"
        assert process_strategy(MergeStrategy.NAMESPACE) == "namespace"

    def test_enum_in_union_types(self):
        """Test that enum can be used in union types."""
        from typing import Union

        def process_strategy_or_string(strategy: Union[MergeStrategy, str]) -> str:
            if isinstance(strategy, MergeStrategy):
                return strategy.value
            return strategy

        assert process_strategy_or_string(MergeStrategy.DEEP) == "deep"
        assert process_strategy_or_string("custom") == "custom"
