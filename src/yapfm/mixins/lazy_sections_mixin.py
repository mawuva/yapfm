"""
Lazy Sections Mixin

This module provides lazy loading functionality for sections.
The LazySectionsMixin allows sections to be loaded on-demand rather than
loading the entire file at once, improving memory efficiency for large files.

Note: This mixin now uses the unified cache system from CacheMixin.
"""

# mypy: ignore-errors

from typing import Any, Dict, List, Optional


class LazySectionsMixin:
    """
    Mixin providing lazy loading functionality for sections.

    This mixin allows sections to be loaded on-demand:
    - Sections are loaded only when first accessed
    - Each section is cached independently
    - Memory efficient for large files
    - Automatic cache invalidation
    """

    def _get_lazy_sections(self):
        """Get the lazy sections dictionary from the manager."""
        return getattr(self, "_lazy_sections", {})

    def get_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
        lazy: bool = True,
    ) -> Any:
        """
        Get an entire section from the file with lazy loading.

        Args:
            dot_key: The dot-separated key.
            path: The path to the section.
            key_name: The name of the section.
            default: The default value if the section is not found.
            lazy: Whether to use lazy loading for this section.

        Returns:
            The section data or default
        """
        if not lazy or not self.enable_lazy_loading:
            from yapfm.mixins.section_operations_mixin import SectionOperationsMixin

            return SectionOperationsMixin.get_section(
                self, dot_key, path=path, key_name=key_name, default=default
            )

        # Use lazy loading with unified cache
        return self._get_section_lazy(
            dot_key, path=path, key_name=key_name, default=default
        )

    def set_section(
        self,
        data: Dict[str, Any],
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        overwrite: bool = True,
        update_lazy_cache: bool = True,
    ) -> None:
        """
        Set an entire section in the file with lazy cache invalidation.

        Args:
            data: The section data.
            dot_key: The dot-separated key.
            path: The path to the section.
            key_name: The name of the section.
            overwrite: Whether to overwrite the existing section.
            update_lazy_cache: Whether to update lazy cache after setting.
        """
        # Call SectionOperationsMixin method
        from yapfm.mixins.section_operations_mixin import SectionOperationsMixin

        SectionOperationsMixin.set_section(
            self, data, dot_key, path=path, key_name=key_name, overwrite=overwrite
        )

        if update_lazy_cache and self.enable_lazy_loading:
            # Invalidate lazy-loaded section
            self._invalidate_lazy_section(dot_key, path=path, key_name=key_name)

    def delete_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """
        Delete an entire section from the file with lazy cache invalidation.

        Args:
            dot_key: The dot-separated key.
            path: The path to the section.
            key_name: The name of the section.

        Returns:
            True if the section was deleted, False if it didn't exist
        """
        from yapfm.mixins.section_operations_mixin import SectionOperationsMixin

        result = SectionOperationsMixin.delete_section(
            self, dot_key, path=path, key_name=key_name
        )

        if result and self.enable_lazy_loading:
            # Invalidate lazy-loaded section
            self._invalidate_lazy_section(dot_key, path=path, key_name=key_name)

        return result

    def _get_section_lazy(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get a section with lazy loading.

        Args:
            dot_key: The dot-separated key.
            path: The path to the section.
            key_name: The name of the section.
            default: The default value if the section is not found.

        Returns:
            The section data or default
        """
        from yapfm.cache import LazySectionLoader

        section_path = self._generate_cache_key(dot_key, path, key_name, "section")
        lazy_sections = self._get_lazy_sections()

        if section_path not in lazy_sections:

            def loader():
                from yapfm.mixins.section_operations_mixin import SectionOperationsMixin

                return SectionOperationsMixin.get_section(
                    self, dot_key, path=path, key_name=key_name, default=default
                )

            lazy_sections[section_path] = LazySectionLoader(
                loader, section_path, self.get_cache()
            )

        return lazy_sections[section_path].get()

    def _invalidate_lazy_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> None:
        """Invalidate a lazy-loaded section."""
        section_path = self._generate_cache_key(dot_key, path, key_name, "section")
        lazy_sections = self._get_lazy_sections()
        if section_path in lazy_sections:
            lazy_sections[section_path].invalidate()

    def clear_lazy_cache(self) -> None:
        """Clear all lazy-loaded sections."""
        lazy_sections = self._get_lazy_sections()
        for loader in lazy_sections.values():
            loader.invalidate()
        lazy_sections.clear()

    def get_lazy_stats(self) -> Dict[str, Any]:
        """Get lazy loading statistics."""
        lazy_sections = self._get_lazy_sections()
        return {
            "loaded_sections": len(
                [section for section in lazy_sections.values() if section.is_loaded()]
            ),
            "total_sections": len(lazy_sections),
        }
