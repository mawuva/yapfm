"""
Key Operations Mixin

This module provides key operations for FileManager.
The KeyOperationsMixin contains operations for manipulating individual keys
using dot notation and path-based access.
"""

# mypy: ignore-errors

from typing import Any, List, Optional, Tuple

from yapfm.helpers import split_dot_key


class KeyOperationsMixin:
    """
    Mixin for key operations.
    """

    def resolve(
        self, dot_key: Optional[str], path: Optional[List[str]], key_name: Optional[str]
    ) -> Tuple[List[str], str]:
        """
        Resolve input: either dot_key or (path + key_name).

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.

        Returns:
            Tuple[List[str], str]: The path and key_name.

        Raises:
            ValueError: If neither dot_key nor (path + key_name) is provided.
        """
        if dot_key is not None:
            return split_dot_key(dot_key)
        if path is not None and key_name is not None:
            return path, key_name
        raise ValueError("You must provide either dot_key or (path + key_name)")

    def resolve_and_navigate(
        self,
        dot_key: Optional[str],
        path: Optional[List[str]],
        key_name: Optional[str],
        create: bool = False,
    ) -> Optional[Tuple[Any, str]]:
        """
        Resolve input and navigate to the parent node.

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.
            create (bool): Whether to create intermediate dicts if they don't exist.

        Returns:
            Optional[Tuple[Any, str]]: The parent node and the key name, or None if path doesn't exist.
        """
        path, key_name = self.resolve(dot_key, path, key_name)
        parent = self.strategy.navigate(self.document, path, create=create)
        if parent is None:
            return None
        return parent, key_name

    def set_key(
        self,
        value: Any,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        overwrite: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Set a value in the file using dot notation.

        Args:
            value (Any): The value to set.
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.
            overwrite (bool): Whether to overwrite the existing value.

        Example:
            >>> fm.set_key("localhost", dot_key="database.host")
            >>> fm.set_key(5432, path=["database"], key_name="port")
        """

        if not self.is_loaded():
            self.load()

        # Use the helper method to resolve and navigate
        result = self.resolve_and_navigate(dot_key, path, key_name, create=True)
        if result is None:
            raise ValueError("Could not navigate to the specified path")

        parent, key_name = result

        if isinstance(parent, dict):
            if overwrite or key_name not in parent:
                parent[key_name] = value
        elif hasattr(parent, "__setitem__"):  # works for Table and list
            if isinstance(parent, list):
                idx = int(key_name)

                while len(parent) <= idx:
                    parent.append(None)
                if overwrite or parent[idx] is None:
                    parent[idx] = value
            else:
                parent[key_name] = value
        self.mark_as_dirty()

    def get_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
        default: Any = None,
        **kwargs: Any,
    ) -> Any:
        """
        Get a value from the file using dot notation.

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.
            default (Any): The default value if the key is not found.

        Returns:
            The value at the specified path or default

        Example:
            >>> host = fm.get_key(dot_key="database.host", default="localhost")
            >>> port = fm.get_key(path=["database"], key_name="port", default=5432)
        """
        if not self.is_loaded():
            self.load()

        result = self.resolve_and_navigate(dot_key, path, key_name, create=False)

        if result is None:
            return default

        parent, key_name = result

        if isinstance(parent, dict):
            return parent.get(key_name, default)
        elif hasattr(parent, "get"):  # TOML Table
            return parent.get(key_name, default)
        elif isinstance(parent, list):
            try:
                idx = int(key_name)
                return parent[idx]
            except (ValueError, IndexError):
                return default
        return default

    def has_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """
        Check if a key exists in the file using dot notation.

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.

        Returns:
            True if the key exists, False otherwise

        Example:
            >>> if fm.has_key(dot_key="database.host"):
            ...     print("Database host exists")
            >>> if fm.has_key(path=["database"], key_name="port"):
            ...     print("Database port exists")
        """
        if not self.is_loaded():
            self.load()

        result = self.resolve_and_navigate(dot_key, path, key_name, create=False)

        if result is None:
            return False

        parent, key_name = result

        if isinstance(parent, dict):
            return key_name in parent
        elif isinstance(parent, list):
            try:
                idx = int(key_name)
                return 0 <= idx < len(parent)
            except ValueError:
                return False
        elif hasattr(parent, "get"):  # TOML Table
            return key_name in parent
        return False

    def delete_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """
        Delete a key from the file using dot notation.

        Args:
            dot_key (Optional[str]): The dot-separated key.
            path (Optional[List[str]]): The path to the key.
            key_name (Optional[str]): The name of the key.

        Returns:
            True if the key was deleted, False if it didn't exist

        Example:
            >>> deleted = fm.delete_key(dot_key="database.host")
            >>> deleted = fm.delete_key(path=["database"], key_name="port")
        """
        if not self.is_loaded():
            self.load()

        result = self.resolve_and_navigate(dot_key, path, key_name)

        if result is None:
            return False

        parent, key_name = result

        if isinstance(parent, dict) and key_name in parent:
            del parent[key_name]
            self.mark_as_dirty()
            return True

        elif hasattr(parent, "__delitem__"):
            try:
                if isinstance(parent, list):
                    idx = int(key_name)
                    parent.pop(idx)
                    self.mark_as_dirty()
                    return True
                else:
                    del parent[key_name]
                    self.mark_as_dirty()
                    return True
            except (ValueError, IndexError, KeyError):
                return False
        return False
