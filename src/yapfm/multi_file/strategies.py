"""
Merge Strategy Enum

This module defines the available merge strategies as an enum for better
type safety and clarity. It provides a centralized way to reference
merge strategies and prevents typos or invalid strategy names.

Key Features:
- Type-safe strategy references
- Clear enumeration of available strategies
- Easy validation and error handling
- IDE autocompletion support

Example:
    >>> from yapfm.multi_file.strategies import MergeStrategy
    >>>
    >>> # Type-safe strategy usage
    >>> strategy = MergeStrategy.DEEP
    >>> print(strategy.value)  # "deep"
    >>>
    >>> # Validation
    >>> if strategy == MergeStrategy.DEEP:
    ...     print("Using deep merge strategy")
"""

from enum import Enum


class MergeStrategy(Enum):
    """
    Enumeration of available merge strategies.

    This enum provides type-safe access to merge strategies and ensures
    that only valid strategy names can be used.
    """

    DEEP = "deep"
    NAMESPACE = "namespace"
    PRIORITY = "priority"
    APPEND = "append"
    REPLACE = "replace"
    CONDITIONAL = "conditional"

    @classmethod
    def from_string(cls, value: str) -> "MergeStrategy":
        """
        Create a MergeStrategy from a string value.

        Args:
            value: String value to convert to enum.

        Returns:
            MergeStrategy enum instance.

        Raises:
            ValueError: If the string value is not a valid strategy.

        Example:
            >>> strategy = MergeStrategy.from_string("deep")
            >>> print(strategy)  # MergeStrategy.DEEP
        """
        value = value.lower().strip()
        for strategy in cls:
            if strategy.value == value:
                return strategy
        raise ValueError(
            f"Invalid merge strategy: {value}. Available: {[s.value for s in cls]}"
        )

    @classmethod
    def get_all_values(cls) -> list[str]:
        """
        Get all strategy values as a list.

        Returns:
            List of all strategy values.

        Example:
            >>> values = MergeStrategy.get_all_values()
            >>> print(values)  # ['deep', 'namespace', 'priority', ...]
        """
        return [strategy.value for strategy in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        Check if a string value is a valid strategy.

        Args:
            value: String value to check.

        Returns:
            True if the value is a valid strategy, False otherwise.

        Example:
            >>> is_valid = MergeStrategy.is_valid("deep")
            >>> print(is_valid)  # True
        """
        try:
            cls.from_string(value)
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        """String representation of the strategy."""
        return self.value

    def __repr__(self) -> str:
        """Detailed string representation of the strategy."""
        return f"MergeStrategy.{self.name}"
