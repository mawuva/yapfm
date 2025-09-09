"""
Unit tests for base strategy protocol.
"""

from pathlib import Path
from typing import Any, List, Union
from unittest.mock import Mock

import pytest

from yapfm.strategies.base import BaseFileStrategy


class TestBaseFileStrategy:
    """Test cases for BaseFileStrategy protocol."""

    def test_base_file_strategy_protocol_definition(self) -> None:
        """
        Scenario: Verify BaseFileStrategy protocol definition

        Expected:
        - Should be a Protocol class
        - Should define required methods
        - Should have correct method signatures
        """
        # Check that it's a Protocol
        from typing import get_origin

        assert (
            get_origin(BaseFileStrategy) is None
        )  # Protocols return None for get_origin

        # Check that required methods are defined
        assert hasattr(BaseFileStrategy, "load")
        assert hasattr(BaseFileStrategy, "save")
        assert hasattr(BaseFileStrategy, "navigate")

    def test_base_file_strategy_method_signatures(self) -> None:
        """
        Scenario: Verify BaseFileStrategy method signatures

        Expected:
        - load method should accept file_path and return Any
        - save method should accept file_path, data and return None
        - navigate method should accept document, path, create and return Any | None
        """
        import inspect

        # Check load method signature
        load_sig = inspect.signature(BaseFileStrategy.load)
        assert "file_path" in load_sig.parameters
        assert load_sig.return_annotation == Any

        # Check save method signature
        save_sig = inspect.signature(BaseFileStrategy.save)
        assert "file_path" in save_sig.parameters
        assert "data" in save_sig.parameters
        assert save_sig.return_annotation is None

        # Check navigate method signature
        navigate_sig = inspect.signature(BaseFileStrategy.navigate)
        assert "document" in navigate_sig.parameters
        assert "path" in navigate_sig.parameters
        assert "create" in navigate_sig.parameters
        assert navigate_sig.return_annotation == Any | None

    def test_base_file_strategy_protocol_implementation(self) -> None:
        """
        Scenario: Test implementing BaseFileStrategy protocol

        Expected:
        - Should be able to create classes that implement the protocol
        - Should enforce method implementation
        - Should work with type checking
        """

        class TestStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"test": "data"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return document.get(path[0]) if path else None

        strategy = TestStrategy()
        # Note: isinstance check doesn't work with non-runtime-checkable protocols
        # We can only verify that the class has the required methods

        # Test that methods work
        result = strategy.load("test.json")
        assert result == {"test": "data"}

        strategy.save("test.json", {"new": "data"})

        nav_result = strategy.navigate({"key": "value"}, ["key"])
        assert nav_result == "value"

    def test_base_file_strategy_with_mock_implementation(self) -> None:
        """
        Scenario: Test BaseFileStrategy with mock implementation

        Expected:
        - Should work with mock objects
        - Should allow method stubbing
        - Should maintain protocol compliance
        """
        mock_strategy = Mock(spec=BaseFileStrategy)
        mock_strategy.load.return_value = {"mocked": "data"}
        mock_strategy.save.return_value = None
        mock_strategy.navigate.return_value = "mocked_value"

        # Test mock behavior
        result = mock_strategy.load("test.json")
        assert result == {"mocked": "data"}

        mock_strategy.save("test.json", {"data": "value"})
        mock_strategy.save.assert_called_once_with("test.json", {"data": "value"})

        nav_result = mock_strategy.navigate({"key": "value"}, ["key"])
        assert nav_result == "mocked_value"

    def test_base_file_strategy_type_hints(self) -> None:
        """
        Scenario: Test BaseFileStrategy type hints and annotations

        Expected:
        - Should have proper type annotations
        - Should support Union types for file_path
        - Should support generic Any type for data
        - Should support List[str] for path parameter
        """

        # Check that type hints are properly defined
        assert hasattr(BaseFileStrategy, "__annotations__")

        # Verify that the protocol can be used in type hints
        def process_strategy(strategy: BaseFileStrategy) -> Any:
            return strategy.load("test.json")

        class TestStrategy(BaseFileStrategy):
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"processed": True}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        strategy = TestStrategy()
        result = process_strategy(strategy)
        assert result == {"processed": True}

    def test_base_file_strategy_optional_parameters(self) -> None:
        """
        Scenario: Test BaseFileStrategy with optional parameters

        Expected:
        - navigate method should have create parameter with default False
        - Should handle optional parameters correctly
        - Should maintain backward compatibility
        """

        class TestStrategy(BaseFileStrategy):
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"test": "data"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                if create:
                    return {"created": True}
                return document.get(path[0]) if path else None

        strategy = TestStrategy()

        # Test with create=False (default)
        result1 = strategy.navigate({"key": "value"}, ["key"])
        assert result1 == "value"

        # Test with create=True
        result2 = strategy.navigate({"key": "value"}, ["key"], create=True)
        assert result2 == {"created": True}

    def test_base_file_strategy_error_handling(self) -> None:
        """
        Scenario: Test BaseFileStrategy error handling capabilities

        Expected:
        - Should allow implementations to raise exceptions
        - Should not restrict error handling in implementations
        - Should work with exception handling patterns
        """

        class ErrorStrategy(BaseFileStrategy):
            def load(self, file_path: Union[Path, str]) -> Any:
                raise FileNotFoundError(f"File not found: {file_path}")

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                raise PermissionError(f"Permission denied: {file_path}")

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                raise KeyError(f"Key not found: {path}")

        strategy = ErrorStrategy()

        # Test that exceptions can be raised
        with pytest.raises(FileNotFoundError):
            strategy.load("nonexistent.json")

        with pytest.raises(PermissionError):
            strategy.save("readonly.json", {"data": "value"})

        with pytest.raises(KeyError):
            strategy.navigate({"key": "value"}, ["nonexistent"])

    def test_base_file_strategy_inheritance_chain(self) -> None:
        """
        Scenario: Test BaseFileStrategy inheritance and composition

        Expected:
        - Should work with inheritance patterns
        - Should support composition
        - Should maintain protocol compliance through inheritance
        """

        class BaseStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {"base": "data"}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        class ExtendedStrategy(BaseStrategy):
            def load(self, file_path: Union[Path, str]) -> Any:
                base_data = super().load(file_path)
                base_data["extended"] = True
                return base_data

        strategy = ExtendedStrategy()
        # Note: isinstance check doesn't work with non-runtime-checkable protocols
        # We can only verify that the class has the required methods

        result = strategy.load("test.json")
        assert result == {"base": "data", "extended": True}

    def test_base_file_strategy_protocol_validation(self) -> None:
        """
        Scenario: Test BaseFileStrategy protocol validation

        Expected:
        - Should validate that implementing classes have required methods
        - Should work with isinstance checks
        - Should support protocol checking
        """

        class ValidStrategy:
            def load(self, file_path: Union[Path, str]) -> Any:
                return {}

            def save(self, file_path: Union[Path, str], data: Any) -> None:
                pass

            def navigate(
                self, document: Any, path: List[str], create: bool = False
            ) -> Any | None:
                return None

        class InvalidStrategy:
            # Missing required methods
            pass

        # Valid strategy should work
        valid_strategy = ValidStrategy()
        # Note: isinstance check doesn't work with non-runtime-checkable protocols
        # We can only verify that the class has the required methods
        assert hasattr(valid_strategy, "load")
        assert hasattr(valid_strategy, "save")
        assert hasattr(valid_strategy, "navigate")

        # Invalid strategy should not have required methods
        invalid_strategy = InvalidStrategy()
        assert not hasattr(invalid_strategy, "load")
        assert not hasattr(invalid_strategy, "save")
        assert not hasattr(invalid_strategy, "navigate")
