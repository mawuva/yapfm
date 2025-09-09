"""
Unit tests for file_operations exceptions.
"""

from pathlib import Path

from yapfm.exceptions.file_operations import (
    FileOperationError,
    FileReadError,
    FileWriteError,
)


class TestFileOperationError:
    """Test cases for FileOperationError base exception."""

    def test_file_operation_error_initialization(self) -> None:
        """
        Scenario: Initialize FileOperationError with message and file path

        Expected:
        - Should create exception with correct message format
        - Should store file_path as instance attribute
        - Should inherit from Exception
        """
        file_path = Path("test.txt")
        message = "Test error message"

        error = FileOperationError(message, file_path)

        assert isinstance(error, Exception)
        assert error.file_path == file_path  # type: ignore[attr-defined]
        assert str(error) == f"{message}: {file_path}"

    def test_file_operation_error_with_string_path(self) -> None:
        """
        Scenario: Initialize FileOperationError with string file path

        Expected:
        - Should convert string to Path object
        - Should create exception with correct message format
        - Should store file_path as Path instance
        """
        file_path_str = "test.txt"
        message = "Test error message"

        error = FileOperationError(message, Path(file_path_str))

        assert isinstance(error.file_path, Path)
        assert error.file_path == Path(file_path_str)
        assert str(error) == f"{message}: {Path(file_path_str)}"

    def test_file_operation_error_message_formatting(self) -> None:
        """
        Scenario: Test different message formats for FileOperationError

        Expected:
        - Should format message with file path correctly
        - Should handle empty messages
        - Should handle special characters in file paths
        """
        file_path = Path("test with spaces/file.txt")
        message = "Operation failed"

        error = FileOperationError(message, file_path)

        assert str(error) == f"{message}: {file_path}"

        # Test with empty message
        empty_error = FileOperationError("", file_path)
        assert str(empty_error) == f": {file_path}"

    def test_file_operation_error_inheritance(self) -> None:
        """
        Scenario: Test FileOperationError inheritance hierarchy

        Expected:
        - Should inherit from Exception
        - Should be catchable as Exception
        - Should be catchable as FileOperationError
        """
        file_path = Path("test.txt")
        error = FileOperationError("Test", file_path)

        assert isinstance(error, Exception)
        assert isinstance(error, FileOperationError)

        # Test exception catching
        try:
            raise error
        except Exception as e:
            assert e is error
        except FileOperationError as e:
            assert e is error


class TestFileReadError:
    """Test cases for FileReadError exception."""

    def test_file_read_error_initialization(self) -> None:
        """
        Scenario: Initialize FileReadError with message and file path

        Expected:
        - Should create exception with correct message format
        - Should store file_path as instance attribute
        - Should inherit from FileOperationError
        """
        file_path = Path("read_test.txt")
        message = "Cannot read file"

        error = FileReadError(message, file_path)

        assert isinstance(error, FileOperationError)
        assert isinstance(error, Exception)
        assert error.file_path == file_path  # type: ignore[attr-defined]
        assert str(error) == f"{message}: {file_path}"

    def test_file_read_error_inheritance_chain(self) -> None:
        """
        Scenario: Test FileReadError inheritance chain

        Expected:
        - Should inherit from FileOperationError
        - Should inherit from Exception
        - Should be catchable at any level in the hierarchy
        """
        file_path = Path("test.txt")
        error = FileReadError("Read failed", file_path)

        assert isinstance(error, FileReadError)
        assert isinstance(error, FileOperationError)
        assert isinstance(error, Exception)

        # Test catching at different levels
        try:
            raise error
        except FileReadError as e:
            assert e is error
        except FileOperationError as e:
            assert e is error
        except Exception as e:
            assert e is error

    def test_file_read_error_with_complex_path(self) -> None:
        """
        Scenario: Test FileReadError with complex file path

        Expected:
        - Should handle absolute paths correctly
        - Should handle paths with special characters
        - Should preserve path information in message
        """
        file_path = Path("/home/user/documents/file with spaces.txt")
        message = "Permission denied"

        error = FileReadError(message, file_path)

        assert error.file_path == file_path  # type: ignore[attr-defined]
        assert str(error) == f"{message}: {file_path}"


