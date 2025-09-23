"""
Append Merge Strategy

This strategy merges files by appending values to lists. When a key exists
in multiple files, the values are combined into a list. This is useful for
collecting data from multiple sources without losing any information.

Key Features:
- Appends values to lists
- Preserves all data from all files
- Handles mixed data types
- Configurable list creation behavior

Example:
    >>> from yapfm.multi_file.strategies import AppendMergeStrategy
    >>>
    >>> strategy = AppendMergeStrategy()
    >>> result = strategy.merge([
    ...     (Path("file1.json"), {"items": ["a", "b"]}),
    ...     (Path("file2.json"), {"items": ["c"], "other": "value"})
    ... ])
    >>> # Result: {"items": ["a", "b", "c"], "other": ["value"]}
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base import BaseMergeStrategy


class AppendMergeStrategy(BaseMergeStrategy):
    """
    Strategy for merging files by appending values to lists.

    This strategy combines values by appending them to lists, ensuring
    that no data is lost during the merge process. It handles both
    existing lists and single values.
    """

    def __init__(self, create_lists_for_singles: bool = True, **options: Any) -> None:
        """
        Initialize the append merge strategy.

        Args:
            create_lists_for_singles: Whether to create lists for single values.
            **options: Additional strategy options.
        """
        super().__init__(create_lists_for_singles=create_lists_for_singles, **options)
        self.create_lists_for_singles = create_lists_for_singles

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge files by appending values to lists.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary with appended values.

        Example:
            >>> strategy = AppendMergeStrategy()
            >>> result = strategy.merge([
            ...     (Path("file1.json"), {"tags": ["python", "config"]}),
            ...     (Path("file2.json"), {"tags": ["json"], "version": "1.0"})
            ... ])
            >>> # Result: {"tags": ["python", "config", "json"], "version": ["1.0"]}
        """
        if not loaded_files:
            return {}

        result: Dict[str, Any] = {}

        for _, data in loaded_files:
            for key, value in data.items():
                if key in result:
                    # Key exists, append to existing list
                    if isinstance(result[key], list):
                        if isinstance(value, list):
                            result[key].extend(value)
                        else:
                            result[key].append(value)
                    else:
                        # Convert existing value to list and append new value
                        result[key] = [result[key]]
                        if isinstance(value, list):
                            result[key].extend(value)
                        else:
                            result[key].append(value)
                else:
                    # New key, create list if needed
                    if isinstance(value, list):
                        result[key] = value.copy()
                    elif self.create_lists_for_singles:
                        result[key] = [value]
                    else:
                        result[key] = value

        return result

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "append"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Merges files by appending values to lists, preserving all data"

    def get_optional_options(self) -> Dict[str, Any]:
        """Get optional options with defaults."""
        return {"create_lists_for_singles": True}

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """Validate and normalize options."""
        validated = super().validate_options(**options)

        # Validate create_lists_for_singles
        if "create_lists_for_singles" in validated:
            if not isinstance(validated["create_lists_for_singles"], bool):
                raise ValueError("create_lists_for_singles must be a boolean")

        return validated

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)
        info.update(
            {
                "create_lists_for_singles": self.create_lists_for_singles,
                "merge_type": "append_to_lists",
            }
        )
        return info
