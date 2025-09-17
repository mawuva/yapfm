"""
Registry for file strategies with thread-safe operations.

This module provides a centralized registry for managing file strategies that can handle
different file formats. The registry includes features such as:
  - Thread-safe strategy registration and retrieval
  - Support for multiple file extensions per strategy
  - Automatic strategy instantiation
  - Format validation and support checking

The registry is designed to be used as a singleton with class-level methods,
ensuring thread safety and global access to registered strategies.

Example:
    >>> from yapfm.registry import FileStrategyRegistry
    >>> from yapfm.strategies import JsonStrategy
    >>>
    >>> # Register a strategy for multiple extensions
    >>> FileStrategyRegistry.register_strategy([".json", ".jsonc"], JsonStrategy)
    >>>
    >>> # Get a strategy instance
    >>> strategy = FileStrategyRegistry.get_strategy("config.json")
    >>>
    >>> # Check supported formats
    >>> formats = FileStrategyRegistry.get_supported_formats()
    >>> print(f"Supported: {formats}")
"""

from threading import RLock
from typing import Callable, Dict, List, Optional, Type, Union

from regify import Registry

from yapfm.strategies.base import BaseFileStrategy
from yapfm.helpers import resolve_file_extension


class FileStrategyRegistry:
    """Registry specialized for file strategies (singleton style)."""

    _registry: Registry = Registry("file_strategies")
    _lock = RLock()

    @classmethod
    def register_strategy(
        cls, file_exts: Union[str, List[str]], strategy_cls: Type[BaseFileStrategy]
    ) -> None:
        """
        Register one or multiple extensions for a strategy class.

        Args:
            file_ext: File extension to register the strategy for.
            strategy_cls: Strategy class to register.
        """

        if isinstance(file_exts, str):
            file_exts = [file_exts]

        with cls._lock:
            for ext in file_exts:
                ext = resolve_file_extension(ext)
                cls._registry.add(ext, strategy_cls)

    @classmethod
    def unregister_strategy(cls, file_ext: str) -> None:
        """
        Unregister a strategy for a file extension.

        Args:
            file_ext: File extension to unregister the strategy for.

        Example:
            registry.unregister_strategy("toml")
        """
        ext = resolve_file_extension(file_ext)

        with cls._lock:
            cls._registry.unregister(ext)

    @classmethod
    def get_strategy(cls, file_ext_or_path: str) -> Optional[BaseFileStrategy]:
        """
        Get a strategy for a file extension or path.

        Args:
            file_ext_or_path: File extension or path to get the strategy for.

        Returns:
            Optional[BaseFileStrategy]: The strategy for the file extension or path.
        """
        ext = resolve_file_extension(file_ext_or_path)

        with cls._lock:
            try:
                strategy_cls = cls._registry.get(ext)
                return strategy_cls() if strategy_cls else None
            except KeyError:
                return None

    @classmethod
    def list_strategies(cls) -> Dict[str, Type[BaseFileStrategy]]:
        """List all registered strategies."""
        with cls._lock:
            return cls._registry.list()

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get the supported formats for all registered strategies."""
        with cls._lock:
            return list(cls._registry.keys())

    @classmethod
    def is_format_supported(cls, file_ext: str) -> bool:
        """Check if a format is supported."""
        ext = resolve_file_extension(file_ext)
        with cls._lock:
            return ext in cls._registry.keys()


def register_file_strategy(
    file_exts: Union[str, List[str]],
    registry: Type[FileStrategyRegistry] = FileStrategyRegistry,
) -> Callable[[Type[BaseFileStrategy]], Type[BaseFileStrategy]]:
    """
    Decorator to register a strategy for one or more formats into the given registry.
    If no registry is provided, use the default global one.

    Args:
        file_exts: The extensions to register the strategy for.
        registry: The registry to register the strategy for.

    Example:
        @register_file_strategy(".toml", FileStrategyRegistry)
        class TomlStrategy: ...
    """

    def decorator(cls: Type[BaseFileStrategy]) -> Type[BaseFileStrategy]:
        registry.register_strategy(file_exts, cls)
        return cls

    return decorator
