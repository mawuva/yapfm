"""
Helper functions and utilities for file management operations.

This module provides generic utility functions for file operations that can be used
across different file formats and strategies. It includes:
  - Generic file loading and saving functions with error handling
  - Navigation utilities for dict-like structures
  - Deep merging capabilities for configuration data
  - TOML-specific merging utilities
  - Strategy validation helpers
  - Convenience functions for common operations
"""

from .dict_utils import deep_merge, navigate_dict_like
from .io import load_file, load_file_with_stream, save_file, save_file_with_stream
from .toml_merger import merge_toml
from .utils import join_dot_key, open_file, split_dot_key
from .validation import validate_strategy

__all__ = [
    # I/O functions
    "load_file",
    "load_file_with_stream",
    "save_file",
    "save_file_with_stream",
    # Dict utilities
    "navigate_dict_like",
    "deep_merge",
    # TOML utilities
    "merge_toml",
    # Validation utilities
    "validate_strategy",
    # Utility functions
    "split_dot_key",
    "join_dot_key",
    "open_file",
]
