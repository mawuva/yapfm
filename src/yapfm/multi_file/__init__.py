"""
Multi-File Operations Module

This module provides functionality for loading and merging multiple files
using various strategies. It implements the Strategy pattern for different
merge approaches with a simple, direct interface.

Key Components:
- Merge strategies (deep, namespace, priority, etc.)
- Simple factory functions for common use cases
- Direct strategy imports for maximum flexibility

Example:
    >>> from yapfm.multi_file import load_and_merge, DeepMergeStrategy
    >>>
    >>> # Using factory function
    >>> result = load_and_merge(["config.json", "secrets.json"], "deep")
    >>>
    >>> # Using strategy directly
    >>> strategy = DeepMergeStrategy(overwrite=True)
    >>> result = strategy.merge(loaded_files)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from yapfm.cache import SmartCache

from .merge_strategies import (
    AppendMergeStrategy,
    BaseMergeStrategy,
    ConditionalMergeStrategy,
    DeepMergeStrategy,
    NamespaceMergeStrategy,
    PriorityMergeStrategy,
    ReplaceMergeStrategy,
)
from .strategies import MergeStrategy

__all__ = [
    "BaseMergeStrategy",
    "DeepMergeStrategy",
    "NamespaceMergeStrategy",
    "PriorityMergeStrategy",
    "AppendMergeStrategy",
    "ReplaceMergeStrategy",
    "ConditionalMergeStrategy",
    "MergeStrategy",
    "load_and_merge",
    "get_available_strategies",
]


def load_and_merge(
    file_paths: Union[List[Union[str, Path]], str],
    strategy: Union[str, MergeStrategy, BaseMergeStrategy] = MergeStrategy.DEEP,
    cache: Optional[SmartCache] = None,
    enable_cache: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Convenience function to load and merge multiple files.

    Args:
        file_paths: List of file paths or single path/pattern string.
        strategy: Strategy name, enum, or strategy instance.
        cache: Optional SmartCache instance to use.
        enable_cache: Whether to enable caching.
        **kwargs: Additional arguments for the strategy.

    Returns:
        Dictionary containing merged data.

    Example:
        >>> result = load_and_merge(["config.json", "secrets.json"], "deep")
        >>> result = load_and_merge(["config.json", "secrets.json"], MergeStrategy.DEEP)
        >>> result = load_and_merge(["*.json"], DeepMergeStrategy(overwrite=True))

        >>> # With custom cache
        >>> from yapfm.cache import SmartCache
        >>> cache = SmartCache(max_size=500)
        >>> result = load_and_merge(["config.json"], "deep", cache=cache)
    """
    from .loader import MultiFileLoader

    loader = MultiFileLoader(cache=cache, enable_cache=enable_cache)
    return loader.load_and_merge(file_paths, strategy, **kwargs)


def get_available_strategies() -> List[str]:
    """
    Get list of available merge strategy names.

    Returns:
        List of strategy names.
    """
    return MergeStrategy.get_all_values()
