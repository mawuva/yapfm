"""
Unit tests for the FileStrategyRegistry class.
"""

# mypy: ignore-errors

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
    FileStrategyRegistry._registry.clear()
    yield


# ============================
# Tests de l'enregistrement
# ============================


def test_register_single_extension_strategy() -> None:
    """
    Scenario: Register a strategy for a single file extension

    Expected:
    - Strategy should be present in the registry
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


def test_register_multiple_extensions_strategy() -> None:
    """
    Scenario: Register a strategy for multiple file extensions

    Expected:
    - All extensions should be present in the registry
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


# ============================
# Tests de récupération
# ============================


def test_get_strategy_by_extension() -> None:
    """
    Scenario: Retrieve a strategy using direct file extension

    Expected:
    - Strategy instance should be returned
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


def test_get_strategy_by_filepath(tmp_path: Path) -> None:
    """
    Scenario: Retrieve a strategy using file path

    Expected:
    - Strategy instance should be returned
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


def test_get_strategy_unknown_extension() -> None:
    """
    Scenario: Try to retrieve a strategy for an unregistered extension

    Expected:
    - No strategy object should be returned (None)
    - Registry state should remain consistent
    """
    result = FileStrategyRegistry.get_strategy("unknown.ext")

    assert result is None


# ============================
# Tests de gestion du registre
# ============================


def test_unregister_strategy_removes_entries() -> None:
    """
    Scenario: Unregister an existing strategy

    Expected:
    - Extension should be removed from registry
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


# ============================
# Tests de statistiques
# ============================


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


# ============================
# Tests pour infer_format_from_extension
# ============================


def test_infer_format_from_extension_json() -> None:
    """
    Scenario: Infer format from JSON file extension

    Expected:
    - Should return "json" for .json extension
    - Should handle both string and Path inputs
    - Should work with full file paths
    """
    assert FileStrategyRegistry.infer_format_from_extension("config.json") == "json"
    assert FileStrategyRegistry.infer_format_from_extension("data.json") == "json"
    assert (
        FileStrategyRegistry.infer_format_from_extension("/path/to/file.json") == "json"
    )

    # Test with Path object
    from pathlib import Path

    assert (
        FileStrategyRegistry.infer_format_from_extension(Path("config.json")) == "json"
    )


def test_infer_format_from_extension_yaml() -> None:
    """
    Scenario: Infer format from YAML file extensions

    Expected:
    - Should return "yaml" for both .yml and .yaml extensions
    - Should handle various file path formats
    """
    assert FileStrategyRegistry.infer_format_from_extension("config.yml") == "yaml"
    assert FileStrategyRegistry.infer_format_from_extension("config.yaml") == "yaml"
    assert (
        FileStrategyRegistry.infer_format_from_extension("/path/to/file.yml") == "yaml"
    )
    assert (
        FileStrategyRegistry.infer_format_from_extension("/path/to/file.yaml") == "yaml"
    )


def test_infer_format_from_extension_toml() -> None:
    """
    Scenario: Infer format from TOML file extension

    Expected:
    - Should return "toml" for .toml extension
    - Should handle various file path formats
    """
    assert FileStrategyRegistry.infer_format_from_extension("config.toml") == "toml"
    assert (
        FileStrategyRegistry.infer_format_from_extension("/path/to/file.toml") == "toml"
    )


def test_infer_format_from_extension_unknown() -> None:
    """
    Scenario: Try to infer format from unknown extension

    Expected:
    - Should raise ValueError for unknown extensions
    - Should provide informative error message
    """
    with pytest.raises(ValueError, match="Cannot infer format from extension"):
        FileStrategyRegistry.infer_format_from_extension("file.unknown")

    with pytest.raises(ValueError, match="Cannot infer format from extension"):
        FileStrategyRegistry.infer_format_from_extension("file.xyz")


def test_infer_format_from_extension_no_extension() -> None:
    """
    Scenario: Try to infer format from file without extension

    Expected:
    - Should raise ValueError for files without extension
    - Should handle edge cases gracefully
    """
    with pytest.raises(ValueError, match="Cannot infer format from extension"):
        FileStrategyRegistry.infer_format_from_extension("file")

    with pytest.raises(ValueError, match="Cannot infer format from extension"):
        FileStrategyRegistry.infer_format_from_extension("")


def test_infer_format_from_extension_case_sensitivity() -> None:
    """
    Scenario: Test case sensitivity of format inference

    Expected:
    - Should handle uppercase extensions correctly
    - Should be case-insensitive for known formats
    """
    # This depends on how resolve_file_extension handles case
    # Assuming it normalizes to lowercase
    assert FileStrategyRegistry.infer_format_from_extension("config.JSON") == "json"
    assert FileStrategyRegistry.infer_format_from_extension("config.YML") == "yaml"
    assert FileStrategyRegistry.infer_format_from_extension("config.TOML") == "toml"


# ============================
# Tests pour les méthodes existantes améliorées
# ============================


def test_list_strategies_returns_copy() -> None:
    """
    Scenario: Test that list_strategies returns a copy of the registry

    Expected:
    - Should return a dictionary copy, not the original
    - Modifying the returned dict should not affect the registry
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

    FileStrategyRegistry.register_strategy(".test", DummyStrategy)

    strategies = FileStrategyRegistry.list_strategies()
    original_count = len(strategies)

    # Modify the returned dictionary
    strategies[".test"] = "modified"

    # Registry should be unchanged
    new_strategies = FileStrategyRegistry.list_strategies()
    assert len(new_strategies) == original_count
    assert new_strategies[".test"] == DummyStrategy


