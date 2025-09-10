"""
Context Management Mixin

This module provides context manager functionality for FileManager.
The ContextMixin contains context managers for safe file operations
and automatic saving.
"""

# mypy: ignore-errors

from contextlib import contextmanager


class ContextMixin:
    """
    Mixin providing context manager functionality.

    This mixin contains:
    - Basic context manager support (__enter__, __exit__)
    - Lazy save context manager
    - Auto save context manager
    """

    def __enter__(self):
        """Enter the context manager and load the file."""
        if getattr(self, "auto_create", False):
            if not self.exists():
                self.create_empty_file()
            elif not self.is_loaded():
                # Try to load, but if it fails (empty file), create empty document
                try:
                    self.load()
                except Exception:
                    self.create_empty_file()
        elif not self.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        elif not self.is_loaded():
            self.load()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and save if dirty."""
        self.save_if_dirty()

    @contextmanager
    def lazy_save(self, save_on_exit: bool = True):
        """
        Context manager for lazy saving.

        Args:
            save_on_exit: Whether to save when exiting the context.

        Example:
            >>> with fm.lazy_save():
            ...     fm.set_key("database.host", "localhost")
            ...     fm.set_key("database.port", 5432)
            ... # Save happens here
        """
        original_dirty = self.is_dirty()
        try:
            yield self
        finally:
            if save_on_exit and self.is_dirty():
                self.save()
            elif not save_on_exit:
                # Restore original dirty state
                if original_dirty:
                    self.mark_as_dirty()
                else:
                    self.mark_as_clean()

    @contextmanager
    def auto_save(self, save_on_exit: bool = True):
        """
        Context manager for automatic saving.

        Args:
            save_on_exit: Whether to save when exiting the context.

        Example:
            >>> with fm.auto_save():
            ...     fm.set_key("database.host", "localhost")
            ...     fm.set_key("database.port", 5432)
            ... # Save happens here
        """
        if not self.is_loaded():
            self.load()
        try:
            yield self
        finally:
            if save_on_exit and self.is_dirty():
                self.save()
