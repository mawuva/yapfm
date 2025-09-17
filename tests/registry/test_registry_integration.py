"""
Registry integration tests.

This module contains tests for the FileStrategyRegistry class.
"""

import threading
from pathlib import Path
from typing import Any, Generator

import pytest

from yapfm.registry import FileStrategyRegistry, register_file_strategy
from yapfm.strategies import BaseFileStrategy


# --- stratégies factices pour test ---
class DummyJsonStrategy(BaseFileStrategy):
    def load(self, file_path: Path | str) -> Any:
        return {"dummy": "json"}

    def save(self, file_path: Path | str, data: Any) -> None:
        pass

    def navigate(
        self, document: Any, path: list[str], create: bool = False
    ) -> Any | None:
        return document.get(path[0]) if path else None


class DummyTomlStrategy(BaseFileStrategy):
    def load(self, file_path: Path | str) -> Any:
        return {"dummy": "toml"}

    def save(self, file_path: Path | str, data: Any) -> None:
        pass

    def navigate(
        self, document: Any, path: list[str], create: bool = False
    ) -> Any | None:
        return document.get(path[0]) if path else None


@pytest.fixture(autouse=True)
def clean_registry() -> Generator[None, None, None]:
    """
    Scenario: Clean registry state before and after each integration test

    Expected:
    - Registry should be completely cleared before each test
    - Registry should be cleaned up after each test
    - No state should persist between integration tests
    """
    FileStrategyRegistry._registry.clear()
    yield
    FileStrategyRegistry._registry.clear()


# --- tests d’intégration ---


def test_register_and_get_strategy_by_extension() -> None:
    """
    Scenario: Register and retrieve strategy using file extension

    Expected:
    - Strategy should be registered successfully
    - Strategy instance should be returned when retrieved
    """
    FileStrategyRegistry.register_strategy(".json", DummyJsonStrategy)

    strategy = FileStrategyRegistry.get_strategy(".json")
    assert isinstance(strategy, DummyJsonStrategy)


def test_register_and_get_strategy_by_filename() -> None:
    """
    Scenario: Register and retrieve strategy using file path

    Expected:
    - Strategy should be registered successfully
    - Extension should be extracted from file path correctly
    - Strategy instance should be returned when retrieved
    """
    FileStrategyRegistry.register_strategy(".toml", DummyTomlStrategy)

    strategy = FileStrategyRegistry.get_strategy("config.toml")
    assert isinstance(strategy, DummyTomlStrategy)


def test_multiple_extensions_for_one_strategy() -> None:
    """
    Scenario: Register one strategy for multiple file extensions

    Expected:
    - Strategy should be registered for all specified extensions
    - All extensions should point to the same strategy class
    - Both extensions should work independently
    """
    FileStrategyRegistry.register_strategy([".json", ".jsonc"], DummyJsonStrategy)

    s1 = FileStrategyRegistry.get_strategy("file.json")
    s2 = FileStrategyRegistry.get_strategy("file.jsonc")

    assert isinstance(s1, DummyJsonStrategy)
    assert isinstance(s2, DummyJsonStrategy)


def test_unsupported_files_return_none() -> None:
    """
    Scenario: Handle files that cannot be handled by any strategy

    Expected:
    - Unsupported files should return None when retrieved
    - Registry should remain in consistent state
    """
    FileStrategyRegistry.register_strategy(".toml", DummyTomlStrategy)

    result = FileStrategyRegistry.get_strategy("unknown.yaml")
    assert result is None


def test_unregister_strategy_removes_it() -> None:
    """
    Scenario: Unregister a strategy and verify it's completely removed

    Expected:
    - Strategy should be removed from registry after unregistration
    - Attempting to retrieve unregistered strategy should return None
    - Strategy should not appear in list of registered strategies
    - Registry should be in consistent state after unregistration
    """
    FileStrategyRegistry.register_strategy(".json", DummyJsonStrategy)
    FileStrategyRegistry.unregister_strategy(".json")

    strategy = FileStrategyRegistry.get_strategy("file.json")
    assert strategy is None

    assert ".json" not in FileStrategyRegistry.list_strategies()


def test_supported_formats_and_is_format_supported() -> None:
    """
    Scenario: Test format support checking functionality

    Expected:
    - get_supported_formats should return list of all registered extensions
    - is_format_supported should return True for registered formats
    - is_format_supported should return False for unregistered formats
    - Extension normalization should work correctly
    """
    FileStrategyRegistry.register_strategy([".json", ".toml"], DummyJsonStrategy)

    supported = FileStrategyRegistry.get_supported_formats()
    assert ".json" in supported
    assert ".toml" in supported

    assert FileStrategyRegistry.is_format_supported("json") is True
    assert FileStrategyRegistry.is_format_supported("yaml") is False


def test_register_file_strategy_decorator() -> None:
    """
    Scenario: Use decorator to register a strategy with custom registry

    Expected:
    - Decorator should register strategy in specified registry
    - Decorated strategy should be retrievable after registration
    - Strategy should maintain its original functionality
    - Registry should contain the decorated strategy
    """

    @register_file_strategy(".json", FileStrategyRegistry)
    class DecoratedJsonStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"decorated": True}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    strategy = FileStrategyRegistry.get_strategy("test.json")
    assert isinstance(strategy, DecoratedJsonStrategy)


def test_thread_safety_with_multiple_threads() -> None:
    """
    Scenario: Test thread safety with multiple concurrent threads accessing the registry

    Expected:
    - Multiple threads should be able to access the registry simultaneously
    - No race conditions should occur during concurrent access
    - All threads should complete successfully without errors
    """
    FileStrategyRegistry.register_strategy(".json", DummyJsonStrategy)

    def worker() -> None:
        for _ in range(100):
            s = FileStrategyRegistry.get_strategy("data.json")
            assert isinstance(s, DummyJsonStrategy)

    threads = [threading.Thread(target=worker) for _ in range(10)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
