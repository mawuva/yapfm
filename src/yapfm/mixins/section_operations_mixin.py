"""
Section Operations Mixin

This module provides section operations for FileManager.
The SectionOperationsMixin contains operations for manipulating entire sections
using dot notation and path-based access.
"""

# mypy: ignore-errors

from typing import Any, Dict, List, Optional

from tomlkit import TOMLDocument
from tomlkit.items import Table

from yapfm.helpers import merge_toml


class SectionOperationsMixin:
    """
    Mixin for section operations.
    """

    def set_section(
        self,
        data: Dict[str, Any],
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        overwrite: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Set an entire section in the file.

        Args:
            data (Dict[str, Any]): The section data.
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the section.
            key_name (Optional[str]): The name of the section.
            overwrite (bool): Whether to overwrite the existing section.

        Example:
            >>> fm.set_section({"database": {"host": "localhost", "port": 5432}}, dot_key="database")
            >>> fm.set_section({"database": {"host": "localhost", "port": 5432}}, path=["database"])
        """

        if not self.is_loaded():
            self.load()

        result = self.resolve_and_navigate(dot_key, path, key_name, create=True)
        if result is None:
            raise ValueError("Could not navigate to the specified path")

        parent, key_name = result

        if key_name in parent:
            existing_value = parent[key_name]

            if isinstance(existing_value, (TOMLDocument, Table)):
                merge_toml(existing_value, data, overwrite=overwrite)
            else:
                parent[key_name] = data
        else:
            parent[key_name] = data
        self.mark_as_dirty()

    def get_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
        **kwargs: Any,
    ) -> Any:
        """
        Get an entire section from the file.

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the section.
            key_name (Optional[str]): The name of the section.
            default (Any): The default value if the section is not found.

        Example:
            >>> section = fm.get_section(dot_key="database", default={"host": "localhost", "port": 5432})
            >>> section = fm.get_section(path=["database"], key_name="database", default={"host": "localhost", "port": 5432})
        """

        if not self.is_loaded():
            self.load()

        result = self.resolve_and_navigate(dot_key, path, key_name)
        if result is None:
            return default

        parent, key_name = result

        return parent.get(key_name, default) if isinstance(parent, dict) else default

    def delete_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """Delete an entire section from the file."""
        return self.delete_key(dot_key, path=path, key_name=key_name)

    def has_section(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """Check if a section exists in the file."""
        return self.has_key(dot_key, path=path, key_name=key_name)

    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all keys in the file with optional prefix.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of key paths

        Note:
            This is a basic implementation. More sophisticated key listing
            may be implemented by specific strategies if needed.

        Example:
            # List all keys
            all_keys = manager.list_keys()

            # List keys with prefix
            tool_keys = manager.list_keys("tool")
        """
        if not prefix:
            return list(self.data.keys())

        # Filter keys that start with prefix
        prefix_parts = prefix.split(".")
        current = self.data

        # Navigate to prefix location
        for part in prefix_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return []

        # Return keys at this level
        if isinstance(current, dict):
            return [f"{prefix}.{key}" for key in current.keys()]
        return []
