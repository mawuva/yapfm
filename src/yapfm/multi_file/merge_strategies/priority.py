"""
Priority Merge Strategy

This strategy merges files based on priority order, where files with
higher priority override values from files with lower priority. This
is useful for configuration hierarchies where some files should take
precedence over others.

Key Features:
- Priority-based merging
- Configurable priority ordering
- Override behavior for conflicts
- Support for explicit priority lists

Example:
    >>> from yapfm.multi_file.strategies import PriorityMergeStrategy
    >>>
    >>> strategy = PriorityMergeStrategy(priority_order=[1, 0, 2])
    >>> result = strategy.merge([
    ...     (Path("base.json"), {"a": 1, "b": 2}),      # Priority 1
    ...     (Path("dev.json"), {"b": 3, "c": 4}),       # Priority 0 (lowest)
    ...     (Path("prod.json"), {"a": 5, "d": 6})       # Priority 2 (highest)
    ... ])
    >>> # Result: {"a": 5, "b": 2, "c": 4, "d": 6}
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .base import BaseMergeStrategy


class PriorityMergeStrategy(BaseMergeStrategy):
    """
    Strategy for merging files based on priority order.

    This strategy merges files where higher priority files override
    values from lower priority files. Priority can be determined by
    file order, explicit priority list, or custom priority function.
    """

    def __init__(
        self,
        priority_order: Optional[List[int]] = None,
        overwrite: bool = True,
        **options: Any,
    ) -> None:
        """
        Initialize the priority merge strategy.

        Args:
            priority_order: Optional list of priority indices (higher = more priority).
            overwrite: Whether to overwrite existing keys during merge.
            **options: Additional strategy options.
        """
        super().__init__(priority_order=priority_order, overwrite=overwrite, **options)
        self.priority_order = priority_order
        self.overwrite = overwrite

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge files based on priority order.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary with merged data based on priority.

        Example:
            >>> strategy = PriorityMergeStrategy(priority_order=[1, 0])
            >>> result = strategy.merge([
            ...     (Path("base.json"), {"a": 1, "b": 2}),    # Priority 1
            ...     (Path("override.json"), {"b": 3, "c": 4}) # Priority 0 (higher)
            ... ])
            >>> # Result: {"a": 1, "b": 2, "c": 4}
        """
        if not loaded_files:
            return {}

        # Apply priority ordering
        ordered_files = self._apply_priority_ordering(loaded_files)

        # Start with the highest priority file
        result = ordered_files[0][1].copy()

        # Merge remaining files (lower priority)
        for _, data in ordered_files[1:]:
            if self.overwrite:
                result.update(data)
            else:
                for key, value in data.items():
                    if key not in result:
                        result[key] = value

        return result

    def _apply_priority_ordering(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """
        Apply priority ordering to loaded files.

        Args:
            loaded_files: List of files to order.

        Returns:
            Files ordered by priority (highest first).
        """
        if self.priority_order is None:
            # Default: reverse order (last file has highest priority)
            return list(reversed(loaded_files))

        if len(self.priority_order) != len(loaded_files):
            raise ValueError(
                f"Priority order length ({len(self.priority_order)}) "
                f"must match number of files ({len(loaded_files)})"
            )

        # Sort files by priority (higher index = higher priority)
        indexed_files = list(enumerate(loaded_files))
        if self.priority_order is not None:
            priority_order = self.priority_order  # Type narrowing for mypy
            indexed_files.sort(key=lambda x: priority_order[x[0]], reverse=True)

        return [file_data for _, file_data in indexed_files]

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "priority"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Merges files based on priority order, with higher priority files overriding lower priority ones"

    def get_optional_options(self) -> Dict[str, Any]:
        """Get optional options with defaults."""
        return {"priority_order": None, "overwrite": True}

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """Validate and normalize options."""
        validated = super().validate_options(**options)

        # Validate priority_order
        if "priority_order" in validated:
            priority_order = validated["priority_order"]
            if priority_order is not None:
                if not isinstance(priority_order, list):
                    raise ValueError("priority_order must be a list or None")
                if not all(isinstance(x, int) for x in priority_order):
                    raise ValueError("All priority_order values must be integers")

        # Validate overwrite
        if "overwrite" in validated:
            if not isinstance(validated["overwrite"], bool):
                raise ValueError("overwrite option must be a boolean")

        return validated

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)

        # Calculate priority information
        if self.priority_order:
            priority_info: List[Dict[str, Union[str, int]]] = []
            for i, (file_path, _) in enumerate(loaded_files):
                priority_info.append(
                    {
                        "file": str(file_path),
                        "index": i,
                        "priority": self.priority_order[i],
                    }
                )
            priority_info.sort(key=lambda x: int(x["priority"]), reverse=True)
        else:
            priority_info = [
                {
                    "file": str(file_path),
                    "index": i,
                    "priority": len(loaded_files) - i - 1,
                }
                for i, (file_path, _) in enumerate(loaded_files)
            ]

        info.update(
            {
                "priority_order": self.priority_order,
                "overwrite": self.overwrite,
                "priority_info": priority_info,
                "merge_type": "priority_based",
            }
        )
        return info