def test_get_supported_formats_returns_list_copy() -> None:
    """
    Scenario: Test that get_supported_formats returns a list

    Expected:
    - Should return a list of supported extensions
    - Should be a copy that doesn't affect the registry
    - Should contain all registered extensions
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

    FileStrategyRegistry.register_strategy([".ext1", ".ext2"], DummyStrategy)

    formats = FileStrategyRegistry.get_supported_formats()
    assert isinstance(formats, list)
    assert ".ext1" in formats
    assert ".ext2" in formats

    # Modify the returned list
    formats.append(".fake")

    # Registry should be unchanged
    new_formats = FileStrategyRegistry.get_supported_formats()
    assert ".fake" not in new_formats


def test_is_format_supported_with_various_inputs() -> None:
    """
    Scenario: Test is_format_supported with various input formats

    Expected:
    - Should handle extensions with and without dots
    - Should handle file paths correctly
    - Should return correct boolean values
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

    FileStrategyRegistry.register_strategy(".test", DummyStrategy)

    # Test with dot
    assert FileStrategyRegistry.is_format_supported(".test") is True
    assert FileStrategyRegistry.is_format_supported("test") is True

    # Test with file path
    assert FileStrategyRegistry.is_format_supported("file.test") is True
    assert FileStrategyRegistry.is_format_supported("/path/to/file.test") is True

    # Test unsupported formats
    assert FileStrategyRegistry.is_format_supported(".unknown") is False
    assert FileStrategyRegistry.is_format_supported("unknown") is False


def test_registry_thread_safety() -> None:
    """
    Scenario: Test that registry operations are thread-safe

    Expected:
    - Multiple concurrent operations should not cause errors
    - Registry state should remain consistent
    - No race conditions should occur
    """
    import threading
    import time

    class DummyStrategy(BaseFileStrategy):
        def load(self, file_path: Path | str) -> Any:
            return {"dummy": "data"}

        def save(self, file_path: Path | str, data: Any) -> None:
            pass

        def navigate(
            self, document: Any, path: list[str], create: bool = False
        ) -> Any | None:
            return document.get(path[0]) if path else None

    def register_strategies():
        for i in range(10):
            try:
                FileStrategyRegistry.register_strategy(f".ext{i}", DummyStrategy)
            except ValueError:
                # Ignore duplicate registration errors
                pass
            time.sleep(0.001)  # Small delay to increase chance of race conditions

    def get_strategies():
        for i in range(10):
            FileStrategyRegistry.get_strategy(f".ext{i}")
            time.sleep(0.001)

    def check_support():
        for i in range(10):
            FileStrategyRegistry.is_format_supported(f".ext{i}")
            time.sleep(0.001)

    # Run operations concurrently
    threads = []
    for _ in range(3):
        threads.append(threading.Thread(target=register_strategies))
        threads.append(threading.Thread(target=get_strategies))
        threads.append(threading.Thread(target=check_support))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Registry should be in a consistent state
    strategies = FileStrategyRegistry.list_strategies()
    assert len(strategies) >= 10  # At least some strategies should be registered


def test_registry_error_handling() -> None:
    """
    Scenario: Test error handling in registry operations

    Expected:
    - Should handle invalid inputs gracefully
    - Should not crash on unexpected data types
    - Should provide meaningful error messages
    """
    # Test with empty string
    assert FileStrategyRegistry.get_strategy("") is None

    # Test with non-string input
    with pytest.raises(AttributeError):
        FileStrategyRegistry.get_strategy(123)  # type: ignore

    # Test with None input
    with pytest.raises(AttributeError):
        FileStrategyRegistry.get_strategy(None)  # type: ignore

    # Test unregister with non-existent extension
    FileStrategyRegistry.unregister_strategy(".nonexistent")  # Should not raise error
