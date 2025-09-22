"""
Cache Mixin for Key Operations

This module provides caching functionality for individual key operations.
The CacheMixin integrates SmartCache with get_key/set_key operations to improve
performance for frequently accessed keys.
"""

# mypy: ignore-errors

from typing import Any, Optional

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
        key: str = None,
        default: Any = None,
    ) -> Any:
        """
        Get a value from the file using key with caching.

        Args:
            key: The key.
            default: The default value if the key is not found.

        Returns:
            The value at the specified key or default
        """
        cache = self.get_cache()

        if cache is None:
            # Call KeyOperationsMixin.get_key without cache
            return KeyOperationsMixin.get_key(self, dot_key=key, default=default)

        cache_key = self._generate_cache_key(dot_key=key, key_type="key")

        # Try to get from cache first (this will count as hit/miss)
        # Use a sentinel object to distinguish between cache miss and None value
        _sentinel = object()
        cached_value = cache.get(cache_key, default=_sentinel)

        # If we got a real value (not our sentinel), return it
        if cached_value is not _sentinel:
            return cached_value

        # Get value from KeyOperationsMixin (cache miss)
        value = KeyOperationsMixin.get_key(self, dot_key=key, default=default)

        # Cache the value (including None values)
        cache.set(cache_key, value)

        return value

    def set_value(
        self,
        key: str,
        value: Any,
        overwrite: bool = True,
    ) -> None:
        """
        Set a value in the file using key.

        The cache will be automatically updated on the next get_value() call.

        Args:
            key: The key to set
            value: The value to set
            overwrite: Whether to overwrite existing values
        """
        # Write the value to the file
        KeyOperationsMixin.set_key(self, value, dot_key=key, overwrite=overwrite)

        cache = self.get_cache()

        if cache is not None:
            cache.delete(self._generate_cache_key(dot_key=key, key_type="key"))

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
