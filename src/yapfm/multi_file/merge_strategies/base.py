"""
Base Merge Strategy

This module defines the abstract base class for all merge strategies.
It provides the interface that all concrete strategies must implement
to handle different ways of merging multiple files.

Key Features:
- Protocol-based interface for type safety
- Standardized merge operations
- Support for configuration and options
- Extensible design for new merge strategies

Example:
    >>> from yapfm.multi_file.strategies import BaseMergeStrategy
    >>> from pathlib import Path
    >>>
    >>> class MyMergeStrategy(BaseMergeStrategy):
    ...     def merge(self, loaded_files, **options):
    ...         # Implement custom merge logic
    ...         return merged_data
    ...
    ...     def get_name(self):
    ...         return "my_strategy"
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple


class BaseMergeStrategy(ABC):
    """
    Abstract base class for all merge strategies.

    This class defines the interface that all concrete merge strategies
    must implement. It provides a standardized way to merge multiple
    files into a single dictionary.
    """

    def __init__(self, **options: Any) -> None:
        """
        Initialize the merge strategy with options.

        Args:
            **options: Strategy-specific configuration options.
        """
        self.options = options

    @abstractmethod
    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge multiple loaded files into a single dictionary.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary containing merged data from all files.

        Raises:
            ValueError: If merge cannot be performed.

        Example:
            >>> strategy = DeepMergeStrategy()
            >>> result = strategy.merge([
            ...     (Path("file1.json"), {"a": 1}),
            ...     (Path("file2.json"), {"b": 2})
            ... ])
            >>> # Result: {"a": 1, "b": 2}
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this merge strategy.

        Returns:
            String name of the strategy.

        Example:
            >>> strategy = DeepMergeStrategy()
            >>> print(strategy.get_name())  # "deep"
        """
        pass

    def get_description(self) -> str:
        """
        Get a description of what this strategy does.

        Returns:
            String description of the strategy.
        """
        return f"Merge strategy: {self.get_name()}"

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """
        Validate and normalize strategy options.

        Args:
            **options: Options to validate.

        Returns:
            Validated and normalized options.

        Raises:
            ValueError: If options are invalid.
        """
        return options

    def can_handle(self, loaded_files: List[Tuple[Path, Dict[str, Any]]]) -> bool:
        """
        Check if this strategy can handle the given files.

        Args:
            loaded_files: List of files to check.

        Returns:
            True if this strategy can handle the files, False otherwise.
        """
        return len(loaded_files) > 0

    def get_required_options(self) -> List[str]:
        """
        Get list of required options for this strategy.

        Returns:
            List of required option names.
        """
        return []

    def get_optional_options(self) -> Dict[str, Any]:
        """
        Get dictionary of optional options with their default values.

        Returns:
            Dictionary mapping option names to default values.
        """
        return {}

    def preprocess_files(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """
        Preprocess files before merging (optional override).

        Args:
            loaded_files: List of files to preprocess.

        Returns:
            Preprocessed list of files.
        """
        return loaded_files

    def postprocess_result(
        self, result: Dict[str, Any], loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Postprocess the merge result (optional override).

        Args:
            result: The merged result dictionary.
            loaded_files: Original list of files that were merged.

        Returns:
            Postprocessed result dictionary.
        """
        return result

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Get information about the merge operation.

        Args:
            loaded_files: List of files that will be merged.

        Returns:
            Dictionary containing merge information.
        """
        return {
            "strategy": self.get_name(),
            "file_count": len(loaded_files),
            "files": [str(path) for path, _ in loaded_files],
            "options": self.options,
        }

    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}({self.get_name()})"

    def __repr__(self) -> str:
        """Detailed string representation of the strategy."""
        return f"{self.__class__.__name__}(name='{self.get_name()}', options={self.options})"
