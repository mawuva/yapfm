"""
Cleanup Mixin

This module provides cleanup functionality for the FileManager.
The CleanupMixin contains operations for cleaning empty sections, removing nulls, and compacting data.
"""

# mypy: ignore-errors

from typing import Any, Callable, Dict


class CleanupMixin:
    """
    Mixin for data cleanup operations.
    """

    def _process_cleanup(self, data: Any, cleanup_func: Callable[[Any], bool]) -> int:
        """
        Generic function to process data cleanup operations.

        Args:
            data: Data to process
            cleanup_func: Function that determines if an item should be removed
                        Returns True if item should be removed, False otherwise

        Returns:
            Number of items removed
        """
        removed_count = 0

        if isinstance(data, dict):
            # Create list of keys to remove to avoid modifying dict during iteration
            keys_to_remove = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    sub_removed = self._process_cleanup(value, cleanup_func)
                    removed_count += sub_removed

                    # Check if item should be removed after processing
                    if cleanup_func(value):
                        keys_to_remove.append(key)
                elif cleanup_func(value):
                    keys_to_remove.append(key)

            # Remove items
            for key in keys_to_remove:
                del data[key]
                removed_count += 1

        elif isinstance(data, list):
            # Process list items
            i = 0
            while i < len(data):
                value = data[i]
                if isinstance(value, (dict, list)):
                    sub_removed = self._process_cleanup(value, cleanup_func)
                    removed_count += sub_removed

                    # Check if item should be removed after processing
                    if cleanup_func(value):
                        data.pop(i)
                        removed_count += 1
                    else:
                        i += 1
                elif cleanup_func(value):
                    data.pop(i)
                    removed_count += 1
                else:
                    i += 1

        return removed_count

    def clean_empty_sections(self) -> int:
        """
        Remove empty sections from the data.

        Returns:
            Number of empty sections removed

        Example:
            >>> removed = fm.clean_empty_sections()
            >>> print(f"Removed {removed} empty sections")
        """

        def is_empty_section(value):
            """Check if a value represents an empty section."""
            if isinstance(value, dict):
                return len(value) == 0
            elif isinstance(value, list):
                return len(value) == 0
            return False

        self.load_if_not_loaded()

        removed_count = self._process_cleanup(self.document, is_empty_section)
        if removed_count > 0:
            self.mark_as_dirty()

        return removed_count

    def remove_nulls(self) -> int:
        """
        Remove null/None values from the data.

        Returns:
            Number of null values removed

        Example:
            >>> removed = fm.remove_nulls()
            >>> print(f"Removed {removed} null values")
        """

        def is_null_value(value):
            """Check if a value is null/None."""
            return value is None

        self.load_if_not_loaded()

        removed_count = self._process_cleanup(self.document, is_null_value)
        if removed_count > 0:
            self.mark_as_dirty()

        return removed_count

    def compact(self) -> Dict[str, int]:
        """
        Optimize the data structure by removing empty sections and nulls.

        Returns:
            Dictionary with counts of operations performed

        Example:
            >>> result = fm.compact()
            >>> print(f"Removed {result['empty_sections']} empty sections and {result['nulls']} nulls")
        """
        self.load_if_not_loaded()

        # Remove nulls first
        nulls_removed = self.remove_nulls()

        # Then remove empty sections
        empty_sections_removed = self.clean_empty_sections()

        return {
            "nulls": nulls_removed,
            "empty_sections": empty_sections_removed,
            "total_operations": nulls_removed + empty_sections_removed,
        }
