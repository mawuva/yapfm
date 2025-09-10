from pathlib import Path
from typing import Any, Optional, Union

from yapfm.strategies import BaseFileStrategy

from .exceptions import StrategyError
from .helpers import validate_strategy
from .mixins.file_operations_mixin import FileOperationsMixin
from .registry import FileStrategyRegistry


class YAPFileManager(
    FileOperationsMixin,
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

        super().__init__(**kwargs)

    pass
