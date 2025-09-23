"""
Clone Mixin

This module provides cloning and copying functionality for the FileManager.
The CloneMixin contains operations for cloning, copying, and merging data.
"""

# mypy: ignore-errors

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from yapfm.strategies import BaseFileStrategy

if TYPE_CHECKING:
    from yapfm.manager import YAPFileManager


class CloneMixin:
    """
    Mixin for cloning and copying operations.
    """

    def clone(self) -> "YAPFileManager":
        """
        Create a complete copy of the manager.

        Returns:
            New YAPFileManager with the same data

        Example:
            >>> original = YAPFileManager("config.json")
            >>> copy = original.clone()
            >>> copy.path != original.path  # Different temporary file
        """
        # Import here to avoid circular import
        from yapfm.manager import YAPFileManager

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=self.path.suffix, delete=False)
        temp_file.close()

        # Copy the file if it exists
        if self.exists():
            shutil.copy2(self.path, temp_file.name)

        # Create a new manager
        clone_manager = YAPFileManager(
            temp_file.name,
            strategy=self.strategy,
            auto_create=self.auto_create,
            enable_cache=self.enable_cache,
            cache_size=self.cache_size,
            cache_ttl=self.cache_ttl,
        )

        # Copy in-memory data if loaded
        if self.is_loaded():
            clone_manager.document = self._deep_copy_dict(self.document)
            clone_manager.mark_as_loaded()

        return clone_manager

    def copy_to(
        self, destination: Union[str, Path], strategy: Optional[BaseFileStrategy] = None
    ) -> "YAPFileManager":
        """
        Copy content to another file.

        Args:
            destination: Destination file path
            strategy: Optional strategy for the destination file

        Returns:
            New YAPFileManager for the destination file

        Example:
            >>> fm.copy_to("backup.json")  # Copy to JSON
            >>> fm.copy_to("config.toml")  # Copy to TOML with auto-detection
        """
        # Import here to avoid circular import
        from yapfm.manager import YAPFileManager

        dest_path = Path(destination)

        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Create new manager for destination
        new_manager = YAPFileManager(
            dest_path,
            strategy=strategy,
            auto_create=True,
            enable_cache=self.enable_cache,
            cache_size=self.cache_size,
            cache_ttl=self.cache_ttl,
        )

        # Copy data
        if not self.is_loaded():
            self.load()

        new_manager.document = self._deep_copy_dict(self.document)
        new_manager.mark_as_loaded()
        new_manager.mark_as_dirty()
        new_manager.save()

        return new_manager

    def merge_from(
        self, source: Union[str, Path, "YAPFileManager"], strategy: str = "deep"
    ) -> None:
        """
        Merge from another file or manager.

        Args:
            source: Source file or YAPFileManager
            strategy: Merge strategy ("deep", "shallow", "replace")

        Example:
            >>> fm.merge_from("override.json", strategy="deep")
            >>> fm.merge_from(other_manager, strategy="replace")
        """
        # Import here to avoid circular import
        from yapfm.manager import YAPFileManager
        from yapfm.multi_file import MergeStrategy, load_and_merge

        # Load source data
        if isinstance(source, YAPFileManager):
            source_data = source.data
        else:
            source_data = load_and_merge([source], strategy=MergeStrategy.DEEP)

        # Load current data
        if not self.is_loaded():
            self.load()

        # Apply merge strategy
        if strategy == "deep":
            from yapfm.helpers import deep_merge

            self.document = deep_merge(self.document, source_data)
        elif strategy == "shallow":
            self.document.update(source_data)
        elif strategy == "replace":
            self.document = source_data
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")

        self.mark_as_dirty()

    def _deep_copy_dict(self, data: Any) -> Any:
        """Create a deep copy of data structure."""
        if isinstance(data, dict):
            return {key: self._deep_copy_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._deep_copy_dict(item) for item in data]
        else:
            return data
