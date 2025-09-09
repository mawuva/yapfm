"""
Registry for file strategies with thread-safe operations and usage tracking.

This module provides a centralized registry for managing file strategies that can handle
different file formats. The registry includes advanced features such as:
  - Thread-safe strategy registration and retrieval
  - Usage counters for performance monitoring
  - Tracking of skipped/unsupported files
  - Support for multiple file extensions per strategy
  - Automatic strategy instantiation
  - Statistics and reporting capabilities

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
    >>>
    >>> # Get usage statistics
    >>> stats = FileStrategyRegistry.get_registry_stats()
    >>> print(f"Usage: {stats['counters']}")
"""

from collections import defaultdict
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from .strategies import BaseFileStrategy

T = TypeVar("T")


class FileStrategyRegistry:
    _strategy_map: Dict[str, Type[BaseFileStrategy]] = {}
    _counter: Dict[str, int] = defaultdict(int)
    _skipped: Dict[str, List[str]] = defaultdict(list)
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

        Raises:
            TypeError: If the strategy does not inherit from BaseFileStrategy.

        Example:
            registry.register_strategy("toml", TomlStrategy)
        """

        if isinstance(file_exts, str):
            file_exts = [file_exts]

        with cls._lock:
            for ext in file_exts:
                ext = ext.lower()

                if not ext.startswith("."):
                    ext = f".{ext}"

                cls._strategy_map[ext] = strategy_cls
                cls._counter.setdefault(ext, 0)

    @classmethod
    def unregister_strategy(cls, file_ext: str) -> None:
        """
        Unregister a strategy for a file extension.

        Args:
            file_ext: File extension to unregister the strategy for.

        Example:
            registry.unregister_strategy("toml")
        """
        ext = file_ext.lower()

        if not ext.startswith("."):
            ext = f".{ext}"

        with cls._lock:
            cls._strategy_map.pop(ext, None)
            cls._counter.pop(ext, None)
            cls._skipped.pop(ext, None)

    @classmethod
    def get_strategy(cls, file_ext_or_path: str) -> Optional[BaseFileStrategy]:
        """
        Get a strategy for a file extension or path.

        Args:
            file_ext_or_path: File extension or path to get the strategy for.

        Returns:
            Optional[BaseFileStrategy]: The strategy for the file extension or path.
        """
        # Handle both file paths and direct extensions
        if file_ext_or_path.startswith("."):
            # Direct extension like '.toml'
            ext = file_ext_or_path.lower()
        else:
            # File path like 'example.toml'
            ext = Path(file_ext_or_path).suffix.lower()

        with cls._lock:
            strategy_cls = cls._strategy_map.get(ext)

            if strategy_cls:
                cls._counter[ext] += 1
                return strategy_cls()
            else:
                cls._skipped["unknown"].append(file_ext_or_path)
        return None

    @classmethod
    def list_strategies(cls) -> Dict[str, Type[BaseFileStrategy]]:
        """List all registered strategies."""
        with cls._lock:
            return cls._strategy_map.copy()

    @classmethod
    def get_counters(cls) -> Dict[str, int]:
        """Get the counters for all registered strategies."""
        with cls._lock:
            return dict(cls._counter)

    @classmethod
    def get_skipped(cls) -> Dict[str, List[str]]:
        """Get the skipped files for all registered strategies"""
        with cls._lock:
            return dict(cls._skipped)

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get the supported formats for all registered strategies."""
        with cls._lock:
            return list(cls._strategy_map.keys())

    @classmethod
    def is_format_supported(cls, file_ext: str) -> bool:
        """Check if a format is supported."""
        with cls._lock:
            return file_ext.lower() in [fmt[1:] for fmt in cls._strategy_map.keys()]

    @classmethod
    def get_registry_stats(cls) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dict[str, Any]: Registry statistics including counters and skipped files

        Example:
            stats = FileStrategyRegistry.get_registry_stats()
            # Returns: {'counters': {...}, 'skipped': {...}}
        """
        with cls._lock:
            return {
                "counters": cls.get_counters(),
                "skipped": cls.get_skipped(),
                "supported_formats": cls.get_supported_formats(),
            }

    @classmethod
    def display_summary(cls) -> None:
        """Print a styled summary of counters and skipped files."""
        with cls._lock:
            print("🎯 Registered Strategies & Usage Summary")
            print("-" * 50)
            for ext, strategy_cls in cls._strategy_map.items():
                count = cls._counter.get(ext, 0)
                print(f"{ext:10} -> {strategy_cls.__name__:20} | Used: {count}")
            if cls._skipped:
                print("\n⚠️ Skipped files:")
                for key, files in cls._skipped.items():
                    print(f"{key}: {len(files)} files -> {files}")


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
