from pathlib import Path
from typing import Optional, Union

from yapfm.strategies import BaseFileStrategy


class YAPFileManager:
    def __init__(
        self,
        path: Union[str, Path],
        strategy: Optional[BaseFileStrategy] = None,
        *,
        auto_create: bool = False,
    ):
        self.path = Path(path)
        self.strategy = strategy
        self.auto_create = auto_create

    pass
