"""
YAPFM - Yet Another Python File Manager

A flexible file manager for handling various file formats (JSON, TOML, YAML, etc)
with support for strategies, mixins, and advanced features.
"""

# Import strategies to register them automatically
from . import strategies  # noqa: F401
from .manager import YAPFileManager
from .proxy import FileManagerProxy
from .registry import FileStrategyRegistry

__version__ = "1.0.0"
__all__ = [
    "YAPFileManager",
    "FileManagerProxy",
    "FileStrategyRegistry",
]
