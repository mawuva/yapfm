"""
Unit tests for file_manager_error exceptions.
"""

from yapfm.exceptions.file_manager_error import (
    FileManagerError,
    KeyNotFoundError,
    LoadFileError,
    StrategyError,
)


class TestFileManagerError:
    """Test cases for FileManagerError base exception."""

    def test_file_manager_error_initialization(self) -> None:
        """
        Scenario: Initialize FileManagerError with message

        Expected:
        - Should create exception with correct message
        - Should inherit from Exception
        - Should be instantiable without additional parameters
        """
        message = "File manager error occurred"

        error = FileManagerError(message)

        assert isinstance(error, Exception)
        assert str(error) == message

    def test_file_manager_error_with_empty_message(self) -> None:
        """
        Scenario: Initialize FileManagerError with empty message

        Expected:
        - Should create exception with empty message
        - Should not raise additional exceptions
        - Should be valid exception instance
        """
        error = FileManagerError("")

        assert isinstance(error, Exception)
        assert str(error) == ""

    def test_file_manager_error_with_none_message(self) -> None:
        """
        Scenario: Initialize FileManagerError with None message

        Expected:
        - Should create exception with None message
        - Should convert None to string representation
        - Should not raise additional exceptions
        """
        error = FileManagerError(None)

        assert isinstance(error, Exception)
        assert str(error) == "None"

    def test_file_manager_error_inheritance(self) -> None:
        """
        Scenario: Test FileManagerError inheritance

        Expected:
        - Should inherit from Exception
        - Should be catchable as Exception
        - Should be catchable as FileManagerError
        """
        error = FileManagerError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, FileManagerError)

        # Test exception catching
        try:
            raise error
        except Exception as e:
            assert e is error
        except FileManagerError as e:
            assert e is error


class TestLoadFileError:
    """Test cases for LoadFileError exception."""

    def test_load_file_error_initialization(self) -> None:
        """
        Scenario: Initialize LoadFileError with message

        Expected:
        - Should create exception with correct message
        - Should inherit from FileManagerError
        - Should inherit from Exception
        """
        message = "Failed to load file"

        error = LoadFileError(message)

        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)
        assert str(error) == message

    def test_load_file_error_inheritance_chain(self) -> None:
        """
        Scenario: Test LoadFileError inheritance chain

        Expected:
        - Should inherit from FileManagerError
        - Should inherit from Exception
        - Should be catchable at any level in the hierarchy
        """
        error = LoadFileError("Load failed")

        assert isinstance(error, LoadFileError)
        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)

        # Test catching at different levels
        try:
            raise error
        except LoadFileError as e:
            assert e is error
        except FileManagerError as e:
            assert e is error
        except Exception as e:
            assert e is error

    def test_load_file_error_with_detailed_message(self) -> None:
        """
        Scenario: Test LoadFileError with detailed error message

        Expected:
        - Should preserve detailed error message
        - Should handle multi-line messages
        - Should maintain message formatting
        """
        detailed_message = (
            "Failed to load file: Invalid JSON format at line 5, column 12"
        )

        error = LoadFileError(detailed_message)

        assert str(error) == detailed_message
        assert "Invalid JSON format" in str(error)


class TestStrategyError:
    """Test cases for StrategyError exception."""

    def test_strategy_error_initialization(self) -> None:
        """
        Scenario: Initialize StrategyError with message

        Expected:
        - Should create exception with correct message
        - Should inherit from FileManagerError
        - Should inherit from Exception
        """
        message = "Strategy not found"

        error = StrategyError(message)

        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)
        assert str(error) == message

    def test_strategy_error_inheritance_chain(self) -> None:
        """
        Scenario: Test StrategyError inheritance chain

        Expected:
        - Should inherit from FileManagerError
        - Should inherit from Exception
        - Should be catchable at any level in the hierarchy
        """
        error = StrategyError("Strategy failed")

        assert isinstance(error, StrategyError)
        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)

        # Test catching at different levels
        try:
            raise error
        except StrategyError as e:
            assert e is error
        except FileManagerError as e:
            assert e is error
        except Exception as e:
            assert e is error

    def test_strategy_error_with_strategy_name(self) -> None:
        """
        Scenario: Test StrategyError with specific strategy name

        Expected:
        - Should preserve strategy name in message
        - Should handle strategy-specific error details
        - Should maintain error context
        """
        strategy_name = "JsonStrategy"
        message = f"Strategy {strategy_name} failed to process file"

        error = StrategyError(message)

        assert str(error) == message
        assert strategy_name in str(error)


