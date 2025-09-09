"""
YAML File Strategy

This module provides the strategy for handling YAML (YAML Ain't Markup Language)
files. It uses the PyYAML library for parsing and writing YAML files with
safe loading and dumping capabilities.

Key Features:
- Safe YAML parsing with PyYAML
- Support for both .yaml and .yml extensions
- Automatic registration with the strategy registry
- Support for nested structures and arrays
- Type-safe operations

Example:
    >>> from yapfm.strategies.yaml_strategy import YamlStrategy
    >>> from pathlib import Path
    >>>
    >>> strategy = YamlStrategy()
    >>>
    >>> # Load YAML file
    >>> data = strategy.load("config.yaml")
    >>> print(data["database"]["host"])
    >>>
    >>> # Save YAML file
    >>> data["database"]["port"] = 5432
    >>> strategy.save("config.yaml", data)
    >>>
    >>> # Navigate document structure
    >>> value = strategy.navigate(data, ["database", "host"])
    >>> print(value)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from yaml import safe_dump as yaml_safe_dump
from yaml import safe_load as yaml_safe_load

from yapfm.helpers import (
    load_file_with_stream,
    navigate_dict_like,
    save_file_with_stream,
)
from yapfm.registry import register_file_strategy


@register_file_strategy([".yaml", ".yml"])
class YamlStrategy:
    def load(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """
        Load a YAML file and parse it into a Python object.

        Args:
            file_path (Union[str, Path]): Path to the YAML file.
        """
        return load_file_with_stream(file_path, yaml_safe_load)

    def save(self, file_path: Union[Path, str], data: Dict[str, Any]) -> None:
        """
        Save a dictionary to a YAML file.

        Args:
            file_path (Union[str, Path]): Path to the YAML file.
            data (Dict): Dictionary to save.
        """

        def yaml_writer(data_to_write: Dict[str, Any], file_stream: Any) -> None:
            yaml_safe_dump(data_to_write, file_stream, encoding="utf-8")

        save_file_with_stream(file_path, data, yaml_writer)

    def navigate(
        self, document: Dict[str, Any], path: List[str], create: bool = False
    ) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """
        Descend into the YAML structure, optionally creating intermediate dicts.

        Args:
            path (List[str]): The path to the key.
            create (bool): Whether to create intermediate dicts if they don't exist.
        """
        return navigate_dict_like(document, path, create)
