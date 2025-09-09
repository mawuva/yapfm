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
    FileStrategyRegistry._strategy_map.clear()
    FileStrategyRegistry._counter.clear()
    FileStrategyRegistry._skipped.clear()
    yield
    FileStrategyRegistry._strategy_map.clear()
    FileStrategyRegistry._counter.clear()
    FileStrategyRegistry._skipped.clear()


# --- tests d’intégration ---


def test_register_and_get_strategy_by_extension() -> None:
    """
    Scenario: Register and retrieve strategy using file extension

    Expected:
    - Strategy should be registered successfully
    - Strategy instance should be returned when retrieved
    - Counter should be incremented after retrieval
    - Registry statistics should reflect the usage
    """
    FileStrategyRegistry.register_strategy(".json", DummyJsonStrategy)

    strategy = FileStrategyRegistry.get_strategy(".json")
    assert isinstance(strategy, DummyJsonStrategy)

    stats = FileStrategyRegistry.get_registry_stats()
    assert stats["counters"][".json"] == 1


def test_register_and_get_strategy_by_filename() -> None:
    """
    Scenario: Register and retrieve strategy using file path

    Expected:
    - Strategy should be registered successfully
    - Extension should be extracted from file path correctly
    - Strategy instance should be returned when retrieved
    - Counter should be incremented after retrieval
    """
    FileStrategyRegistry.register_strategy(".toml", DummyTomlStrategy)

    strategy = FileStrategyRegistry.get_strategy("config.toml")
    assert isinstance(strategy, DummyTomlStrategy)

    stats = FileStrategyRegistry.get_registry_stats()
    assert stats["counters"][".toml"] == 1


def test_multiple_extensions_for_one_strategy() -> None:
    """
    Scenario: Register one strategy for multiple file extensions

    Expected:
    - Strategy should be registered for all specified extensions
    - All extensions should point to the same strategy class
    - Each extension should have its own counter
    - Both extensions should work independently
    """
    FileStrategyRegistry.register_strategy([".json", ".jsonc"], DummyJsonStrategy)

    s1 = FileStrategyRegistry.get_strategy("file.json")
    s2 = FileStrategyRegistry.get_strategy("file.jsonc")

    assert isinstance(s1, DummyJsonStrategy)
    assert isinstance(s2, DummyJsonStrategy)

    stats = FileStrategyRegistry.get_registry_stats()
    assert stats["counters"][".json"] == 1
    assert stats["counters"][".jsonc"] == 1


def test_skipped_files_are_tracked() -> None:
    """
    Scenario: Track files that cannot be handled by any strategy

    Expected:
    - Unsupported files should return None when retrieved
    - Skipped files should be tracked in the registry
    - Skipped files should be accessible via get_skipped method
    - Registry should maintain list of all skipped files
    """
    FileStrategyRegistry.register_strategy(".toml", DummyTomlStrategy)

    result = FileStrategyRegistry.get_strategy("unknown.yaml")
    assert result is None

    skipped = FileStrategyRegistry.get_skipped()
    assert "unknown" in skipped
    assert "unknown.yaml" in skipped["unknown"]


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


def test_display_summary_runs_without_error(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Scenario: Test display_summary method output and functionality

    Expected:
    - display_summary should run without errors
    - Output should contain information about registered strategies
    - Output should show usage counters for strategies
    - Output should display skipped files information
    - Summary should be properly formatted and readable
    """
    FileStrategyRegistry.register_strategy(".json", DummyJsonStrategy)
    FileStrategyRegistry.get_strategy("file.json")  # incrémente compteur
    FileStrategyRegistry.get_strategy("unknown.txt")  # skip

    FileStrategyRegistry.display_summary()
    captured = capsys.readouterr()

    assert "Registered Strategies" in captured.out
    assert ".json" in captured.out
    assert "Skipped files" in captured.out


def test_thread_safety_with_multiple_threads() -> None:
    """
    Scenario: Test thread safety with multiple concurrent threads accessing the registry

    Expected:
    - Multiple threads should be able to access the registry simultaneously
    - No race conditions should occur during concurrent access
    - Counters should accurately reflect the total number of strategy retrievals
    - All threads should complete successfully without errors
    - Final counter value should equal the total number of operations across all threads
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

    # On doit avoir exactement 1000 appels (10 threads * 100 boucles)
    stats = FileStrategyRegistry.get_registry_stats()
    assert stats["counters"][".json"] == 1000
