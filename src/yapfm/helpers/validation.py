"""
Validation utilities.
"""

from yapfm.strategies.base import BaseFileStrategy


def validate_strategy(strategy: BaseFileStrategy) -> None:
    """
    Validate the strategy.

    Args:
        strategy (BaseFileStrategy): The strategy to validate.

    Raises:
        TypeError: If the strategy does not implement BaseFileStrategy protocol.
    """
    if (
        not hasattr(strategy, "load")
        or not hasattr(strategy, "save")
        or not hasattr(strategy, "navigate")
    ):
        raise TypeError("Strategy must implement BaseFileStrategy protocol")
