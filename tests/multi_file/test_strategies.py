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
        """
        Scenario: Test that all expected enum values are present

        Expected:
        - Should contain all expected strategy values
        - Should have correct number of enum members
        - Should include all required strategy types
        """
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
        """
        Scenario: Test that all enum members are accessible

        Expected:
        - Should provide access to all enum members
        - Should have correct values for each member
        - Should maintain consistent member names
        """
        assert MergeStrategy.DEEP.value == "deep"
        assert MergeStrategy.NAMESPACE.value == "namespace"
        assert MergeStrategy.PRIORITY.value == "priority"
        assert MergeStrategy.APPEND.value == "append"
        assert MergeStrategy.REPLACE.value == "replace"
        assert MergeStrategy.CONDITIONAL.value == "conditional"

    def test_from_string_valid(self):
        """
        Scenario: Test from_string with valid strategy names

        Expected:
        - Should convert valid strings to enum members
        - Should handle case variations correctly
        - Should return correct enum for each valid string
        """
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
        """
        Scenario: Test from_string with invalid strategy names

        Expected:
        - Should raise ValueError for invalid names
        - Should handle empty strings correctly
        - Should reject non-existent strategy names
        """
        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("invalid")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("deep_merge")

        with pytest.raises(ValueError, match="Invalid merge strategy"):
            MergeStrategy.from_string("123")

    def test_from_string_case_insensitive(self):
        """
        Scenario: Test that from_string is case insensitive

        Expected:
        - Should handle uppercase strings correctly
        - Should handle mixed case strings correctly
        - Should handle lowercase strings correctly
        """
        assert MergeStrategy.from_string("DEEP") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("Deep") == MergeStrategy.DEEP
        assert MergeStrategy.from_string("deep") == MergeStrategy.DEEP

        assert MergeStrategy.from_string("NAMESPACE") == MergeStrategy.NAMESPACE
        assert MergeStrategy.from_string("Namespace") == MergeStrategy.NAMESPACE
        assert MergeStrategy.from_string("namespace") == MergeStrategy.NAMESPACE

    def test_get_all_values(self):
        """
        Scenario: Test get_all_values method

        Expected:
        - Should return list of all enum values
        - Should contain correct number of values
        - Should return all values as strings
        """
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
        """
        Scenario: Test that get_all_values returns a new list each time

        Expected:
        - Should return new list instance each time
        - Should maintain same content across calls
        - Should prevent external modification
        """
        values1 = MergeStrategy.get_all_values()
        values2 = MergeStrategy.get_all_values()

        assert values1 == values2
        assert values1 is not values2  # Different objects

    def test_is_valid_true(self):
        """
        Scenario: Test is_valid with valid strategy names

        Expected:
        - Should return True for valid strategy names
        - Should handle case variations correctly
        - Should validate all supported strategies
        """
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
        """
        Scenario: Test is_valid with invalid strategy names

        Expected:
        - Should return False for invalid strategy names
        - Should handle empty strings correctly
        - Should reject non-existent strategies
        """
        assert MergeStrategy.is_valid("invalid") is False
        assert MergeStrategy.is_valid("") is False
        assert MergeStrategy.is_valid("deep_merge") is False
        assert MergeStrategy.is_valid("123") is False
        assert MergeStrategy.is_valid("None") is False
        assert MergeStrategy.is_valid("True") is False

    def test_is_valid_case_insensitive(self):
        """
        Scenario: Test that is_valid is case insensitive

        Expected:
        - Should handle uppercase strings correctly
        - Should handle mixed case strings correctly
        - Should handle lowercase strings correctly
        """
        assert MergeStrategy.is_valid("DEEP") is True
        assert MergeStrategy.is_valid("Deep") is True
        assert MergeStrategy.is_valid("deep") is True

        assert MergeStrategy.is_valid("NAMESPACE") is True
        assert MergeStrategy.is_valid("Namespace") is True
        assert MergeStrategy.is_valid("namespace") is True

    def test_enum_comparison(self):
        """
        Scenario: Test enum member comparison

        Expected:
        - Should compare equal members as equal
        - Should compare different members as not equal
        - Should handle string value comparisons correctly
        """
        assert MergeStrategy.DEEP == MergeStrategy.DEEP
        assert MergeStrategy.DEEP != MergeStrategy.NAMESPACE

        # Test with string values
        assert MergeStrategy.DEEP.value == "deep"
        assert MergeStrategy.DEEP.value != "namespace"

    def test_enum_iteration(self):
        """
        Scenario: Test iterating over enum members

        Expected:
        - Should iterate over all enum members
        - Should include all expected members
        - Should maintain correct member count
        """
        members = list(MergeStrategy)

        assert len(members) == 6
        assert MergeStrategy.DEEP in members
        assert MergeStrategy.NAMESPACE in members
        assert MergeStrategy.PRIORITY in members
        assert MergeStrategy.APPEND in members
        assert MergeStrategy.REPLACE in members
        assert MergeStrategy.CONDITIONAL in members

    def test_enum_membership(self):
        """
        Scenario: Test membership testing

        Expected:
        - Should identify valid members correctly
        - Should reject invalid members
        - Should handle value-based membership testing
        """
        assert "deep" in [member.value for member in MergeStrategy]
        assert "namespace" in [member.value for member in MergeStrategy]
        assert "invalid" not in [member.value for member in MergeStrategy]

    def test_enum_string_representation(self):
        """
        Scenario: Test string representation of enum members

        Expected:
        - Should return correct string values
        - Should maintain consistent string format
        - Should handle all enum members correctly
        """
        assert str(MergeStrategy.DEEP) == "deep"
        assert str(MergeStrategy.NAMESPACE) == "namespace"
        assert str(MergeStrategy.PRIORITY) == "priority"

    def test_enum_repr(self):
        """
        Scenario: Test repr of enum members

        Expected:
        - Should return descriptive repr strings
        - Should include class name in repr
        - Should be consistent across all members
        """
        assert repr(MergeStrategy.DEEP) == "MergeStrategy.DEEP"
        assert repr(MergeStrategy.NAMESPACE) == "MergeStrategy.NAMESPACE"

    def test_enum_hash(self):
        """
        Scenario: Test that enum members are hashable

        Expected:
        - Should be usable as dictionary keys
        - Should maintain hash consistency
        - Should support hash-based operations
        """
        # This is important for using enum members as dictionary keys
        strategy_dict = {
            MergeStrategy.DEEP: "Deep merge strategy",
            MergeStrategy.NAMESPACE: "Namespace merge strategy",
        }

        assert strategy_dict[MergeStrategy.DEEP] == "Deep merge strategy"
        assert strategy_dict[MergeStrategy.NAMESPACE] == "Namespace merge strategy"

    def test_enum_equality_with_strings(self):
        """
        Scenario: Test equality comparison with strings

        Expected:
        - Should not equal string values directly
        - Should equal their own string values via .value
        - Should maintain proper equality semantics
        """
        # Enum members should not be equal to their string values
        assert MergeStrategy.DEEP != "deep"
        assert MergeStrategy.DEEP.value == "deep"

        # But they should be equal to themselves
        assert MergeStrategy.DEEP == MergeStrategy.DEEP

    def test_enum_ordering(self):
        """
        Scenario: Test that enum members can be ordered

        Expected:
        - Should support sorting by value
        - Should maintain consistent ordering
        - Should handle alphabetical ordering correctly
        """
        strategies = [MergeStrategy.APPEND, MergeStrategy.DEEP, MergeStrategy.NAMESPACE]
        sorted_strategies = sorted(strategies, key=lambda x: x.value)

        # Note: This test assumes alphabetical ordering by value
        assert sorted_strategies[0] == MergeStrategy.APPEND
        assert sorted_strategies[1] == MergeStrategy.DEEP
        assert sorted_strategies[2] == MergeStrategy.NAMESPACE

    def test_enum_immutability(self):
        """
        Scenario: Test that enum members are immutable

        Expected:
        - Should prevent modification of enum values
        - Should raise AttributeError on modification attempts
        - Should maintain original values after modification attempts
        """
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
        """
        Scenario: Test that enum can be used in type annotations

        Expected:
        - Should work in function parameter type hints
        - Should maintain type safety
        - Should support type checking
        """

        def process_strategy(strategy: MergeStrategy) -> str:
            return strategy.value

        assert process_strategy(MergeStrategy.DEEP) == "deep"
        assert process_strategy(MergeStrategy.NAMESPACE) == "namespace"

    def test_enum_in_union_types(self):
        """
        Scenario: Test that enum can be used in union types

        Expected:
        - Should work in Union type annotations
        - Should support type checking with unions
        - Should handle both enum and string types
        """
        from typing import Union

        def process_strategy_or_string(strategy: Union[MergeStrategy, str]) -> str:
            if isinstance(strategy, MergeStrategy):
                return strategy.value
            return strategy

        assert process_strategy_or_string(MergeStrategy.DEEP) == "deep"
        assert process_strategy_or_string("custom") == "custom"
