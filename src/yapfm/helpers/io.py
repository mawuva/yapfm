"""
I/O Helper Functions

This module provides utility functions for file I/O operations.
It includes functions for loading, saving, and managing file operations
with proper error handling and type safety.

Key Functions:
- load_file: Generic file loading with custom parser
- save_file: Generic file saving with custom serializer
- load_file_with_stream: Stream-based file loading
- save_file_with_stream: Stream-based file saving
"""

from pathlib import Path
from typing import Any, Callable, TypeVar, Union

from yapfm.decorators import handle_file_errors

T = TypeVar("T")


@handle_file_errors
def load_file(file_path: Union[Path, str], parser_func: Callable[[str], T]) -> T:
    """
    Generic function to load and parse a file using a provided parser function.

    This function reads a file from disk and applies a custom parser function
    to convert the raw content into the desired data structure. It includes
    automatic error handling for common file operations.

    Args:
        file_path (Union[str, Path]): Path to the file to load.
        parser_func (Callable[[str], T]): Function to parse the file content.
            Should take a string and return the parsed data.

    Returns:
        T: Parsed file content of type T.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the file cannot be read.
        ValueError: If the parser function fails.

    Example:
        >>> import json
        >>> from yapfm.helpers.io import load_file
        >>>
        >>> # Load JSON file
        >>> data = load_file("config.json", json.loads)
        >>> print(data["database"]["host"])
        >>>
        >>> # Load with custom parser
        >>> def parse_config(content):
        ...     return {"raw": content, "lines": content.splitlines()}
        >>>
        >>> config = load_file("config.txt", parse_config)
        >>> print(f"Lines: {len(config['lines'])}")
    """
    file_path = Path(file_path)
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()
        return parser_func(content)


@handle_file_errors
def load_file_with_stream(
    file_path: Union[Path, str], parser_func: Callable[[Any], T]
) -> T:
    """
    Generic function to load and parse a file using a provided parser function
    that works with file streams.

    Args:
        file_path (Union[str, Path]): Path to the file.
        parser_func (Callable[[Any], T]): Function to parse the file stream.

    Returns:
        T: Parsed file content.
    """
    file_path = Path(file_path)
    with file_path.open("r", encoding="utf-8") as f:
        return parser_func(f)


@handle_file_errors
def save_file(
    file_path: Union[Path, str], data: Any, serializer_func: Callable[[Any], str]
) -> None:
    """
    Generic function to save data to a file using a provided serializer function
    that converts data to string content.

    Args:
        file_path (Union[str, Path]): Path to the file.
        data (Any): Data to save.
        serializer_func (Callable[[Any], str]): Function to serialize data to string.

    Returns:
        None

    Raises:
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the file cannot be written.
        ValueError: If the serializer function fails.

    Example:
        >>> from yapfm.helpers.io import save_file
        >>> import json
        >>>
        >>> # Save JSON file
        >>> save_file("output.json", data, json.dumps)
        >>>
        >>> # Save with custom serializer
        >>> def serialize_data(data):
        ...     return json.dumps(data, indent=4)
        >>>
        >>> save_file("output.json", data, serialize_data)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        f.write(serializer_func(data))


@handle_file_errors
def save_file_with_stream(
    file_path: Union[Path, str], data: Any, writer_func: Callable[[Any, Any], None]
) -> None:
    """
    Generic function to save data to a file using a provided writer function
    that works with file streams.

    Args:
        file_path (Union[str, Path]): Path to the file.
        data (Any): Data to save.
        writer_func (Callable[[Any, Any], None]): Function to write data to file stream.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        writer_func(data, f)
