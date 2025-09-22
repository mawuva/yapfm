"""
Cache Mixin for Key Operations

This module provides caching functionality for individual key operations.
The CacheMixin integrates SmartCache with get_key/set_key operations to improve
performance for frequently accessed keys.
"""

# mypy: ignore-errors

from typing import Any, List, Optional

from yapfm.mixins.key_operations_mixin import KeyOperationsMixin


class CacheMixin:
    """
    Mixin providing unified caching and lazy loading functionality.

    This mixin provides:
    - Regular caching for individual keys (strings, numbers, etc.)
    - Lazy loading for sections (which contain multiple keys)
    - Automatic cache invalidation
    - Configurable cache settings
    - Cache statistics and monitoring

    Architecture:
    - Keys: Simple values cached directly (fast access)
    - Sections: Lazy loaded to avoid cache bloat (memory efficient)
    """

    def get_value(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get a value from the file using dot notation with caching.

        Args:
            dot_key: The dot-separated key.
            path: The path to the key.
            key_name: The name of the key.
            default: The default value if the key is not found.

        Returns:
            The value at the specified path or default
            
        Raises:
            ValueError: If neither dot_key nor (path + key_name) is provided.
        """
        # Validate parameters
        if dot_key is None and (path is None or key_name is None):
            raise ValueError("You must provide either dot_key or (path + key_name)")
        cache = self.get_cache()

        if cache is None:
            # Appel direct de KeyOperationsMixin.get_key sans cache
            return KeyOperationsMixin.get_key(
                self, dot_key, path=path, key_name=key_name, default=default
            )

        cache_key = self._generate_cache_key(dot_key, path, key_name, "key")

        # Check if key exists in cache (distinguish between cache miss and None value)
        if cache.has_key(cache_key):
            return cache.get(cache_key)

        # Get value from KeyOperationsMixin
        value = KeyOperationsMixin.get_key(
            self, dot_key, path=path, key_name=key_name, default=default
        )

        # Cache the value (including None values)
        cache.set(cache_key, value)

        return value

    def clear_cache(self) -> None:
        """Clear all cached keys."""
        cache = self.get_cache()

        if cache is not None:
            cache.clear()

    def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            pattern: Optional pattern to match (supports wildcards)

        Returns:
            Number of entries invalidated

        Example:
            >>> fm.invalidate_cache()  # Clear all cache
            >>> fm.invalidate_cache("database.*")  # Clear database-related cache
        """
        cache = self.get_cache()

        if cache is None:
            return 0

        if pattern is None:
            # Count entries before clearing
            count = len(cache._cache) if hasattr(cache, "_cache") else 0
            cache.clear()
            return count
        else:
            return cache.invalidate_pattern(pattern)
