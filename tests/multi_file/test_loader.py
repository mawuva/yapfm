"""
Tests for MultiFileLoader.

This module contains tests for the MultiFileLoader class that handles loading
and merging multiple files using different strategies.
"""

# mypy: ignore-errors

import json
import tempfile
from pathlib import Path

import pytest
import tomlkit
import yaml

from yapfm.cache import SmartCache
from yapfm.multi_file.loader import MultiFileLoader
from yapfm.multi_file.merge_strategies.deep import DeepMergeStrategy
from yapfm.multi_file.merge_strategies.namespace import NamespaceMergeStrategy
from yapfm.multi_file.strategies import MergeStrategy


class TestMultiFileLoader:
    """Test cases for MultiFileLoader."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        loader = MultiFileLoader()

        assert loader._cache is not None  # Cache is created by default
        assert loader.enable_cache is True
        assert loader.cache_ttl == 3600  # Default TTL is 1 hour

    def test_init_with_cache(self):
        """Test initialization with provided cache."""
        cache = SmartCache(max_size=100, default_ttl=600)
        loader = MultiFileLoader(cache=cache, enable_cache=True)

        assert loader._cache == cache
        assert loader.enable_cache is True
        # cache_ttl is not updated when cache is provided, it remains the default
        assert loader.cache_ttl == 3600

    def test_init_with_enable_cache_false(self):
        """Test initialization with caching disabled."""
        loader = MultiFileLoader(enable_cache=False)

        assert loader._cache is None
        assert loader.enable_cache is False

    def test_init_creates_cache_when_enabled(self):
        """Test that cache is created when enable_cache=True and no cache provided."""
        loader = MultiFileLoader(enable_cache=True, cache_ttl=120)

        assert loader._cache is not None
        assert isinstance(loader._cache, SmartCache)
        assert loader.cache_ttl == 120

    def test_expand_file_paths_single_file(self):
        """Test expanding single file path."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_file.write_text('{"key": "value"}')

            expanded = loader._expand_file_paths([str(test_file)])

            assert len(expanded) == 1
            assert expanded[0] == test_file

    def test_expand_file_paths_multiple_files(self):
        """Test expanding multiple file paths."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "test1.json"
            file2 = temp_path / "test2.json"

            file1.write_text('{"key1": "value1"}')
            file2.write_text('{"key2": "value2"}')

            expanded = loader._expand_file_paths([str(file1), str(file2)])

            assert len(expanded) == 2
            assert file1 in expanded
            assert file2 in expanded

    def test_expand_file_paths_glob_pattern(self):
        """Test expanding glob patterns."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "config.json"
            file2 = temp_path / "database.json"
            file3 = temp_path / "secrets.toml"

            file1.write_text('{"app": "config"}')
            file2.write_text('{"db": "config"}')
            file3.write_text('[database]\nhost = "localhost"')

            expanded = loader._expand_file_paths([str(temp_path / "*.json")])

            assert len(expanded) == 2
            assert file1 in expanded
            assert file2 in expanded
            assert file3 not in expanded

    def test_expand_file_paths_nonexistent_file(self):
        """Test expanding nonexistent file path."""
        loader = MultiFileLoader()

        # Nonexistent files are still included in expansion (existence check happens later)
        expanded = loader._expand_file_paths(["nonexistent.json"])
        assert len(expanded) == 1
        assert expanded[0] == Path("nonexistent.json")

    def test_expand_file_paths_nonexistent_glob(self):
        """Test expanding nonexistent glob pattern."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Nonexistent glob patterns just return empty list
            expanded = loader._expand_file_paths(
                [str(Path(temp_dir) / "*.nonexistent")]
            )
            assert expanded == []

    def test_load_files_json(self):
        """Test loading JSON files."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value", "number": 42}
            test_file.write_text(json.dumps(test_data))

            loaded = loader._load_files([test_file])

            assert len(loaded) == 1
            assert loaded[0][0] == test_file
            assert loaded[0][1] == test_data

    def test_load_files_toml(self):
        """Test loading TOML files."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.toml"
            test_data = {"database": {"host": "localhost", "port": 5432}}
            test_file.write_text(tomlkit.dumps(test_data))

            loaded = loader._load_files([test_file])

            assert len(loaded) == 1
            assert loaded[0][0] == test_file
            assert loaded[0][1] == test_data

    def test_load_files_yaml(self):
        """Test loading YAML files."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.yml"
            test_data = {"app": {"name": "MyApp", "debug": True}}
            test_file.write_text(yaml.dump(test_data))

            loaded = loader._load_files([test_file])

            assert len(loaded) == 1
            assert loaded[0][0] == test_file
            assert loaded[0][1] == test_data

    def test_load_files_mixed_formats(self):
        """Test loading files with mixed formats."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            json_file = temp_path / "config.json"
            json_data = {"app": {"name": "MyApp"}}
            json_file.write_text(json.dumps(json_data))

            toml_file = temp_path / "database.toml"
            toml_data = {"database": {"host": "localhost"}}
            toml_file.write_text(tomlkit.dumps(toml_data))

            yaml_file = temp_path / "secrets.yml"
            yaml_data = {"api_key": "secret123"}
            yaml_file.write_text(yaml.dump(yaml_data))

            loaded = loader._load_files([json_file, toml_file, yaml_file])

            assert len(loaded) == 3

            # Check that all files were loaded correctly
            loaded_data = {str(path): data for path, data in loaded}
            assert loaded_data[str(json_file)] == json_data
            assert loaded_data[str(toml_file)] == toml_data
            assert loaded_data[str(yaml_file)] == yaml_data

    def test_load_files_with_caching(self):
        """Test loading files with caching enabled."""
        cache = SmartCache(max_size=100, default_ttl=300)
        loader = MultiFileLoader(cache=cache, enable_cache=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value"}
            test_file.write_text(json.dumps(test_data))

            # First load
            loaded1 = loader._load_files([test_file])

            # Second load (should use cache)
            loaded2 = loader._load_files([test_file])

            assert loaded1 == loaded2
            assert len(loaded1) == 1
            assert loaded1[0][1] == test_data

    def test_load_files_without_caching(self):
        """Test loading files with caching disabled."""
        loader = MultiFileLoader(enable_cache=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value"}
            test_file.write_text(json.dumps(test_data))

            loaded = loader._load_files([test_file])

            assert len(loaded) == 1
            assert loaded[0][1] == test_data

    def test_get_merge_strategy_string(self):
        """Test getting merge strategy by string name."""
        loader = MultiFileLoader()

        strategy = loader._get_merge_strategy("deep")
        assert isinstance(strategy, DeepMergeStrategy)

        strategy = loader._get_merge_strategy("namespace")
        assert isinstance(strategy, NamespaceMergeStrategy)

    def test_get_merge_strategy_enum(self):
        """Test getting merge strategy by enum."""
        loader = MultiFileLoader()

        strategy = loader._get_merge_strategy(MergeStrategy.DEEP)
        assert isinstance(strategy, DeepMergeStrategy)

        strategy = loader._get_merge_strategy(MergeStrategy.NAMESPACE)
        assert isinstance(strategy, NamespaceMergeStrategy)

    def test_get_merge_strategy_instance(self):
        """Test getting merge strategy from instance."""
        loader = MultiFileLoader()

        custom_strategy = DeepMergeStrategy(overwrite=False)
        strategy = loader._get_merge_strategy(custom_strategy)

        assert strategy == custom_strategy

    def test_get_merge_strategy_invalid(self):
        """Test getting invalid merge strategy."""
        loader = MultiFileLoader()

        with pytest.raises(ValueError, match="Unknown strategy"):
            loader._get_merge_strategy("invalid_strategy")

    def test_load_and_merge_single_file(self):
        """Test loading and merging single file."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value"}
            test_file.write_text(json.dumps(test_data))

            result = loader.load_and_merge([test_file])

            assert result == test_data

    def test_load_and_merge_multiple_files(self):
        """Test loading and merging multiple files."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config1.json"
            file1.write_text(json.dumps({"app": {"name": "MyApp"}}))

            file2 = temp_path / "config2.json"
            file2.write_text(json.dumps({"app": {"debug": True}}))

            result = loader.load_and_merge([file1, file2], strategy="deep")

            expected = {"app": {"name": "MyApp", "debug": True}}
            assert result == expected

    def test_load_and_merge_with_strategy_options(self):
        """Test loading and merging with strategy options."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config.json"
            file1.write_text(json.dumps({"key": "value1"}))

            file2 = temp_path / "database.json"
            file2.write_text(json.dumps({"key": "value2"}))

            result = loader.load_and_merge(
                [file1, file2], strategy="namespace", namespace_prefix="app"
            )

            expected = {
                "app.config": {"key": "value1"},
                "app.database": {"key": "value2"},
            }
            assert result == expected

    def test_load_and_merge_with_glob_pattern(self):
        """Test loading and merging with glob pattern."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            file1 = temp_path / "config.json"
            file1.write_text(json.dumps({"app": "config"}))

            file2 = temp_path / "database.json"
            file2.write_text(json.dumps({"db": "config"}))

            file3 = temp_path / "secrets.toml"
            file3.write_text(tomlkit.dumps({"api_key": "secret"}))

            result = loader.load_and_merge(
                [str(temp_path / "*.json")], strategy="namespace"
            )

            expected = {"config": {"app": "config"}, "database": {"db": "config"}}
            assert result == expected

    def test_clear_cache(self):
        """Test clearing cache."""
        cache = SmartCache(max_size=100, default_ttl=300)
        loader = MultiFileLoader(cache=cache, enable_cache=True)

        # Add some data to cache
        cache.set("test_key", {"test": "data"})
        assert cache.get("test_key") == {"test": "data"}

        # Clear cache
        loader.clear_cache()
        assert cache.get("test_key") is None

    def test_clear_cache_no_cache(self):
        """Test clearing cache when no cache is available."""
        loader = MultiFileLoader(enable_cache=False)

        # Should not raise an error
        loader.clear_cache()

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        cache = SmartCache(max_size=100, default_ttl=300)
        loader = MultiFileLoader(cache=cache, enable_cache=True)

        # Add some data to cache
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})

        stats = loader.get_cache_stats()

        assert "enabled" in stats
        assert "cache_type" in stats
        assert "smart_cache_stats" in stats
        assert stats["enabled"] is True
        assert stats["cache_type"] == "SmartCache"
        assert "hits" in stats["smart_cache_stats"]
        assert "misses" in stats["smart_cache_stats"]
        assert "size" in stats["smart_cache_stats"]
        assert stats["smart_cache_stats"]["size"] == 2

    def test_get_cache_stats_no_cache(self):
        """Test getting cache statistics when no cache is available."""
        loader = MultiFileLoader(enable_cache=False)

        stats = loader.get_cache_stats()
        assert stats == {"enabled": False}

    def test_invalidate_file_cache(self):
        """Test invalidating cache for specific file."""
        cache = SmartCache(max_size=100, default_ttl=300)
        loader = MultiFileLoader(cache=cache, enable_cache=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_data = {"key": "value"}
            test_file.write_text(json.dumps(test_data))

            # Load file to populate cache
            loader._load_files([test_file])

            # Invalidate cache for this file
            loader.invalidate_file_cache(test_file)

            # Cache should be cleared for this file (pattern-based invalidation)
            # The actual cache key format is: multi_file:{file_path}:{mtime}
            cache_key = f"multi_file:{test_file}:{test_file.stat().st_mtime}"
            assert cache.get(cache_key) is None

    def test_invalidate_file_cache_no_cache(self):
        """Test invalidating cache when no cache is available."""
        loader = MultiFileLoader(enable_cache=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_file.write_text('{"key": "value"}')

            # Should not raise an error
            loader.invalidate_file_cache(test_file)

    def test_load_and_merge_with_kwargs(self):
        """Test load_and_merge with additional kwargs."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            test_file.write_text('{"key": "value"}')

            result = loader.load_and_merge(
                [test_file], strategy="deep", test_kwarg="test_value"
            )

            assert result == {"key": "value"}

    def test_load_and_merge_empty_files(self):
        """Test load_and_merge with empty file list."""
        loader = MultiFileLoader()

        result = loader.load_and_merge([])
        assert result == {}

    def test_load_and_merge_nonexistent_file(self):
        """Test load_and_merge with nonexistent file."""
        loader = MultiFileLoader()

        # Nonexistent files are skipped, returns empty dict
        result = loader.load_and_merge(["nonexistent.json"])
        assert result == {}

    def test_load_and_merge_invalid_file_format(self):
        """Test load_and_merge with invalid file format."""
        loader = MultiFileLoader()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.invalid"
            test_file.write_text("invalid content")

            # Invalid file formats are skipped with a warning, returns empty dict
            result = loader.load_and_merge([test_file])
            assert result == {}
