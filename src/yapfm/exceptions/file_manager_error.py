"""
File Manager Exceptions

This module defines custom exceptions for the FileManager system.
It provides specific exception types for different error conditions
that can occur during file operations.

Key Exceptions:
- FileManagerError: Base exception for all FileManager errors
- LoadFileError: Raised when a file cannot be loaded
- StrategyError: Raised when a strategy fails or is not found
- KeyNotFoundError: Raised when a requested key is not found

Example:
    >>> from yapfm.exceptions.file_manager_error import FileManagerError, LoadFileError
    >>>
    >>> try:
    ...     # Some file operation
    ...     pass
    ... except LoadFileError as e:
    ...     print(f"Failed to load file: {e}")
    ... except FileManagerError as e:
    ...     print(f"FileManager error: {e}")
"""


class FileManagerError(Exception):
    """
    Base exception for FileManager errors.
    """


class LoadFileError(FileManagerError):
    """
    Raised when a file cannot be loaded.
    """


class StrategyError(FileManagerError):
    """
    Raised when a strategy fails or is not found.
    """


class KeyNotFoundError(FileManagerError):
    """
    Raised when a requested key is not found.
    """
