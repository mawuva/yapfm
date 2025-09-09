"""
Custom exceptions for file operations.

This module defines custom exceptions for file operations.

Key Exceptions:
- FileOperationError: Base exception for file operations
- FileReadError: Raised when a file cannot be read
- FileWriteError: Raised when a file cannot be written

Example:
    >>> from yapfm.exceptions.file_operations import FileOperationError, FileReadError, FileWriteError
    >>>
    >>> try:
    ...     # Some file operation
    ...     pass
    ... except FileOperationError as e:
    ...     print(f"File operation error: {e}")
    ... except FileReadError as e:
    ...     print(f"File read error: {e}")
    ... except FileWriteError as e:
    ...     print(f"File write error: {e}")
"""

from pathlib import Path


class FileOperationError(Exception):
    """Base exception for file operations."""

    def __init__(self, message: str, file_path: Path):
        super().__init__(f"{message}: {file_path}")
        self.file_path = file_path


class FileReadError(FileOperationError):
    """Raised when a file cannot be read."""


class FileWriteError(FileOperationError):
    """Raised when a file cannot be written."""
