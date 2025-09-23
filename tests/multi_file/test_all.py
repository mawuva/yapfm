"""
Test suite for all multi-file functionality.

This module provides a comprehensive test suite for all multi-file operations
including merge strategies, loader, and enum functionality.
"""

# mypy: ignore-errors

import json
import tempfile
from pathlib import Path

import pytest
import tomlkit
import yaml

from yapfm.multi_file import get_available_strategies, load_and_merge
from yapfm.multi_file.loader import MultiFileLoader
from yapfm.multi_file.strategies import MergeStrategy


class TestMultiFileIntegration:
    """Integration tests for multi-file functionality."""

    def test_load_and_merge_function(self):
        """Test the main load_and_merge function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"app": {"name": "MyApp"}}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"app": {"debug": True}}))

            # Test deep merge
            result = load_and_merge([file1, file2], strategy=MergeStrategy.DEEP)

            expected = {"app": {"name": "MyApp", "debug": True}}
            assert result == expected

    def test_get_available_strategies_function(self):
        """Test the get_available_strategies function."""
        strategies = get_available_strategies()

        assert isinstance(strategies, list)
        assert len(strategies) == 6

        expected_strategies = [
            "deep",
            "namespace",
            "priority",
            "append",
            "replace",
            "conditional",
        ]

        for strategy in expected_strategies:
            assert strategy in strategies

    def test_all_strategies_work(self):
        """Test that all merge strategies work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"key": "value1", "shared": "from1"}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"key": "value2", "shared": "from2"}))

            # Test each strategy
            strategies_to_test = [
                (MergeStrategy.DEEP, {"key": "value2", "shared": "from2"}),
                (
                    MergeStrategy.NAMESPACE,
                    {
                        "config1": {"key": "value1", "shared": "from1"},
                        "config2": {"key": "value2", "shared": "from2"},
                    },
                ),
                (MergeStrategy.REPLACE, {"key": "value2", "shared": "from2"}),
                (
                    MergeStrategy.APPEND,
                    {"key": ["value1", "value2"], "shared": ["from1", "from2"]},
                ),
            ]

            for strategy, expected in strategies_to_test:
                result = load_and_merge([file1, file2], strategy=strategy)
                assert result == expected, f"Strategy {strategy} failed"

    def test_priority_strategy_with_order(self):
        """Test priority strategy with explicit order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"key": "value1"}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"key": "value2"}))

            result = load_and_merge(
                [file1, file2],
                strategy=MergeStrategy.PRIORITY,
                priority_order=[1, 0],  # file2 has higher priority
            )

            assert result == {"key": "value2"}

    def test_conditional_strategy(self):
        """Test conditional strategy with custom condition."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            json_file = temp_path / "config.json"
            json_file.write_text(json.dumps({"app": "config"}))

            toml_file = temp_path / "database.toml"
            toml_file.write_text(tomlkit.dumps({"host": "localhost"}))

            # Create a custom condition that only includes .json files
            def is_json_file(file_path, data):
                return str(file_path).endswith(".json")

            result = load_and_merge(
                [json_file, toml_file],
                strategy=MergeStrategy.CONDITIONAL,
                condition=is_json_file,
            )

            # Should only include .json files
            assert result == {"app": "config"}

    def test_mixed_file_formats(self):
        """Test loading files with mixed formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            json_file = temp_path / "config.json"
            json_file.write_text(json.dumps({"app": {"name": "MyApp"}}))

            toml_file = temp_path / "database.toml"
            toml_file.write_text(tomlkit.dumps({"database": {"host": "localhost"}}))

            yaml_file = temp_path / "secrets.yml"
            yaml_file.write_text(yaml.dump({"api_key": "secret123"}))

            result = load_and_merge(
                [json_file, toml_file, yaml_file], strategy=MergeStrategy.NAMESPACE
            )

            expected = {
                "config": {"app": {"name": "MyApp"}},
                "database": {"database": {"host": "localhost"}},
                "secrets": {"api_key": "secret123"},
            }
            assert result == expected

    def test_glob_patterns(self):
        """Test loading files using glob patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"app": "config1"}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"app": "config2"}))

            file3 = temp_path / "database.toml"
            file3.write_text(tomlkit.dumps({"host": "localhost"}))

            result = load_and_merge(
                [str(temp_path / "*.json")], strategy=MergeStrategy.NAMESPACE
            )

            expected = {"config1": {"app": "config1"}, "config2": {"app": "config2"}}
            assert result == expected

    def test_caching_functionality(self):
        """Test that caching works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            test_file = temp_path / "test.json"
            test_data = {"key": "value"}
            test_file.write_text(json.dumps(test_data))

            # Create loader with caching
            loader = MultiFileLoader(enable_cache=True)

            # First load
            result1 = loader.load_and_merge([test_file])

            # Second load (should use cache)
            result2 = loader.load_and_merge([test_file])

            assert result1 == result2
            assert result1 == test_data

            # Check cache stats
            stats = loader.get_cache_stats()
            assert "enabled" in stats
            assert "smart_cache_stats" in stats
            assert "hits" in stats["smart_cache_stats"]
            assert "misses" in stats["smart_cache_stats"]

    def test_error_handling(self):
        """Test error handling for various scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test nonexistent file (should return empty dict, not raise error)
            result = load_and_merge(["nonexistent.json"])
            assert result == {}

            # Test invalid file format (should return empty dict, not raise error)
            invalid_file = temp_path / "test.invalid"
            invalid_file.write_text("invalid content")

            result = load_and_merge([invalid_file])
            assert result == {}

            # Test invalid strategy
            test_file = temp_path / "test.json"
            test_file.write_text(json.dumps({"key": "value"}))

            with pytest.raises(ValueError, match="Unknown strategy"):
                load_and_merge([test_file], strategy="invalid_strategy")

    def test_strategy_enum_usage(self):
        """Test using MergeStrategy enum in various ways."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"key": "value1"}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"key": "value2"}))

            # Test enum member usage
            result = load_and_merge([file1, file2], strategy=MergeStrategy.DEEP)
            assert result == {"key": "value2"}

            # Test enum value usage
            result = load_and_merge([file1, file2], strategy=MergeStrategy.DEEP.value)
            assert result == {"key": "value2"}

            # Test enum string conversion
            result = load_and_merge([file1, file2], strategy=str(MergeStrategy.DEEP))
            assert result == {"key": "value2"}

    def test_complex_nested_merging(self):
        """Test complex nested data merging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "base.json"
            file1.write_text(
                json.dumps(
                    {
                        "database": {
                            "host": "localhost",
                            "port": 5432,
                            "credentials": {"username": "admin"},
                        },
                        "app": {"name": "MyApp", "features": ["auth", "logging"]},
                    }
                )
            )

            file2 = temp_path / "override.json"
            file2.write_text(
                json.dumps(
                    {
                        "database": {
                            "host": "prod-server",
                            "credentials": {"password": "secret123"},
                        },
                        "app": {"debug": True, "features": ["caching"]},
                    }
                )
            )

            result = load_and_merge([file1, file2], strategy=MergeStrategy.DEEP)

            expected = {
                "database": {
                    "host": "prod-server",
                    "port": 5432,
                    "credentials": {"username": "admin", "password": "secret123"},
                },
                "app": {
                    "name": "MyApp",
                    "debug": True,
                    "features": ["caching"],  # Last file overwrites
                },
            }
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
