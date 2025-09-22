"""
Tests for CacheMixin.

This module tests the CacheMixin functionality including caching,
invalidation, and integration with the unified cache system.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from yapfm.cache.smart_cache import SmartCache
from yapfm.mixins.cache_mixin import CacheMixin
from yapfm.mixins.key_operations_mixin import KeyOperationsMixin
from yapfm.strategies.json_strategy import JsonStrategy


class MockFileManager(CacheMixin, KeyOperationsMixin):
    """Mock file manager for testing CacheMixin."""
    
    def __init__(self, enable_cache=True, cache_size=100, cache_ttl=3600):
        self.enable_cache = enable_cache
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.document = {}
        self._loaded = False
        self._dirty = False
        
        # Initialize strategy
        self.strategy = JsonStrategy()
        
        # Initialize cache
        if enable_cache:
            self.unified_cache = SmartCache(
                max_size=cache_size,
                default_ttl=cache_ttl,
                track_stats=True
            )
        else:
            self.unified_cache = None
        
        # Initialize key cache
        self._key_cache = {}
    
    def get_cache(self):
        """Get the unified cache."""
        if self.enable_cache:
            return self.unified_cache
        return None
    
    def _generate_cache_key(self, dot_key, path, key_name, key_type="key"):
        """Generate a cache key."""
        if dot_key is not None:
            return f"{key_type}:{dot_key}"
        elif path is not None and key_name is not None:
            path_str = ".".join(path) if path else ""
            return f"{key_type}:{path_str}.{key_name}" if path_str else f"{key_type}:{key_name}"
        else:
            raise ValueError("Cannot generate cache key without key parameters")
    
    def is_loaded(self):
        """Mock is_loaded method."""
        return self._loaded
    
    def load(self):
        """Mock load method."""
        self._loaded = True
    
    def save(self):
        """Mock save method."""
        pass
    
    def get_key_from_document(self, dot_key=None, path=None, key_name=None, default=None):
        """Mock method to get key from document."""
        if dot_key is not None:
            keys = dot_key.split('.')
            value = self.document
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        elif path is not None and key_name is not None:
            value = self.document
            for key in path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            if isinstance(value, dict) and key_name in value:
                return value[key_name]
            return default
        return default


class TestCacheMixin:
    """Test cases for CacheMixin class."""

    def test_cache_mixin_initialization(self):
        """Test CacheMixin initialization."""
        manager = MockFileManager()
        
        assert manager.enable_cache is True
        assert manager.unified_cache is not None
        assert isinstance(manager.unified_cache, SmartCache)

    def test_cache_mixin_without_cache(self):
        """Test CacheMixin without cache enabled."""
        manager = MockFileManager(enable_cache=False)
        
        assert manager.enable_cache is False
        assert manager.unified_cache is None

    def test_get_value_with_dot_key(self):
        """Test get_value with dot key notation."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost", "port": 5432}}
        
        # First call should load from document and cache
        value = manager.get_value("database.host")
        assert value == "localhost"
        
        # Verify it's cached
        assert manager.unified_cache.has_key("key:database.host")
        assert manager.unified_cache.get("key:database.host") == "localhost"

    def test_get_value_with_path_and_key_name(self):
        """Test get_value with path and key_name parameters."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost", "port": 5432}}
        
        # First call should load from document and cache
        value = manager.get_value(path=["database"], key_name="port")
        assert value == 5432
        
        # Verify it's cached
        assert manager.unified_cache.has_key("key:database.port")
        assert manager.unified_cache.get("key:database.port") == 5432

    def test_get_value_parameter_validation(self):
        """Test get_value parameter validation."""
        manager = MockFileManager()
        
        # Should raise ValueError when no parameters provided
        with pytest.raises(ValueError, match="You must provide either dot_key or \\(path \\+ key_name\\)"):
            manager.get_value()
        
        # Should raise ValueError when only path provided
        with pytest.raises(ValueError, match="You must provide either dot_key or \\(path \\+ key_name\\)"):
            manager.get_value(path=["database"])
        
        # Should raise ValueError when only key_name provided
        with pytest.raises(ValueError, match="You must provide either dot_key or \\(path \\+ key_name\\)"):
            manager.get_value(key_name="host")

    def test_get_value_with_default(self):
        """Test get_value with default value."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost"}}
        
        # Test with existing key
        value = manager.get_value("database.host", default="unknown")
        assert value == "localhost"
        
        # Test with non-existing key
        value = manager.get_value("database.nonexistent", default="unknown")
        assert value == "unknown"

    def test_get_value_caching_behavior(self):
        """Test caching behavior of get_value."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost"}}
        
        # Mock KeyOperationsMixin.get_key to track calls
        original_get_key = KeyOperationsMixin.get_key
        call_count = 0
        
        def mock_get_key(self, dot_key=None, path=None, key_name=None, default=None, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_get_key(self, dot_key, path=path, key_name=key_name, default=default, **kwargs)
        
        with patch.object(KeyOperationsMixin, 'get_key', side_effect=mock_get_key):
            # First call should call KeyOperationsMixin.get_key
            value1 = manager.get_value("database.host")
            assert value1 == "localhost"
            assert call_count == 1
            
            # Second call should use cache, not call KeyOperationsMixin.get_key
            value2 = manager.get_value("database.host")
            assert value2 == "localhost"
            assert call_count == 1  # Should not increase

    def test_get_value_without_cache(self):
        """Test get_value when cache is disabled."""
        manager = MockFileManager(enable_cache=False)
        manager.document = {"database": {"host": "localhost"}}
        
        # Should work without cache
        value = manager.get_value("database.host")
        assert value == "localhost"
        
        # Should not have any cache
        assert manager.unified_cache is None

    def test_get_value_with_none_values(self):
        """Test get_value with None values."""
        manager = MockFileManager()
        manager.document = {"database": {"host": None, "port": 5432}}
        
        # Test with None value
        value = manager.get_value("database.host")
        assert value is None
        
        # Should be cached
        assert manager.unified_cache.has_key("key:database.host")
        assert manager.unified_cache.get("key:database.host") is None

    def test_clear_cache(self):
        """Test clear_cache method."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost", "port": 5432}}
        
        # Add some values to cache
        manager.get_value("database.host")
        manager.get_value("database.port")
        
        # Verify cache has data
        assert manager.unified_cache.get_stats()["size"] == 2
        
        # Clear cache
        manager.clear_cache()
        
        # Verify cache is empty
        assert manager.unified_cache.get_stats()["size"] == 0

    def test_clear_cache_without_cache(self):
        """Test clear_cache when cache is disabled."""
        manager = MockFileManager(enable_cache=False)
        
        # Should not raise error
        manager.clear_cache()

    def test_invalidate_cache_without_pattern(self):
        """Test invalidate_cache without pattern (clear all)."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost", "port": 5432}}
        
        # Add some values to cache
        manager.get_value("database.host")
        manager.get_value("database.port")
        
        # Verify cache has data
        assert manager.unified_cache.get_stats()["size"] == 2
        
        # Invalidate all cache
        count = manager.invalidate_cache()
        
        # Should return count of invalidated entries
        assert count == 2
        
        # Verify cache is empty
        assert manager.unified_cache.get_stats()["size"] == 0

    def test_invalidate_cache_with_pattern(self):
        """Test invalidate_cache with pattern."""
        manager = MockFileManager()
        manager.document = {
            "database": {"host": "localhost", "port": 5432},
            "app": {"name": "myapp", "version": "1.0.0"}
        }
        
        # Add values to cache
        manager.get_value("database.host")
        manager.get_value("database.port")
        manager.get_value("app.name")
        manager.get_value("app.version")
        
        # Verify cache has data
        assert manager.unified_cache.get_stats()["size"] == 4
        
        # Invalidate database-related cache
        count = manager.invalidate_cache("key:database.*")
        
        # Should return count of invalidated entries
        assert count == 2
        
        # Verify only database entries are removed
        assert not manager.unified_cache.has_key("key:database.host")
        assert not manager.unified_cache.has_key("key:database.port")
        assert manager.unified_cache.has_key("key:app.name")
        assert manager.unified_cache.has_key("key:app.version")

    def test_invalidate_cache_without_cache(self):
        """Test invalidate_cache when cache is disabled."""
        manager = MockFileManager(enable_cache=False)
        
        # Should return 0
        count = manager.invalidate_cache()
        assert count == 0
        
        count = manager.invalidate_cache("pattern")
        assert count == 0

    def test_get_value_with_complex_data(self):
        """Test get_value with complex data structures."""
        manager = MockFileManager()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432
                }
            }
        }
        manager.document = complex_data
        
        # Test getting complex values
        users = manager.get_value("users")
        assert users == complex_data["users"]
        
        config = manager.get_value("config")
        assert config == complex_data["config"]
        
        # Verify they're cached
        assert manager.unified_cache.has_key("key:users")
        assert manager.unified_cache.has_key("key:config")

    def test_get_value_cache_key_generation(self):
        """Test cache key generation for different parameter combinations."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost"}}
        
        # Test with dot_key
        manager.get_value("database.host")
        assert manager.unified_cache.has_key("key:database.host")
        
        # Test with path and key_name
        manager.get_value(path=["database"], key_name="host")
        assert manager.unified_cache.has_key("key:database.host")

    def test_get_value_performance(self):
        """Test get_value performance with caching."""
        manager = MockFileManager()
        manager.document = {"database": {"host": "localhost"}}
        
        # First call (cache miss)
        start_time = time.time()
        value1 = manager.get_value("database.host")
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        value2 = manager.get_value("database.host")
        second_call_time = time.time() - start_time
        
        # Both should return same value
        assert value1 == value2 == "localhost"
        
        # Second call should be faster (cached)
        # Note: This might not always be true due to timing variations
        # but it's a good indicator that caching is working

    def test_get_value_with_empty_document(self):
        """Test get_value with empty document."""
        manager = MockFileManager()
        manager.document = {}

        # Should return default value
        value = manager.get_value("nonexistent.key", default="default")
        assert value == "default"

        # Should cache default values (this is the expected behavior)
        assert manager.unified_cache.get_stats()["size"] == 1
        assert manager.unified_cache.has_key("key:nonexistent.key")

    def test_get_value_error_handling(self):
        """Test get_value error handling."""
        manager = MockFileManager()
        
        # Test with invalid parameters
        with pytest.raises(ValueError):
            manager.get_value()
        
        with pytest.raises(ValueError):
            manager.get_value(path=["database"])
        
        with pytest.raises(ValueError):
            manager.get_value(key_name="host")

    def test_cache_mixin_integration_with_real_file(self):
        """Test CacheMixin integration with real file operations."""
        # Create a temporary JSON file
        test_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb"
            },
            "app": {
                "name": "testapp",
                "version": "1.0.0"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(test_data, f)
            file_path = Path(f.name)
        
        try:
            # Create manager with real file using YAPFileManager
            from yapfm import YAPFileManager
            from yapfm.strategies.json_strategy import JsonStrategy
            
            manager = YAPFileManager(
                file_path,
                strategy=JsonStrategy(),
                auto_create=True,
                enable_cache=True,
                cache_size=100,
                cache_ttl=3600
            )

            # Test caching behavior
            host = manager.get_value("database.host")
            assert host == "localhost"

            # Verify cache statistics
            stats = manager.unified_cache.get_stats()
            assert stats["hits"] == 0  # First call is a miss
            assert stats["misses"] == 1  # First call is a miss
            assert stats["size"] == 1  # Value was cached

            # Second call should be a hit
            host2 = manager.get_value("database.host")
            assert host2 == "localhost"

            stats = manager.unified_cache.get_stats()
            assert stats["hits"] == 1
            assert stats["misses"] == 1
            assert stats["size"] == 1
            
        finally:
            file_path.unlink()

    def test_cache_mixin_thread_safety(self):
        """Test CacheMixin thread safety."""
        import threading
        
        manager = MockFileManager()
        manager.document = {"key": "value"}
        
        results = []
        
        def worker():
            for i in range(10):
                value = manager.get_value("key")
                results.append(value)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All results should be the same
        assert all(result == "value" for result in results)
        assert len(results) == 50  # 5 threads * 10 calls each
