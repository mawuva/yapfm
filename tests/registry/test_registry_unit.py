from pathlib import Path
from typing import Any, Generator

import pytest

from yapfm.registry import FileStrategyRegistry, register_file_strategy
from yapfm.strategies import BaseFileStrategy


@pytest.fixture(autouse=True)
def clean_registry() -> Generator[None, None, None]:
    """
    Scenario: Clean registry state before and after each test

    Expected:
    - Registry should be completely cleared before each test
    - Registry should be cleaned up after each test
    - No state should persist between tests
    """
    FileStrategyRegistry._strategy_map.clear()
    FileStrategyRegistry._counter.clear()
    FileStrategyRegistry._skipped.clear()
    yield


# ============================
# Tests de l'enregistrement
# ============================


def test_register_single_extension_strategy() -> None:
    """
    Scenario: Register a strategy for a single file extension

    Expected:
    - Strategy should be present in the registry
    - Counter for this extension should be initialized to 0
    - Strategy should be retrievable by extension
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".json", DummyStrategy)

    strategies = FileStrategyRegistry.list_strategies()
    assert ".json" in strategies
    assert strategies[".json"] == DummyStrategy
    assert FileStrategyRegistry.get_counters()[".json"] == 0


def test_register_multiple_extensions_strategy() -> None:
    """
    Scenario: Register a strategy for multiple file extensions

    Expected:
    - All extensions should be present in the registry
    - Each extension should have a counter initialized to 0
    - All extensions should point to the same strategy class
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy([".yaml", ".yml"], DummyStrategy)

    strategies = FileStrategyRegistry.list_strategies()
    assert ".yaml" in strategies
    assert ".yml" in strategies
    assert FileStrategyRegistry.get_counters()[".yaml"] == 0
    assert FileStrategyRegistry.get_counters()[".yml"] == 0


# ============================
# Tests de récupération
# ============================


def test_get_strategy_by_extension_increments_counter() -> None:
    """
    Scenario: Retrieve a strategy using direct file extension

    Expected:
    - Strategy instance should be returned
    - Usage counter should be incremented
    - Strategy should be properly instantiated
    """

    class DummyStrategy(BaseFileStrategy):
        def __init__(self) -> None:
            pass

        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".txt", DummyStrategy)

    instance = FileStrategyRegistry.get_strategy(".txt")

    assert isinstance(instance, DummyStrategy)
    assert FileStrategyRegistry.get_counters()[".txt"] == 1


def test_get_strategy_by_filepath_increments_counter(tmp_path: Path) -> None:
    """
    Scenario: Retrieve a strategy using file path

    Expected:
    - Strategy instance should be returned
    - Counter should be incremented
    - Extension should be extracted from file path correctly
    """

    class DummyStrategy(BaseFileStrategy):
        def __init__(self) -> None:
            pass

        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".cfg", DummyStrategy)

    file_path = tmp_path / "settings.cfg"
    file_path.write_text("dummy")

    instance = FileStrategyRegistry.get_strategy(str(file_path))

    assert isinstance(instance, DummyStrategy)
    assert FileStrategyRegistry.get_counters()[".cfg"] == 1


def test_get_strategy_unknown_extension_skips() -> None:
    """
    Scenario: Try to retrieve a strategy for an unregistered extension

    Expected:
    - No strategy object should be returned (None)
    - File/extension should be added to the skipped list
    - Registry state should remain consistent
    """
    result = FileStrategyRegistry.get_strategy("unknown.ext")

    assert result is None
    skipped = FileStrategyRegistry.get_skipped()
    assert "unknown" in skipped
    assert "unknown.ext" in skipped["unknown"]


# ============================
# Tests de gestion du registre
# ============================


def test_unregister_strategy_removes_entries() -> None:
    """
    Scenario: Unregister an existing strategy

    Expected:
    - Extension should be removed from registry
    - Counter and related skipped entries should be removed
    - Strategy should no longer be retrievable
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".ini", DummyStrategy)
    FileStrategyRegistry.unregister_strategy(".ini")

    assert ".ini" not in FileStrategyRegistry.list_strategies()
    assert ".ini" not in FileStrategyRegistry.get_counters()
    assert ".ini" not in FileStrategyRegistry.get_skipped()


# ============================
# Tests de statistiques
# ============================


def test_get_supported_formats_returns_list() -> None:
    """
    Scenario: Get list of supported formats after registration

    Expected:
    - Registered extensions should appear in the list
    - List should contain all registered extensions
    - List should be a copy that doesn't affect registry state
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy([".a", ".b"], DummyStrategy)

    supported = FileStrategyRegistry.get_supported_formats()
    assert ".a" in supported
    assert ".b" in supported


def test_is_format_supported_true_and_false() -> None:
    """
    Scenario: Check if a format is supported or not

    Expected:
    - Should return True for a registered extension
    - Should return False for an unknown extension
    - Should handle extension normalization correctly
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".csv", DummyStrategy)

    assert FileStrategyRegistry.is_format_supported("csv") is True
    assert FileStrategyRegistry.is_format_supported("xml") is False


def test_get_registry_stats_returns_all_data() -> None:
    """
    Scenario: Get comprehensive registry statistics

    Expected:
    - Should return counters, skipped files and supported formats
    - Returned structures should match internal registry state
    - Statistics should be consistent and accurate
    """

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    FileStrategyRegistry.register_strategy(".json", DummyStrategy)
    FileStrategyRegistry.get_strategy("file.json")
    FileStrategyRegistry.get_strategy("file.unknown")

    stats = FileStrategyRegistry.get_registry_stats()

    assert "counters" in stats
    assert "skipped" in stats
    assert "supported_formats" in stats
    assert stats["counters"][".json"] == 1
    assert "unknown" in stats["skipped"]


# ============================
# Tests du décorateur
# ============================


def test_register_file_strategy_decorator() -> None:
    """
    Scenario: Use decorator to register a strategy

    Expected:
    - Decorated strategy should be registered in the registry
    - Strategy should be retrievable after decoration
    - Decorator should preserve class functionality
    """

    @register_file_strategy(".toml")
    class TomlStrategy(BaseFileStrategy):
        def __init__(self) -> None:
            pass

        def load(self, file_path: Path | str) -> Any:
            return {"toml": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    assert ".toml" in FileStrategyRegistry.list_strategies()
    assert FileStrategyRegistry.list_strategies()[".toml"] == TomlStrategy
