"""
Cache Mixin for Key Operations

This module provides caching functionality for individual key operations.
The CacheMixin integrates SmartCache with get_key/set_key operations to improve
performance for frequently accessed keys.
"""

# mypy: ignore-errors

from typing import Any, List, Optional
from yapfm.cache import SmartCache


class CacheMixin:
    """
    Mixin providing caching functionality for key operations.
    
    This mixin enhances key operations with intelligent caching:
    - Caches individual key values with TTL support
    - Automatic cache invalidation on key updates
    - Configurable cache settings
    - Cache statistics and monitoring
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # ✅ Appel obligatoire pour le MRO
        
        # Cache configuration
        self.enable_cache = kwargs.get('enable_cache', True)
        self.cache_size = kwargs.get('cache_size', 1000)
        self.cache_ttl = kwargs.get('cache_ttl', 3600)  # 1 hour
        
        # Initialize cache
        if self.enable_cache:
            self._cache = SmartCache(
                max_size=self.cache_size,
                default_ttl=self.cache_ttl
            )
        else:
            self._cache = None

    def _generate_cache_key(self, dot_key: Optional[str], path: Optional[List[str]], key_name: Optional[str]) -> str:
        """Generate a cache key from the key parameters."""
        if dot_key is not None:
            return f"key:{dot_key}"
        elif path is not None and key_name is not None:
            path_str = ".".join(path) if path else ""
            return f"key:{path_str}.{key_name}" if path_str else f"key:{key_name}"
        else:
            raise ValueError("Cannot generate cache key without key parameters")

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
        """
        
        cache_key = self._generate_cache_key(dot_key, path, key_name)
        
        if self._cache is not None:
            # Check if key exists in cache (distinguish between cache miss and None value)
            if self._cache.has_key(cache_key):
                return self._cache.get(cache_key)
        
        # Get value from parent method
        value = super().get_key(dot_key, path=path, key_name=key_name, default=default)
        
        # Cache the value (including None values)
        if self._cache is not None:
            self._cache.set(cache_key, value)
        
        return value

    def get_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
        **kwargs: Any
    ) -> Any:
        """
        Get a value from the file using dot notation with optional caching.
        
        This method overrides the parent get_key to add caching functionality.
        Additional kwargs: use_cache (bool) - whether to use cache (default: True)
        """
        use_cache = kwargs.get('use_cache', True)
        
        if not use_cache or self._cache is None:
            return super().get_key(dot_key, path=path, key_name=key_name, default=default)
        
        return self.get_value(dot_key, path=path, key_name=key_name, default=default)

    def set_key(
        self,
        value: Any,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        overwrite: bool = True,
        **kwargs: Any
    ) -> None:
        """
        Set a value in the file using dot notation with optional cache invalidation.
        
        This method overrides the parent set_key to add cache invalidation.
        Additional kwargs: update_cache (bool) - whether to update cache (default: True)
        """
        # Call parent method
        super().set_key(value, dot_key, path=path, key_name=key_name, overwrite=overwrite)
        
        update_cache = kwargs.get('update_cache', True)
        if update_cache and self._cache is not None:
            cache_key = self._generate_cache_key(dot_key, path, key_name)
            self._cache.delete(cache_key)


    def clear_cache(self) -> None:
        """Clear all cached keys."""
        if self._cache is not None:
            self._cache.clear()

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
        if self._cache is None:
            return 0
        
        if pattern is None:
            # Count entries before clearing
            count = len(self._cache._cache) if hasattr(self._cache, '_cache') else 0
            self._cache.clear()
            return count
        else:
            return self._cache.invalidate_pattern(pattern)
    
