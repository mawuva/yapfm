"""
Multi-File Operations Mixin

This mixin provides functionality to load and merge multiple files into a single
dictionary. It uses the Strategy pattern for different merge approaches and
integrates with the existing cache system.

Key Features:
- Multiple merge strategies (deep, namespace, priority, conditional, append, replace)
- Support for file patterns (glob patterns)
- Integration with existing cache system
- Conditional merging based on environment or context
- Namespace prefixing for organized data structure
- Performance optimization with lazy loading

Example:
    >>> from yapfm import YAPFileManager
    >>> fm = YAPFileManager("config.json")
    >>>
    >>> # Load and merge multiple files with deep merge
    >>> merged_data = fm.load_multiple_files([
    ...     "config.json",
    ...     "secrets.json",
    ...     "env.toml"
    ... ], strategy="deep")
    >>>
    >>> # Load with namespace strategy
    >>> data = fm.load_multiple_files([
    ...     "database.json",
    ...     "cache.toml"
    ... ], strategy="namespace")
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from yapfm.multi_file.loader import MultiFileLoader
from yapfm.multi_file.merge_strategies.base import BaseMergeStrategy
from yapfm.multi_file.strategies import MergeStrategy


class MultiFileMixin:
    """
    Mixin for handling multiple file operations and merging.

    This mixin extends the file manager with capabilities to load and merge
    multiple files using various strategies. It integrates seamlessly with
    the existing cache and context systems.
    """

    def load_multiple_files(
        self,
        file_paths: Union[List[Union[str, Path]], str],
        strategy: Union[str, MergeStrategy, BaseMergeStrategy] = MergeStrategy.DEEP,
        file_patterns: Optional[List[str]] = None,
        conditional_filter: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Load and merge multiple files into a single dictionary.

        Args:
            file_paths: List of file paths or single path/pattern string.
            strategy: Strategy to use for merging files (name, enum, or instance).
            file_patterns: Optional list of glob patterns to expand.
            conditional_filter: Optional function to filter files based on content.
            use_cache: Whether to use caching for loaded files.
            **kwargs: Additional arguments passed to the strategy.

        Returns:
            Dictionary containing merged data from all files.

        Example:
            >>> # Deep merge multiple files
            >>> data = fm.load_multiple_files([
            ...     "config.json",
            ...     "secrets.json"
            ... ], strategy="deep")
            >>>
            >>> # Namespace merge with prefix
            >>> data = fm.load_multiple_files([
            ...     "database.json",
            ...     "cache.toml"
            ... ], strategy="namespace", namespace_prefix="app")
            >>>
            >>> # Use file patterns
            >>> data = fm.load_multiple_files(
            ...     "config/*.json",
            ...     strategy="deep"
            ... )
        """
        # Use the MultiFileLoader for the actual work
        # Pass the existing cache if available
        existing_cache = None
        if use_cache and hasattr(self, "get_cache"):
            existing_cache = self.get_cache()

        loader = MultiFileLoader(cache=existing_cache, enable_cache=use_cache)
        return loader.load_and_merge(
            file_paths,
            strategy=strategy,
            file_patterns=file_patterns,
            conditional_filter=conditional_filter,
            use_cache=use_cache,
            **kwargs,
        )

    def get_available_merge_strategies(self) -> List[str]:
        """
        Get list of available merge strategies.

        Returns:
            List of strategy names.
        """
        return MergeStrategy.get_all_values()

    def invalidate_multi_file_cache(self, file_path: Union[str, Path]) -> None:
        """
        Invalidate cache for a specific file in multi-file operations.

        Args:
            file_path: Path to the file to invalidate.
        """
        if hasattr(self, "get_cache"):
            cache = self.get_cache()
            if cache:
                file_path = Path(file_path)
                # Invalidate all cache entries for this file (regardless of mtime)
                pattern = f"multi_file:{file_path}:*"
                cache.invalidate_pattern(pattern)

    def load_file_group(
        self, group_name: str, config: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Load a predefined group of files based on configuration.

        Args:
            group_name: Name of the file group.
            config: Configuration dictionary defining the group.
            **kwargs: Additional arguments for file loading.

        Returns:
            Merged dictionary from the file group.

        Example:
            >>> config = {
            ...     "app_config": {
            ...         "files": ["config.json", "secrets.json"],
            ...         "strategy": "deep",
            ...         "namespace_prefix": "app"
            ...     }
            ... }
            >>> data = fm.load_file_group("app_config", config)
        """
        if group_name not in config:
            raise ValueError(f"File group '{group_name}' not found in configuration")

        group_config = config[group_name]

        # Extract configuration parameters
        files = group_config.get("files", [])
        strategy = group_config.get("strategy", MergeStrategy.DEEP)
        file_patterns = group_config.get("file_patterns")
        conditional_filter = group_config.get("conditional_filter")
        use_cache = group_config.get("use_cache", True)

        # Extract strategy-specific options
        strategy_options = {
            key: value
            for key, value in group_config.items()
            if key
            not in [
                "files",
                "strategy",
                "file_patterns",
                "conditional_filter",
                "use_cache",
            ]
        }

        return self.load_multiple_files(
            files,
            strategy=strategy,
            file_patterns=file_patterns,
            conditional_filter=conditional_filter,
            use_cache=use_cache,
            **strategy_options,
            **kwargs,
        )
