"""
Decorators for file manager operations.
"""

from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, Union

from .exceptions import FileReadError, FileWriteError

T = TypeVar("T")


def handle_file_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to wrap file operations with consistent error handling.

    Args:
        func (Callable[..., T]): The function to wrap.

    Returns:
        Callable[..., T]: The wrapped function.

    Raises:
        FileReadError: If the file is not found.
        FileWriteError: If the file is not writable.
        Exception: If there is an error during the file operation.
    """

    @wraps(func)
    def wrapper(file_path: Union[str, Path], *args: Any, **kwargs: Any) -> T:
        """Wrapper to wrap file operations with consistent error handling.

        Args:
            file_path (Union[str, Path]): The path to the file.
            *args: The arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.
        """
        file_path = Path(file_path)
        try:
            return func(file_path, *args, **kwargs)
        except FileNotFoundError:
            raise FileReadError("File not found", file_path)
        except PermissionError:
            raise FileWriteError("Permission denied", file_path)
        except Exception as e:
            if "save" in func.__name__:
                raise FileWriteError(str(e), file_path)
            else:
                raise FileReadError(str(e), file_path)

    return wrapper
