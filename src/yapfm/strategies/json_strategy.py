"""
JSON File Strategy

This module provides the strategy for handling JSON files.
It uses the standard json library for parsing and writing JSON files.

Example:
    >>> from yapfm.strategies.json_strategy import JsonStrategy
    >>> strategy = JsonStrategy()
    >>> data = strategy.load(Path('config.json'))
    >>> strategy.save(Path('output.json'), data)
"""

from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from yapfm.helpers import load_file, navigate_dict_like, save_file
from yapfm.registry import register_file_strategy


@register_file_strategy(".json")
class JsonStrategy:
    def load(self, file_path: Union[Path, str]) -> Union[Dict[str, Any], List[Any]]:
        """
        Load data from a JSON file.

        Args:
            file_path (Union[str, Path]): Path to the JSON file.
        """
        return load_file(file_path, json_loads)

    def save(
        self, file_path: Union[Path, str], data: Union[Dict[str, Any], List[Any]]
    ) -> None:
        """
        Save data to a JSON file.

        Args:
            file_path (Union[str, Path]): Path to the JSON file.
            data (Union[Dict[str, Any], List[Any]]): Data to save.
        """

        def json_serializer(data_to_save: Union[Dict[str, Any], List[Any]]) -> str:
            return json_dumps(data_to_save, indent=2, ensure_ascii=False)

        save_file(file_path, data, json_serializer)

    def navigate(
        self, document: Union[Dict, List], path: List[str], create: bool = False
    ) -> Optional[Union[Dict, List]]:
        """
        Navigate through the JSON document.
        Descend into the JSON structure, optionally creating intermediate dicts.

        Args:
            document (Union[Dict, List]): The JSON document to navigate.
            path (List[str]): The path to the key.
            create (bool): Whether to create intermediate dicts if they don't exist.
        """
        return navigate_dict_like(document, path, create)
