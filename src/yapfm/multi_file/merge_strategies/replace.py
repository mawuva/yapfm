"""
Replace Merge Strategy

This strategy merges files by completely replacing the result with the
last file's data. This is useful when you want to use files as a chain
of overrides, where each file completely replaces the previous one.

Key Features:
- Complete replacement with last file
- Simple and predictable behavior
- Useful for override chains
- Minimal processing overhead

Example:
    >>> from yapfm.multi_file.strategies import ReplaceMergeStrategy
    >>>
    >>> strategy = ReplaceMergeStrategy()
    >>> result = strategy.merge([
    ...     (Path("base.json"), {"a": 1, "b": 2}),
    ...     (Path("override.json"), {"c": 3, "d": 4})
    ... ])
    >>> # Result: {"c": 3, "d": 4}
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base import BaseMergeStrategy


class ReplaceMergeStrategy(BaseMergeStrategy):
    """
    Strategy for merging files by complete replacement.

    This strategy simply returns the data from the last file, effectively
    replacing all previous data. This is useful for override chains where
    each file should completely replace the previous one.
    """

    def __init__(self, **options: Any) -> None:
        """
        Initialize the replace merge strategy.

        Args:
            **options: Additional strategy options.
        """
        super().__init__(**options)

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge files by replacing with the last file.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary containing data from the last file.

        Example:
            >>> strategy = ReplaceMergeStrategy()
            >>> result = strategy.merge([
            ...     (Path("base.json"), {"app": {"name": "BaseApp"}}),
            ...     (Path("dev.json"), {"app": {"name": "DevApp", "debug": True}})
            ... ])
            >>> # Result: {"app": {"name": "DevApp", "debug": True}}
        """
        if not loaded_files:
            return {}

        # Return the last file's data
        return loaded_files[-1][1].copy()

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "replace"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Merges files by completely replacing with the last file's data"

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)

        # Add information about which file was used
        if loaded_files:
            info["final_file"] = str(loaded_files[-1][0])
            info["file_count_processed"] = len(loaded_files)

        info["merge_type"] = "complete_replacement"
        return info
