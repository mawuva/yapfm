"""
Tests for NamespaceMergeStrategy.

This module contains tests for the namespace merge strategy that places each file's data
under a separate namespace.
"""

# mypy: ignore-errors

from pathlib import Path

import pytest

from yapfm.multi_file.merge_strategies.namespace import NamespaceMergeStrategy


class TestNamespaceMergeStrategy:
    """Test cases for NamespaceMergeStrategy."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        strategy = NamespaceMergeStrategy()

        assert strategy.namespace_generator is not None
        assert strategy.namespace_prefix is None
        assert strategy.options == {
            "namespace_generator": None,
            "namespace_prefix": None,
        }

    def test_init_with_prefix(self):
        """Test initialization with namespace prefix."""
        strategy = NamespaceMergeStrategy(namespace_prefix="app")

        assert strategy.namespace_prefix == "app"
        assert strategy.options == {
            "namespace_generator": None,
            "namespace_prefix": "app",
        }

    def test_init_with_custom_generator(self):
        """Test initialization with custom namespace generator."""

        def custom_generator(path: Path) -> str:
            return f"custom_{path.stem}"

        strategy = NamespaceMergeStrategy(namespace_generator=custom_generator)

        assert strategy.namespace_generator == custom_generator

    def test_default_namespace_generator(self):
        """Test default namespace generator."""
        strategy = NamespaceMergeStrategy()

        # Test with different file extensions
        assert strategy._default_namespace_generator(Path("config.json")) == "config"
        assert (
            strategy._default_namespace_generator(Path("database.toml")) == "database"
        )
        assert strategy._default_namespace_generator(Path("secrets.yml")) == "secrets"
        assert (
            strategy._default_namespace_generator(Path("app.config.json"))
            == "app.config"
        )

    def test_get_name(self):
        """Test get_name method."""
        strategy = NamespaceMergeStrategy()

        assert strategy.get_name() == "namespace"

    def test_get_description(self):
        """Test get_description method."""
        strategy = NamespaceMergeStrategy()

        description = strategy.get_description()
        assert (
            "Merges files by placing each file's data under a separate namespace"
            in description
        )

    def test_get_optional_options(self):
        """Test get_optional_options method."""
        strategy = NamespaceMergeStrategy()

        options = strategy.get_optional_options()
        assert options == {"namespace_generator": None, "namespace_prefix": None}

    def test_validate_options_valid(self):
        """Test validate_options with valid options."""
        strategy = NamespaceMergeStrategy()

        def custom_generator(path: Path) -> str:
            return path.stem

        validated = strategy.validate_options(
            namespace_generator=custom_generator, namespace_prefix="test"
        )

        assert validated["namespace_generator"] == custom_generator
        assert validated["namespace_prefix"] == "test"

    def test_validate_options_invalid_generator(self):
        """Test validate_options with invalid generator."""
        strategy = NamespaceMergeStrategy()

        with pytest.raises(
            ValueError, match="namespace_generator must be callable or None"
        ):
            strategy.validate_options(namespace_generator="invalid")

    def test_validate_options_invalid_prefix(self):
        """Test validate_options with invalid prefix."""
        strategy = NamespaceMergeStrategy()

        with pytest.raises(
            ValueError, match="namespace_prefix must be a string or None"
        ):
            strategy.validate_options(namespace_prefix=123)

    def test_merge_empty_files(self):
        """Test merge with empty file list."""
        strategy = NamespaceMergeStrategy()

        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merge with single file."""
        strategy = NamespaceMergeStrategy()

        files = [(Path("config.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"config": {"key": "value"}}

    def test_merge_multiple_files(self):
        """Test merge with multiple files."""
        strategy = NamespaceMergeStrategy()

        files = [
            (Path("config.json"), {"app": {"name": "MyApp"}}),
            (Path("database.json"), {"host": "localhost", "port": 5432}),
            (Path("secrets.json"), {"api_key": "secret123"}),
        ]
        result = strategy.merge(files)

        expected = {
            "config": {"app": {"name": "MyApp"}},
            "database": {"host": "localhost", "port": 5432},
            "secrets": {"api_key": "secret123"},
        }
        assert result == expected

    def test_merge_with_namespace_prefix(self):
        """Test merge with namespace prefix."""
        strategy = NamespaceMergeStrategy(namespace_prefix="app")

        files = [
            (Path("config.json"), {"name": "MyApp"}),
            (Path("database.json"), {"host": "localhost"}),
        ]
        result = strategy.merge(files)

        expected = {
            "app.config": {"name": "MyApp"},
            "app.database": {"host": "localhost"},
        }
        assert result == expected

    def test_merge_with_custom_generator(self):
        """Test merge with custom namespace generator."""

        def custom_generator(path: Path) -> str:
            return f"custom_{path.stem.upper()}"

        strategy = NamespaceMergeStrategy(namespace_generator=custom_generator)

        files = [
            (Path("config.json"), {"name": "MyApp"}),
            (Path("database.json"), {"host": "localhost"}),
        ]
        result = strategy.merge(files)

        expected = {
            "custom_CONFIG": {"name": "MyApp"},
            "custom_DATABASE": {"host": "localhost"},
        }
        assert result == expected

    def test_merge_with_prefix_and_custom_generator(self):
        """Test merge with both prefix and custom generator."""

        def custom_generator(path: Path) -> str:
            return f"env_{path.stem}"

        strategy = NamespaceMergeStrategy(
            namespace_generator=custom_generator, namespace_prefix="prod"
        )

        files = [
            (Path("config.json"), {"name": "MyApp"}),
            (Path("database.json"), {"host": "localhost"}),
        ]
        result = strategy.merge(files)

        expected = {
            "prod.env_config": {"name": "MyApp"},
            "prod.env_database": {"host": "localhost"},
        }
        assert result == expected

    def test_merge_with_duplicate_namespaces(self):
        """Test merge with files that would create duplicate namespaces."""
        strategy = NamespaceMergeStrategy()

        files = [
            (Path("config.json"), {"key1": "value1"}),
            (Path("config.toml"), {"key2": "value2"}),  # Same stem, different extension
        ]
        result = strategy.merge(files)

        # Both should be under "config" namespace, second overwrites first
        assert result == {"config": {"key2": "value2"}}

    def test_merge_with_nested_data(self):
        """Test merge with nested data structures."""
        strategy = NamespaceMergeStrategy()

        files = [
            (
                Path("app.json"),
                {
                    "database": {"host": "localhost", "port": 5432},
                    "features": ["auth", "logging"],
                },
            ),
            (
                Path("cache.json"),
                {"redis": {"host": "redis-server", "port": 6379}, "ttl": 3600},
            ),
        ]
        result = strategy.merge(files)

        expected = {
            "app": {
                "database": {"host": "localhost", "port": 5432},
                "features": ["auth", "logging"],
            },
            "cache": {"redis": {"host": "redis-server", "port": 6379}, "ttl": 3600},
        }
        assert result == expected

    def test_merge_with_kwargs(self):
        """Test merge with additional kwargs."""
        strategy = NamespaceMergeStrategy()

        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, test_kwarg="test_value")

        assert result == {"test": {"key": "value"}}

    def test_get_merge_info(self):
        """Test get_merge_info method."""
        strategy = NamespaceMergeStrategy(namespace_prefix="app")

        files = [
            (Path("config.json"), {"name": "MyApp"}),
            (Path("database.json"), {"host": "localhost"}),
        ]
        info = strategy.get_merge_info(files)

        assert info["strategy"] == "namespace"
        assert info["namespace_prefix"] == "app"
        assert info["namespaces"] == ["app.config", "app.database"]
        assert info["merge_type"] == "namespace_separation"
        assert info["file_count"] == 2
        assert info["files"] == ["config.json", "database.json"]

    def test_str_representation(self):
        """Test string representation."""
        strategy = NamespaceMergeStrategy(namespace_prefix="app")

        assert str(strategy) == "NamespaceMergeStrategy(namespace)"

    def test_repr_representation(self):
        """Test detailed string representation."""
        strategy = NamespaceMergeStrategy(namespace_prefix="app")

        expected = "NamespaceMergeStrategy(name='namespace', options={'namespace_generator': None, 'namespace_prefix': 'app'})"
        assert repr(strategy) == expected
