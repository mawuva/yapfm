"""
Merge Strategies Module

This module contains all the merge strategy implementations using the Strategy pattern.
Each strategy defines how multiple files should be merged into a single dictionary.

Available Strategies:
- DeepMergeStrategy: Recursive deep merge of dictionaries
- NamespaceMergeStrategy: Merge files into separate namespaces
- PriorityMergeStrategy: Merge with priority-based overwriting
- AppendMergeStrategy: Append values to lists
- ReplaceMergeStrategy: Complete replacement with last file
- ConditionalMergeStrategy: Merge based on conditions

Example:
    >>> from yapfm.multi_file.strategies import DeepMergeStrategy
    >>>
    >>> strategy = DeepMergeStrategy()
    >>> result = strategy.merge([
    ...     (Path("file1.json"), {"a": {"b": 1}}),
    ...     (Path("file2.json"), {"a": {"c": 2}})
    ... ])
    >>> # Result: {"a": {"b": 1, "c": 2}}
"""

from .append import AppendMergeStrategy
from .base import BaseMergeStrategy
from .conditional import ConditionalMergeStrategy
from .deep import DeepMergeStrategy
from .namespace import NamespaceMergeStrategy
from .priority import PriorityMergeStrategy
from .replace import ReplaceMergeStrategy

__all__ = [
    "BaseMergeStrategy",
    "DeepMergeStrategy",
    "NamespaceMergeStrategy",
    "PriorityMergeStrategy",
    "AppendMergeStrategy",
    "ReplaceMergeStrategy",
    "ConditionalMergeStrategy",
]