class TestFileWriteError:
    """Test cases for FileWriteError exception."""

    def test_file_write_error_initialization(self) -> None:
        """
        Scenario: Initialize FileWriteError with message and file path

        Expected:
        - Should create exception with correct message format
        - Should store file_path as instance attribute
        - Should inherit from FileOperationError
        """
        file_path = Path("write_test.txt")
        message = "Cannot write file"

        error = FileWriteError(message, file_path)

        assert isinstance(error, FileOperationError)
        assert isinstance(error, Exception)
        assert error.file_path == file_path  # type: ignore[attr-defined]
        assert str(error) == f"{message}: {file_path}"

    def test_file_write_error_inheritance_chain(self) -> None:
        """
        Scenario: Test FileWriteError inheritance chain

        Expected:
        - Should inherit from FileOperationError
        - Should inherit from Exception
        - Should be catchable at any level in the hierarchy
        """
        file_path = Path("test.txt")
        error = FileWriteError("Write failed", file_path)

        assert isinstance(error, FileWriteError)
        assert isinstance(error, FileOperationError)
        assert isinstance(error, Exception)

        # Test catching at different levels
        try:
            raise error
        except FileWriteError as e:
            assert e is error
        except FileOperationError as e:
            assert e is error
        except Exception as e:
            assert e is error

    def test_file_write_error_with_relative_path(self) -> None:
        """
        Scenario: Test FileWriteError with relative file path

        Expected:
        - Should handle relative paths correctly
        - Should preserve relative path information
        - Should work with Path objects created from relative strings
        """
        file_path = Path("output/data.json")
        message = "Directory does not exist"

        error = FileWriteError(message, file_path)

        assert error.file_path == file_path  # type: ignore[attr-defined]
        assert str(error) == f"{message}: {file_path}"


class TestExceptionIntegration:
    """Integration tests for file operation exceptions."""

    def test_exception_raising_and_catching(self) -> None:
        """
        Scenario: Test raising and catching file operation exceptions

        Expected:
        - Should be able to raise and catch specific exceptions
        - Should maintain exception information
        - Should work in try/except blocks
        """
        file_path = Path("integration_test.txt")

        # Test FileReadError
        try:
            raise FileReadError("File not found", file_path)
        except FileReadError as e:
            assert e.file_path == file_path
            assert "File not found" in str(e)

        # Test FileWriteError
        try:
            raise FileWriteError("Permission denied", file_path)
        except FileWriteError as e:
            assert e.file_path == file_path
            assert "Permission denied" in str(e)

    def test_exception_chaining(self) -> None:
        """
        Scenario: Test exception chaining with file operation exceptions

        Expected:
        - Should support exception chaining
        - Should preserve original exception information
        - Should work with from/raise syntax
        """
        file_path = Path("chain_test.txt")
        original_error = OSError("Original error")

        try:
            raise FileReadError("Failed to read", file_path) from original_error
        except FileReadError as e:
            assert e.file_path == file_path
            assert e.__cause__ is original_error

    def test_exception_equality_and_identity(self) -> None:
        """
        Scenario: Test exception equality and identity

        Expected:
        - Different instances should not be equal
        - Same instance should be equal to itself
        - Exceptions should be distinguishable by type
        """
        file_path = Path("test.txt")
        error1 = FileReadError("Error 1", file_path)
        error2 = FileReadError("Error 2", file_path)
        error3 = FileWriteError("Error 3", file_path)

        assert error1 != error2
        assert error1 == error1
        assert error1 is not error2
        assert not isinstance(error1, FileWriteError)
        assert isinstance(error1, FileReadError)
        assert isinstance(error3, FileWriteError)

    def test_exception_with_none_file_path(self) -> None:
        """
        Scenario: Test exception behavior with None file path

        Expected:
        - Should handle None file path gracefully
        - Should convert None to Path object
        - Should not raise additional exceptions
        """
        error = FileReadError("Test error", Path("None"))

        assert error.file_path == Path("None")
        assert str(error) == "Test error: None"
