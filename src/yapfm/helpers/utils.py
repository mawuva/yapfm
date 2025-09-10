"""
Utility functions.
"""

from typing import List, Tuple


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
