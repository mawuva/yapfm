from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from yapfm.cache import LazySectionLoader, SmartCache
from yapfm.strategies import BaseFileStrategy

from .exceptions import StrategyError
from .helpers import validate_strategy
from .mixins import (
    CacheMixin,
    ContextMixin,
    FileOperationsMixin,
    KeyOperationsMixin,
    LazySectionsMixin,
    SectionOperationsMixin,
    StreamingMixin,
)
from .registry import FileStrategyRegistry


class YAPFileManager(
    FileOperationsMixin,
    ContextMixin,
    KeyOperationsMixin,
    SectionOperationsMixin,
    CacheMixin,
    LazySectionsMixin,
    StreamingMixin,
):
    unified_cache: Optional[SmartCache]

    def __init__(
        self,
        path: Union[str, Path],
        strategy: Optional[BaseFileStrategy] = None,
        *,
        auto_create: bool = False,
        enable_context: bool = True,
        enable_cache: bool = True,
        cache_size: int = 1000,  # default 1000 keys
        cache_ttl: Optional[float] = 3600,  # 1 hour
        enable_streaming: bool = False,
        enable_lazy_loading: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the FileManager with mixins.
        """
        # Set up path and strategy
        self.path = Path(path)

        if strategy is None:
            strategy = FileStrategyRegistry.get_strategy(self.path.suffix.lower())
            if strategy is None:
                raise StrategyError(
                    f"No strategy found for extension: {self.path.suffix}"
                )

        self.strategy = strategy
        validate_strategy(strategy)
        self.auto_create = auto_create
        self.document: Dict[str, Any] = {}

        # Initialize file state
        self._loaded = False
        self._dirty = False

        # Store cache configuration
        self.enable_cache = enable_cache
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.enable_lazy_loading = enable_lazy_loading

        # Initialize unified cache system
        self._init_unified_cache()

        super().__init__(**kwargs)

    def _init_unified_cache(self) -> None:
        """Initialize the unified cache system."""
        # Unified cache for all operations
        if self.enable_cache:
            self.unified_cache = SmartCache(
                max_size=self.cache_size, default_ttl=self.cache_ttl, track_stats=True
            )
        else:
            self.unified_cache = None

        # Lazy loaders for sections only
        self._lazy_sections: Dict[str, LazySectionLoader] = {}

    def get_cache(self) -> Optional[SmartCache]:
        """Get the unified cache."""
        if self.enable_cache:
            return self.unified_cache
        return None

    def _generate_cache_key(
        self,
        dot_key: Optional[str],
        path: Optional[List[str]],
        key_name: Optional[str],
        key_type: str = "key",
    ) -> str:
        """Generate a cache key from the key parameters."""
        if dot_key is not None:
            return f"{key_type}:{dot_key}"
        elif path is not None and key_name is not None:
            path_str = ".".join(path) if path else ""
            return (
                f"{key_type}:{path_str}.{key_name}"
                if path_str
                else f"{key_type}:{key_name}"
            )
        else:
            raise ValueError("Cannot generate cache key without key parameters")

    @property
    def data(self) -> Dict[str, Any]:
        """
        Get the file data, loading it if necessary.

        Returns:
            Dictionary containing the file data

        Note:
            This property automatically loads the file on first access
            if it hasn't been loaded yet.
        """
        self.load_if_not_loaded()
        return self.document

    @data.setter
    def data(self, value: Dict[str, Any]) -> None:
        """
        Set the file data.

        Args:
            value: Dictionary containing the data to set

        Raises:
            TypeError: If value is not a dictionary
        """
        if not isinstance(value, dict):
            raise TypeError("Data must be a dictionary")
        self.document = value
        self.mark_as_loaded()
        self.mark_as_dirty()
