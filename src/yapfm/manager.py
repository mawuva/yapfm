from pathlib import Path
from typing import Any, Dict, Optional, Union

from yapfm.strategies import BaseFileStrategy

from .exceptions import StrategyError
from .helpers import validate_strategy
from .mixins import (
    ContextMixin,
    FileOperationsMixin,
    KeyOperationsMixin,
    SectionOperationsMixin,
)
from .registry import FileStrategyRegistry


class YAPFileManager(
    FileOperationsMixin,
    ContextMixin,
    KeyOperationsMixin,
    SectionOperationsMixin,
):
    def __init__(
        self,
        path: Union[str, Path],
        strategy: Optional[BaseFileStrategy] = None,
        *,
        auto_create: bool = False,
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

        super().__init__(**kwargs)

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
