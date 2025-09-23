"""
Multi-File Utilities

This module provides utility functions for loading and merging multiple files.
It includes a simple loader class and helper functions for common operations.

Key Features:
- File pattern expansion
- File loading with caching
- Strategy instantiation
- Error handling

Example:
    >>> from yapfm.multi_file.utils import MultiFileLoader
    >>>
    >>> loader = MultiFileLoader()
    >>> result = loader.load_and_merge(["config.json", "secrets.json"], "deep")
"""

import glob
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from yapfm.cache import SmartCache
from yapfm.exceptions import StrategyError
from yapfm.registry import FileStrategyRegistry

from .merge_strategies.append import AppendMergeStrategy
from .merge_strategies.base import BaseMergeStrategy
from .merge_strategies.conditional import ConditionalMergeStrategy
from .merge_strategies.deep import DeepMergeStrategy
from .merge_strategies.namespace import NamespaceMergeStrategy
from .merge_strategies.priority import PriorityMergeStrategy
from .merge_strategies.replace import ReplaceMergeStrategy
from .strategies import MergeStrategy


class MultiFileLoader:
    """
    Simple loader for multiple files with strategy-based merging.

    This class provides a straightforward interface for loading multiple files
    and merging them using various strategies. It integrates with the SmartCache
    system for efficient file caching.
    """

    def __init__(
        self,
        cache: Optional[SmartCache] = None,
        enable_cache: bool = True,
        cache_ttl: Optional[float] = 3600,  # 1 hour default
    ) -> None:
        """
        Initialize the multi-file loader.

        Args:
            cache: Optional SmartCache instance to use. If None, creates a new one.
            enable_cache: Whether to enable caching for loaded files.
            cache_ttl: TTL for cached files in seconds.
        """
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl

        if enable_cache:
            if cache is not None:
                self._cache: Optional[SmartCache] = cache
            else:
                # Create a dedicated cache for multi-file operations
                self._cache = SmartCache(
                    max_size=1000, default_ttl=cache_ttl, track_stats=True
                )
        else:
            self._cache = None

    def load_and_merge(
        self,
        file_paths: Union[List[Union[str, Path]], str],
        strategy: Union[str, MergeStrategy, BaseMergeStrategy] = MergeStrategy.DEEP,
        file_patterns: Optional[List[str]] = None,
        conditional_filter: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Load and merge multiple files using the specified strategy.

        Args:
            file_paths: List of file paths or single path/pattern string.
            strategy: Merge strategy to use (name, enum, or instance).
            file_patterns: Optional list of glob patterns to expand.
            conditional_filter: Optional function to filter files based on content.
            use_cache: Whether to use caching for loaded files.
            **kwargs: Additional arguments passed to the strategy.

        Returns:
            Dictionary containing merged data from all files.

        Example:
            >>> loader = MultiFileLoader()
            >>>
            >>> # Using strategy name
            >>> result = loader.load_and_merge(
            ...     ["config.json", "secrets.json"],
            ...     strategy="deep"
            ... )
            >>>
            >>> # Using strategy enum
            >>> from yapfm.multi_file import MergeStrategy
            >>> result = loader.load_and_merge(
            ...     ["config.json", "secrets.json"],
            ...     strategy=MergeStrategy.DEEP
            ... )
        """
        # Expand file paths and patterns
        expanded_paths = self._expand_file_paths(file_paths, file_patterns)

        if not expanded_paths:
            return {}

        # Load all files
        loaded_files = self._load_files(expanded_paths, use_cache)

        # Apply conditional filtering if provided
        if conditional_filter:
            loaded_files = self._apply_conditional_filter(
                loaded_files, conditional_filter
            )

        # Get merge strategy
        merge_strategy = self._get_merge_strategy(strategy, **kwargs)

        # Merge files according to strategy
        return merge_strategy.merge(loaded_files, **kwargs)

    def _expand_file_paths(
        self,
        file_paths: Union[List[Union[str, Path]], str],
        file_patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """Expand file paths and patterns into a list of actual file paths."""
        expanded = []

        # Handle single string input
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        # Add additional patterns if provided
        if file_patterns:
            file_paths.extend(file_patterns)

        for path in file_paths:
            path_str = str(path)

            # Check if it's a glob pattern
            if "*" in path_str or "?" in path_str or "[" in path_str:
                # Expand glob pattern
                matches = glob.glob(path_str, recursive=True)
                expanded.extend([Path(match) for match in matches])
            else:
                # Regular file path
                expanded.append(Path(path))

        # Remove duplicates and sort for consistent ordering
        return sorted(list(set(expanded)))

    def _load_files(
        self, file_paths: List[Path], use_cache: bool = True
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """Load multiple files and return their data."""
        loaded_files = []

        for file_path in file_paths:
            if not file_path.exists():
                continue  # Skip non-existent files

            # Generate cache key if caching is enabled
            cache_key = None
            if use_cache and self._cache is not None:
                # Use file path and modification time for cache key
                cache_key = f"multi_file:{file_path}:{file_path.stat().st_mtime}"
                cached_data = self._cache.get(cache_key)
                if cached_data is not None:
                    loaded_files.append((file_path, cached_data))
                    continue

            # Load file using appropriate strategy
            try:
                strategy = FileStrategyRegistry.get_strategy(file_path.suffix.lower())
                if strategy is None:
                    raise StrategyError(
                        f"No strategy found for extension: {file_path.suffix}"
                    )

                data = strategy.load(file_path)

                # Cache the loaded data using SmartCache
                if cache_key and self._cache is not None:
                    self._cache.set(cache_key, data, ttl=self.cache_ttl)

                loaded_files.append((file_path, data))

            except Exception as e:
                # Log error but continue with other files
                print(f"Warning: Failed to load {file_path}: {e}")
                continue

        return loaded_files

    def _apply_conditional_filter(
        self,
        loaded_files: List[Tuple[Path, Dict[str, Any]]],
        conditional_filter: Callable[[str, Dict[str, Any]], bool],
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """Apply conditional filtering to loaded files."""
        return [
            (file_path, data)
            for file_path, data in loaded_files
            if conditional_filter(str(file_path), data)
        ]

    def _get_merge_strategy(
        self, strategy: Union[str, MergeStrategy, BaseMergeStrategy], **kwargs: Any
    ) -> BaseMergeStrategy:
        """Get a merge strategy instance."""
        if isinstance(strategy, BaseMergeStrategy):
            return strategy

        if isinstance(strategy, MergeStrategy):
            return self._create_strategy_by_name(strategy.value, **kwargs)

        if isinstance(strategy, str):
            return self._create_strategy_by_name(strategy, **kwargs)

        raise ValueError(f"Invalid strategy type: {type(strategy)}")

    def _create_strategy_by_name(self, name: str, **kwargs: Any) -> BaseMergeStrategy:
        """Create a strategy instance by name."""
        strategy_map = {
            "deep": DeepMergeStrategy,
            "namespace": NamespaceMergeStrategy,
            "priority": PriorityMergeStrategy,
            "append": AppendMergeStrategy,
            "replace": ReplaceMergeStrategy,
            "conditional": ConditionalMergeStrategy,
        }

        if name not in strategy_map:
            raise ValueError(
                f"Unknown strategy: {name}. Available: {list(strategy_map.keys())}"
            )

        strategy_class = strategy_map[name]
        return strategy_class(**kwargs)

    def clear_cache(self) -> None:
        """Clear the file cache."""
        if self._cache is not None:
            self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self._cache is None:
            return {"enabled": False}

        # Get comprehensive stats from SmartCache
        smart_cache_stats = self._cache.get_stats()

        return {
            "enabled": True,
            "cache_type": "SmartCache",
            "smart_cache_stats": smart_cache_stats,
        }

    def invalidate_file_cache(self, file_path: Union[str, Path]) -> None:
        """
        Invalidate cache for a specific file.

        Args:
            file_path: Path to the file to invalidate.
        """
        if self._cache is not None:
            file_path = Path(file_path)
            # Invalidate all cache entries for this file (regardless of mtime)
            pattern = f"multi_file:{file_path}:*"
            self._cache.invalidate_pattern(pattern)
