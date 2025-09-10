"""
Utility functions.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union


def split_dot_key(dot_key: str) -> Tuple[List[str], str]:
    """
    Split a dot-separated key into a list of strings and the last part.
    """
    parts = dot_key.split(".")
    return parts[:-1], parts[-1]


def join_dot_key(path: List[str], key_name: str) -> str:
    """
    Join a list of strings with a dot separator.
    """
    return ".".join(path + [key_name])


def open_file(  # type: ignore
    path: Union[str, Path], format: Optional[str] = None, auto_create: bool = False
):
    """
    Open a configuration file with the appropriate strategy.

    Args:
        path: Path to the file
        format: Optional format override (e.g. "toml", "json", "yaml").
                If provided, will select the strategy based on this format instead of the file extension.

    Returns:
        FileManager instance
    """
    # Import here to avoid circular import
    from yapfm.manager import YAPFileManager

    path = Path(path)

    # Optional: force the extension if format provided
    if format:
        # Strip whitespace and handle empty format
        format = format.strip()
        if format:
            ext = f".{format.lower().lstrip('.')}"
            path = path.with_suffix(ext)

    # FileManager detects the strategy automatically via FileStrategyRegistry
    return YAPFileManager(path, strategy=None, auto_create=auto_create)
