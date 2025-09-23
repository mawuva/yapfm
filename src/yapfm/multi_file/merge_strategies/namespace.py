"""
Namespace Merge Strategy

This strategy merges files by placing each file's data under a separate
namespace, typically based on the file name. This prevents conflicts
between files and maintains clear separation of concerns.

Key Features:
- Each file gets its own namespace
- Configurable namespace generation
- Prevention of key conflicts
- Clear separation of file data

Example:
    >>> from yapfm.multi_file.strategies import NamespaceMergeStrategy
    >>>
    >>> strategy = NamespaceMergeStrategy()
    >>> result = strategy.merge([
    ...     (Path("database.json"), {"host": "localhost"}),
    ...     (Path("cache.json"), {"redis": "redis://localhost"})
    ... ])
    >>> # Result: {"database": {"host": "localhost"}, "cache": {"redis": "redis://localhost"}}
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .base import BaseMergeStrategy


class NamespaceMergeStrategy(BaseMergeStrategy):
    """
    Strategy for merging files into separate namespaces.

    This strategy places each file's data under a separate namespace,
    preventing conflicts and maintaining clear separation. The namespace
    is typically derived from the file name but can be customized.
    """

    def __init__(
        self,
        namespace_generator: Optional[Callable[[Path], str]] = None,
        namespace_prefix: Optional[str] = None,
        **options: Any,
    ) -> None:
        """
        Initialize the namespace merge strategy.

        Args:
            namespace_generator: Function to generate namespace from file path.
            namespace_prefix: Optional prefix to add to all namespaces.
            **options: Additional strategy options.
        """
        super().__init__(
            namespace_generator=namespace_generator,
            namespace_prefix=namespace_prefix,
            **options,
        )
        self.namespace_generator = (
            namespace_generator or self._default_namespace_generator
        )
        self.namespace_prefix = namespace_prefix

    def _default_namespace_generator(self, file_path: Path) -> str:
        """
        Default namespace generator using file stem.

        Args:
            file_path: Path to the file.

        Returns:
            Generated namespace string.
        """
        return file_path.stem

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge files into separate namespaces.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary with each file's data under its own namespace.

        Example:
            >>> strategy = NamespaceMergeStrategy()
            >>> result = strategy.merge([
            ...     (Path("config.json"), {"app": {"name": "MyApp"}}),
            ...     (Path("secrets.json"), {"api": {"key": "secret"}})
            ... ])
            >>> # Result: {"config": {"app": {"name": "MyApp"}}, "secrets": {"api": {"key": "secret"}}}
        """
        if not loaded_files:
            return {}

        result = {}

        for file_path, data in loaded_files:
            # Generate namespace for this file
            namespace = self.namespace_generator(file_path)

            # Add prefix if specified
            if self.namespace_prefix:
                namespace = f"{self.namespace_prefix}.{namespace}"

            # Place data under namespace
            result[namespace] = data

        return result

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "namespace"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Merges files by placing each file's data under a separate namespace"

    def get_optional_options(self) -> Dict[str, Any]:
        """Get optional options with defaults."""
        return {"namespace_generator": None, "namespace_prefix": None}

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """Validate and normalize options."""
        validated = super().validate_options(**options)

        # Validate namespace_generator
        if "namespace_generator" in validated:
            generator = validated["namespace_generator"]
            if generator is not None and not callable(generator):
                raise ValueError("namespace_generator must be callable or None")

        # Validate namespace_prefix
        if "namespace_prefix" in validated:
            prefix = validated["namespace_prefix"]
            if prefix is not None and not isinstance(prefix, str):
                raise ValueError("namespace_prefix must be a string or None")

        return validated

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)

        # Generate namespaces for all files
        namespaces = []
        for file_path, _ in loaded_files:
            namespace = self.namespace_generator(file_path)
            if self.namespace_prefix:
                namespace = f"{self.namespace_prefix}.{namespace}"
            namespaces.append(namespace)

        info.update(
            {
                "namespace_prefix": self.namespace_prefix,
                "namespaces": namespaces,
                "merge_type": "namespace_separation",
            }
        )
        return info
