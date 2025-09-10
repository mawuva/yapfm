# Import all strategies to register them automatically
from . import json_strategy, toml_strategy, yaml_strategy  # noqa: F401
from .base import BaseFileStrategy

__all__ = ["BaseFileStrategy"]
