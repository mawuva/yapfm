"""
Base File Strategy Protocol

This module defines the abstract base protocol for all file handling strategies.
It provides the interface that all concrete strategies must implement to handle
different file formats (JSON, YAML, TOML, etc.).

Key Features:
- Protocol-based interface for type safety
- Standardized load/save operations
- Document navigation capabilities
- Extensible design for new file formats

Example:
    >>> from yapfm.strategies import BaseFileStrategy
    >>> from pathlib import Path
    >>>
    >>> class MyStrategy(BaseFileStrategy):
    ...     def load(self, file_path):
    ...         # Load data from file
    ...         return data
    ...
    ...     def save(self, file_path, data):
    ...         # Save data to file
    ...         pass
    ...
    ...     def navigate(self, document, path, create=False):
    ...         # Navigate through document structure
    ...         return value
"""

from pathlib import Path
from typing import Any, List, Optional, Protocol, Union


class BaseFileStrategy(Protocol):
    def load(self, file_path: Union[Path, str]) -> Any:
        """
        Load data from a file.

        This method reads the file from disk and returns its parsed contents.
        The exact format of the returned data depends on the file type and
        the specific strategy implementation.

        Args:
            file_path (Union[Path, str]): Path to the file to load.

        Returns:
            Any: The parsed file contents, typically a dictionary or list.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is invalid.

        Example:
            >>> strategy = TomlStrategy()
            >>> data = strategy.load("config.toml")
            >>> print(data["database"]["host"])
        """
        ...

    def save(self, file_path: Union[Path, str], data: Any) -> None:
        """
        Save data to a file.

        This method writes the provided data to the specified file path.
        The data will be serialized according to the file format supported
        by this strategy.

        Args:
            file_path (Union[Path, str]): Path where to save the file.
            data (Any): The data to save, typically a dictionary or list.

        Raises:
            PermissionError: If the file cannot be written due to permissions.
            ValueError: If the data cannot be serialized to the target format.

        Example:
            >>> strategy = TomlStrategy()
            >>> data = {"database": {"host": "localhost", "port": 5432}}
            >>> strategy.save("config.toml", data)
        """
        ...

    def navigate(
        self, document: Any, path: List[str], create: bool = False
    ) -> Optional[Any]:
        """
        Navigate through the document structure.

        This method traverses the document structure using the provided path
        and returns the value at that location. If the path doesn't exist
        and create is True, it will create the necessary intermediate structures.

        Args:
            document (Any): The document to navigate through.
            path (List[str]): List of keys representing the path to traverse.
            create (bool): Whether to create missing intermediate structures.

        Returns:
            Optional[Any]: The value at the specified path, or None if not found
            and create is False.

        Example:
            >>> strategy = TomlStrategy()
            >>> document = {"database": {"host": "localhost"}}
            >>> value = strategy.navigate(document, ["database", "host"])
            >>> print(value)  # "localhost"
            >>>
            >>> # Create missing path
            >>> value = strategy.navigate(document, ["cache", "redis"], create=True)
            >>> print(document)  # {"database": {...}, "cache": {"redis": None}}
        """
        ...