class TestKeyNotFoundError:
    """Test cases for KeyNotFoundError exception."""

    def test_key_not_found_error_initialization(self) -> None:
        """
        Scenario: Initialize KeyNotFoundError with message

        Expected:
        - Should create exception with correct message
        - Should inherit from FileManagerError
        - Should inherit from Exception
        """
        message = "Key not found in document"

        error = KeyNotFoundError(message)

        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)
        assert str(error) == message

    def test_key_not_found_error_inheritance_chain(self) -> None:
        """
        Scenario: Test KeyNotFoundError inheritance chain

        Expected:
        - Should inherit from FileManagerError
        - Should inherit from Exception
        - Should be catchable at any level in the hierarchy
        """
        error = KeyNotFoundError("Key not found")

        assert isinstance(error, KeyNotFoundError)
        assert isinstance(error, FileManagerError)
        assert isinstance(error, Exception)

        # Test catching at different levels
        try:
            raise error
        except KeyNotFoundError as e:
            assert e is error
        except FileManagerError as e:
            assert e is error
        except Exception as e:
            assert e is error

    def test_key_not_found_error_with_key_path(self) -> None:
        """
        Scenario: Test KeyNotFoundError with specific key path

        Expected:
        - Should preserve key path in message
        - Should handle nested key paths
        - Should maintain navigation context
        """
        key_path = "user.profile.settings.theme"
        message = f"Key '{key_path}' not found in document"

        error = KeyNotFoundError(message)

        assert str(error) == message
        assert key_path in str(error)


class TestExceptionIntegration:
    """Integration tests for file manager exceptions."""

    def test_exception_hierarchy_consistency(self) -> None:
        """
        Scenario: Test that all exceptions follow proper hierarchy

        Expected:
        - All specific exceptions should inherit from FileManagerError
        - All exceptions should inherit from Exception
        - Hierarchy should be consistent across all exception types
        """
        exceptions = [
            FileManagerError("Base error"),
            LoadFileError("Load error"),
            StrategyError("Strategy error"),
            KeyNotFoundError("Key error"),
        ]

        for error in exceptions:
            assert isinstance(error, Exception)
            assert isinstance(error, FileManagerError)

            # Test that specific exceptions are also their specific type
            if isinstance(error, LoadFileError):
                assert isinstance(error, LoadFileError)
            elif isinstance(error, StrategyError):
                assert isinstance(error, StrategyError)
            elif isinstance(error, KeyNotFoundError):
                assert isinstance(error, KeyNotFoundError)

    def test_exception_raising_and_catching_specific(self) -> None:
        """
        Scenario: Test raising and catching specific exceptions

        Expected:
        - Should be able to catch specific exception types
        - Should be able to catch base exception types
        - Should maintain exception information
        """
        # Test LoadFileError
        try:
            raise LoadFileError("File load failed")
        except LoadFileError as e:
            assert "File load failed" in str(e)
        except FileManagerError as e:
            assert "File load failed" in str(e)
        except Exception as e:
            assert "File load failed" in str(e)

        # Test StrategyError
        try:
            raise StrategyError("Strategy failed")
        except StrategyError as e:
            assert "Strategy failed" in str(e)
        except FileManagerError as e:
            assert "Strategy failed" in str(e)
        except Exception as e:
            assert "Strategy failed" in str(e)

    def test_exception_equality_and_identity(self) -> None:
        """
        Scenario: Test exception equality and identity

        Expected:
        - Different instances should not be equal
        - Same instance should be equal to itself
        - Exceptions should be distinguishable by type
        """
        error1 = LoadFileError("Error 1")
        error2 = LoadFileError("Error 2")
        error3 = StrategyError("Error 3")

        assert error1 != error2
        assert error1 == error1
        assert error1 is not error2
        assert not isinstance(error1, StrategyError)
        assert isinstance(error1, LoadFileError)
        assert isinstance(error3, StrategyError)

    def test_exception_with_special_characters(self) -> None:
        """
        Scenario: Test exceptions with special characters in messages

        Expected:
        - Should handle special characters correctly
        - Should preserve message formatting
        - Should not cause encoding issues
        """
        special_message = "Error with special chars: àéîöü 中文 🚀"

        error = LoadFileError(special_message)

        assert str(error) == special_message
        assert "àéîöü" in str(error)
        assert "中文" in str(error)
        assert "🚀" in str(error)
