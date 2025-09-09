"""
TOML File Strategy

This module provides the strategy for handling TOML (Tom's Obvious, Minimal Language)
files. It uses the tomlkit library for parsing and writing TOML files with
preservation of comments and formatting.

Key Features:
- Full TOML specification support
- Comment and formatting preservation
- Type-safe operations with tomlkit
- Automatic registration with the strategy registry
- Support for nested tables and arrays

Example:
    >>> from yapfm.strategies.toml_strategy import TomlStrategy
    >>> from pathlib import Path
    >>>
    >>> strategy = TomlStrategy()
    >>>
    >>> # Load TOML file
    >>> data = strategy.load("config.toml")
    >>> print(data["database"]["host"])
    >>>
    >>> # Save TOML file
    >>> data["database"]["port"] = 5432
    >>> strategy.save("config.toml", data)
    >>>
    >>> # Navigate document structure
    >>> value = strategy.navigate(data, ["database", "host"])
    >>> print(value)
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, cast

from tomlkit import TOMLDocument
from tomlkit import dumps as toml_dumps
from tomlkit import parse as toml_parse
from tomlkit import table as toml_table
from tomlkit.items import Table

from yapfm.helpers import load_file, save_file
from yapfm.registry import register_file_strategy

TomlLike = Union[TOMLDocument, Table]


@register_file_strategy(".toml")
class TomlStrategy:
    def load(self, file_path: Union[Path, str]) -> TOMLDocument:
        """
        Load a TOML file and parse it into a TOMLDocument.

        Args:
            file_path (Union[str, Path]): Path to the TOML file.

        Returns:
            TOMLDocument: Parsed TOML content.

        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: If there is an error reading or parsing the file.
        """
        return load_file(file_path, toml_parse)

    def save(
        self, file_path: Union[Path, str], data: Union[Dict, TOMLDocument]
    ) -> None:
        """
        Save a TOML file ensuring proper directory creation and formatting.
        Adds a double newline at the end of the file.

        Args:
            file_path (Union[str, Path]): Path to write the TOML file.
            data (Union[Dict, TOMLDocument]): TOML content to save.

        Raises:
            PermissionError: If the file cannot be written due to permissions.
            Exception: If there is an error during writing.
        """

        def toml_serializer(data_to_save: Union[Dict, TOMLDocument]) -> str:
            text = toml_dumps(data_to_save)

            if not text.endswith("\n"):
                text += "\n"
            if not text.endswith("\n\n"):
                text += "\n"

            return text

        save_file(file_path, data, toml_serializer)

    def navigate(
        self, document: TomlLike, path: List[str], create: bool = False
    ) -> Optional[TomlLike]:
        """
        Descend into the TOML structure, optionally creating intermediate tables.

        Args:
            path (List[str]): The path to the key.
            create (bool): Whether to create intermediate tables if they don't exist.

        Returns:
            Optional[TomlLike]: The current node in the TOML structure.
            None if the path doesn't exist and create is False.
        """

        current = document

        for part in path:
            if part not in current or not isinstance(
                current[part], (TOMLDocument, Table)
            ):
                if create:
                    current[part] = toml_table()
                else:
                    return None
            current = cast(TomlLike, current[part])
        return current
