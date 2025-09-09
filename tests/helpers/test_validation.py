"""
Unit tests for validation module.
"""

# mypy: disable-error-code=arg-type

from pathlib import Path
from typing import Any, List, Union
from unittest.mock import Mock

import pytest

from yapfm.helpers.validation import validate_strategy
from yapfm.strategies.base import BaseFileStrategy


class TestValidateStrategy:
    """Test cases for validate_strategy function."""

    def test_validate_strategy_with_valid_strategy(self) -> None:
        """
        Scenario: Validate a strategy that implements all required methods

        Expected:
        - Should not raise any exception
        - Should complete validation successfully
        - Should accept valid strategy implementations
        """

        class ValidStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        strategy = ValidStrategy()

        # Should not raise any exception
        validate_strategy(strategy)

    def test_validate_strategy_with_mock_strategy(self) -> None:
        """
        Scenario: Validate a mock strategy that implements all required methods

        Expected:
        - Should not raise any exception
        - Should work with mock objects
        - Should accept mock strategy implementations
        """
        mock_strategy = Mock(spec=BaseFileStrategy)
        mock_strategy.load.return_value = {"mocked": "data"}
        mock_strategy.save.return_value = None
        mock_strategy.navigate.return_value = "mocked_value"

        # Should not raise any exception
        validate_strategy(mock_strategy)

    def test_validate_strategy_missing_load_method(self) -> None:
        """
        Scenario: Validate a strategy missing the load method

        Expected:
        - Should raise TypeError
        - Should indicate missing load method
        - Should provide clear error message
        """

        class InvalidStrategy:
            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        strategy = InvalidStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_missing_save_method(self) -> None:
        """
        Scenario: Validate a strategy missing the save method

        Expected:
        - Should raise TypeError
        - Should indicate missing save method
        - Should provide clear error message
        """

        class InvalidStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        strategy = InvalidStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_missing_navigate_method(self) -> None:
        """
        Scenario: Validate a strategy missing the navigate method

        Expected:
        - Should raise TypeError
        - Should indicate missing navigate method
        - Should provide clear error message
        """

        class InvalidStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

        strategy = InvalidStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_missing_multiple_methods(self) -> None:
        """
        Scenario: Validate a strategy missing multiple required methods

        Expected:
        - Should raise TypeError
        - Should indicate missing methods
        - Should provide clear error message
        """

        class InvalidStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            # Missing save and navigate methods

        strategy = InvalidStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_no_methods(self) -> None:
        """
        Scenario: Validate a strategy with no required methods

        Expected:
        - Should raise TypeError
        - Should indicate missing all methods
        - Should provide clear error message
        """

        class InvalidStrategy:
            pass

        strategy = InvalidStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_none_strategy(self) -> None:
        """
        Scenario: Validate None as strategy

        Expected:
        - Should raise TypeError
        - Should handle None input gracefully
        - Should provide clear error message
        """
        with pytest.raises(TypeError) as exc_info:
            validate_strategy(None)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_string_strategy(self) -> None:
        """
        Scenario: Validate a string as strategy

        Expected:
        - Should raise TypeError
        - Should handle non-object input gracefully
        - Should provide clear error message
        """
        with pytest.raises(TypeError) as exc_info:
            validate_strategy("not_a_strategy")

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_integer_strategy(self) -> None:
        """
        Scenario: Validate an integer as strategy

        Expected:
        - Should raise TypeError
        - Should handle non-object input gracefully
        - Should provide clear error message
        """
        with pytest.raises(TypeError) as exc_info:
            validate_strategy(42)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_partial_implementation(self) -> None:
        """
        Scenario: Validate a strategy with only some required methods

        Expected:
        - Should raise TypeError
        - Should detect incomplete implementation
        - Should provide clear error message
        """

        class PartialStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            # Missing navigate method

        strategy = PartialStrategy()

        with pytest.raises(TypeError) as exc_info:
            validate_strategy(strategy)

        assert "Strategy must implement BaseFileStrategy protocol" in str(
            exc_info.value
        )

    def test_validate_strategy_with_extra_methods(self) -> None:
        """
        Scenario: Validate a strategy with all required methods plus extra methods

        Expected:
        - Should not raise any exception
        - Should accept strategies with additional methods
        - Should only validate required methods
        """

        class ExtendedStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"data": "test"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

            def extra_method(self) -> str:
                return "extra"

            def another_method(self, param: int) -> bool:
                return True

        strategy = ExtendedStrategy()

        # Should not raise any exception
        validate_strategy(strategy)

    def test_validate_strategy_with_different_method_signatures(self) -> None:
        """
        Scenario: Validate a strategy with different method signatures but correct names

        Expected:
        - Should not raise any exception
        - Should only check method existence, not signatures
        - Should accept strategies with different parameter types
        """

        class DifferentSignatureStrategy:
            def load(self, file_path: str) -> dict:  # Different parameter type
                return {"data": "test"}

            def save(
                self, file_path: str, data: dict
            ) -> None:  # Different parameter types
                pass

            def navigate(
                self, document: dict, path: list, create: bool = True
            ) -> str | None:  # Different types
                return None

        strategy = DifferentSignatureStrategy()

        # Should not raise any exception (only checks method existence)
        validate_strategy(strategy)

    def test_validate_strategy_with_callable_attributes(self) -> None:
        """
        Scenario: Validate a strategy where methods are callable attributes

        Expected:
        - Should not raise any exception
        - Should work with callable attributes
        - Should accept various method implementations
        """

        class CallableAttributeStrategy:
            def __init__(self) -> None:
                self.load = lambda file_path: {"data": "test"}
                self.save = lambda file_path, data: None
                self.navigate = lambda document, path, create=False: None

        strategy = CallableAttributeStrategy()

        # Should not raise any exception
        validate_strategy(strategy)

    def test_validate_strategy_error_message_consistency(self) -> None:
        """
        Scenario: Test that error messages are consistent across different failure cases

        Expected:
        - Should always raise TypeError
        - Should always use the same error message
        - Should provide consistent error handling
        """
        error_cases = [
            None,
            "string",
            42,
            object(),
            type("EmptyClass", (), {})(),
        ]

        for case in error_cases:
            with pytest.raises(TypeError) as exc_info:
                validate_strategy(case)

            assert "Strategy must implement BaseFileStrategy protocol" in str(
                exc_info.value
            )

    def test_validate_strategy_with_real_strategy_implementations(self) -> None:
        """
        Scenario: Validate actual strategy implementations from the codebase

        Expected:
        - Should not raise any exception for real strategies
        - Should work with actual strategy classes
        - Should validate real implementations correctly
        """
        # Import actual strategies
        from yapfm.strategies.json_strategy import JsonStrategy
        from yapfm.strategies.toml_strategy import TomlStrategy
        from yapfm.strategies.yaml_strategy import YamlStrategy

        strategies = [
            JsonStrategy(),
            TomlStrategy(),
            YamlStrategy(),
        ]

        for strategy in strategies:
            # Should not raise any exception
            validate_strategy(strategy)
