"""
Lazy Loading System

This module provides lazy loading functionality for sections and keys.
The LazySectionLoader handles on-demand loading of sections with caching.
"""

from typing import Any, Callable, Optional

from .smart_cache import SmartCache


class LazySectionLoader:
    """
    Lazy loader for individual sections.

    This class handles the lazy loading of a specific section,
    including caching and invalidation.
    """

    def __init__(
        self,
        loader_func: Callable[[], Any],
        section_path: str,
        cache: Optional[SmartCache] = None,
    ):
        self._loader_func = loader_func
        self._section_path = section_path
        self._cache = cache
        self._loaded = False
        self._value = None
        self._load_error: Optional[Exception] = None

    def get(self) -> Any:
        """Get the section value, loading it if necessary."""
        if not self._loaded:
            try:
                # Try to get from cache first
                if self._cache:
                    cached_value = self._cache.get(self._section_path)
                    if cached_value is not None:
                        self._value = cached_value
                        self._loaded = True
                        return self._value

                # Load the section
                self._value = self._loader_func()
                self._loaded = True

                # Cache the loaded section
                if self._cache:
                    self._cache.set(self._section_path, self._value)

            except Exception as e:
                self._load_error = e
                raise e

        return self._value

    def invalidate(self) -> None:
        """Invalidate the loaded section."""
        self._loaded = False
        self._value = None
        self._load_error = None

        # Remove from cache
        if self._cache:
            self._cache.delete(self._section_path)

    def is_loaded(self) -> bool:
        """Check if the section is loaded."""
        return self._loaded

    def get_load_error(self) -> Optional[Exception]:
        """Get the last load error if any."""
        return self._load_error
