"""
Deep Merge Strategy

This strategy performs a recursive deep merge of multiple dictionaries.
It merges nested structures by combining values at each level, with
configurable overwrite behavior.

Key Features:
- Recursive merging of nested dictionaries
- Configurable overwrite behavior
- Preservation of data types
- Support for complex nested structures

Example:
    >>> from yapfm.multi_file.strategies import DeepMergeStrategy
    >>>
    >>> strategy = DeepMergeStrategy(overwrite=True)
    >>> result = strategy.merge([
    ...     (Path("file1.json"), {"a": {"b": 1, "c": 2}}),
    ...     (Path("file2.json"), {"a": {"c": 3, "d": 4}})
    ... ])
    >>> # Result: {"a": {"b": 1, "c": 3, "d": 4}}
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from yapfm.helpers.dict_utils import deep_merge

from .base import BaseMergeStrategy


class DeepMergeStrategy(BaseMergeStrategy):
    """
    Strategy for performing deep merge of multiple files.

    This strategy recursively merges dictionaries, combining nested
    structures while preserving the hierarchy. It supports configurable
    overwrite behavior for handling conflicts.
    """

    def __init__(self, overwrite: bool = True, **options: Any) -> None:
        """
        Initialize the deep merge strategy.

        Args:
            overwrite: Whether to overwrite existing keys during merge.
            **options: Additional strategy options.
        """
        super().__init__(overwrite=overwrite, **options)
        self.overwrite = overwrite

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Perform deep merge of multiple files.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary containing deeply merged data.

        Example:
            >>> strategy = DeepMergeStrategy()
            >>> result = strategy.merge([
            ...     (Path("config.json"), {"app": {"name": "MyApp"}}),
            ...     (Path("dev.json"), {"app": {"debug": True}})
            ... ])
            >>> # Result: {"app": {"name": "MyApp", "debug": True}}
        """
        if not loaded_files:
            return {}

        # Start with the first file
        result = loaded_files[0][1].copy()

        # Merge remaining files
        for _, data in loaded_files[1:]:
            result = deep_merge(result, data, overwrite=self.overwrite)

        return result

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "deep"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Recursively merges nested dictionaries, combining values at each level"

    def get_optional_options(self) -> Dict[str, Any]:
        """Get optional options with defaults."""
        return {"overwrite": True}

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """Validate and normalize options."""
        validated = super().validate_options(**options)

        # Validate overwrite option
        if "overwrite" in validated:
            if not isinstance(validated["overwrite"], bool):
                raise ValueError("overwrite option must be a boolean")

        return validated

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)
        info.update({"overwrite": self.overwrite, "merge_type": "recursive_deep"})
        return info
