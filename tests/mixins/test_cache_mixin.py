"""
Tests for CacheMixin.

This module contains unit tests for the CacheMixin class,
which provides caching functionality for key operations.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

from yapfm.cache.smart_cache import SmartCache
from yapfm.mixins.cache_mixin import CacheMixin
from yapfm.mixins.key_operations_mixin import KeyOperationsMixin


class MockFileManager(CacheMixin, KeyOperationsMixin):
    """Mock file manager for testing CacheMixin."""

    def __init__(
        self,
        path: Path,
        auto_create: bool = False,
        document: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True,
        cache: Optional[SmartCache] = None,
    ) -> None:
        self.path = path
        self.auto_create = auto_create
        self.document = document or {}
        self._loaded = True
        self._dirty = False
        self.strategy = MagicMock()
        self.enable_cache = enable_cache
        self.unified_cache = cache or (SmartCache() if enable_cache else None)
        super().__init__()

    def exists(self) -> bool:
        """Check if file exists."""
        return self.path.exists()

    def is_loaded(self) -> bool:
        """Check if file is loaded."""
        return self._loaded

    def load(self) -> None:
        """Load file."""
        self._loaded = True

    def save(self) -> None:
        """Save file."""
        self._dirty = False

    def get_cache(self) -> Optional[SmartCache]:
        """Get the cache instance."""
        if self.enable_cache:
            return self.unified_cache
        return None

    def _generate_cache_key(
        self,
        dot_key: Optional[str],
        path: Optional[list],
        key_name: Optional[str],
        key_type: str = "key",
    ) -> str:
        """Generate cache key for testing."""
        if dot_key:
            return f"key:{dot_key}"
        elif path and key_name:
            return f"key:{'.'.join(path)}.{key_name}"
        else:
            return "key:root"


class TestCacheMixin:
    """Test class for CacheMixin."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data
        self.test_data = {
            "database": {"host": "localhost", "port": 5432, "name": "testdb"},
            "api": {"timeout": 30, "retries": 3},
            "debug": True,
            "version": "1.0.0",
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_value_with_cache_enabled(self) -> None:
        """Test get_value with cache enabled."""
        # Create mock file manager with cache
        fm = MockFileManager(self.test_file, document=self.test_data)

        # First call should load from document and cache
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            result = fm.get_value("database.host")

            assert result == "localhost"
            mock_get_key.assert_called_once_with(
                fm, dot_key="database.host", path=None, key_name=None, default=None
            )

        # Second call should use cache (no call to get_key)
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            result = fm.get_value("database.host")

            assert result == "localhost"
            mock_get_key.assert_not_called()

    def test_get_value_with_cache_disabled(self) -> None:
        """Test get_value with cache disabled."""
        # Create mock file manager without cache
        fm = MockFileManager(
            self.test_file, document=self.test_data, enable_cache=False
        )

        # Both calls should go to get_key (no caching)
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"

            result1 = fm.get_value("database.host")
            result2 = fm.get_value("database.host")

            assert result1 == "localhost"
            assert result2 == "localhost"
            assert mock_get_key.call_count == 2

    def test_get_value_with_default(self) -> None:
        """Test get_value with default value."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "default_host"
            result = fm.get_value("nonexistent.key", default="default_host")

            assert result == "default_host"
            mock_get_key.assert_called_once_with(
                fm,
                dot_key="nonexistent.key",
                path=None,
                key_name=None,
                default="default_host",
            )

    def test_get_value_caches_none_values(self) -> None:
        """Test that None values are properly cached."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = None

            # First call
            result1 = fm.get_value("nonexistent.key")
            assert result1 is None

            # Second call should use cache
            result2 = fm.get_value("nonexistent.key")
            assert result2 is None

            # get_key should only be called once
            mock_get_key.assert_called_once()

    def test_set_value_invalidates_cache(self) -> None:
        """Test that set_value invalidates cache."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # First, cache a value
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            fm.get_value("database.host")

        # Now set a new value
        with patch.object(KeyOperationsMixin, "set_key") as mock_set_key:
            fm.set_value("database.host", "new_host")
            mock_set_key.assert_called_once_with(
                fm,
                "new_host",
                dot_key="database.host",
                path=None,
                key_name=None,
                overwrite=True,
            )

        # Cache should be invalidated, so next get should call get_key again
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "new_host"
            result = fm.get_value("database.host")

            assert result == "new_host"
            mock_get_key.assert_called_once()

    def test_set_value_with_overwrite_false(self) -> None:
        """Test set_value with overwrite=False."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        with patch.object(KeyOperationsMixin, "set_key") as mock_set_key:
            fm.set_value("database.host", "new_host", overwrite=False)
            mock_set_key.assert_called_once_with(
                fm,
                "new_host",
                dot_key="database.host",
                path=None,
                key_name=None,
                overwrite=False,
            )

    def test_set_value_with_no_cache(self) -> None:
        """Test set_value when cache is disabled."""
        fm = MockFileManager(
            self.test_file, document=self.test_data, enable_cache=False
        )

        with patch.object(KeyOperationsMixin, "set_key") as mock_set_key:
            fm.set_value("database.host", "new_host")
            mock_set_key.assert_called_once_with(
                fm,
                "new_host",
                dot_key="database.host",
                path=None,
                key_name=None,
                overwrite=True,
            )

    def test_clear_cache(self) -> None:
        """Test clear_cache method."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Cache some values
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            fm.get_value("database.host")
            fm.get_value("database.port")

        # Verify cache has entries
        assert len(fm.unified_cache._cache) > 0

        # Clear cache
        fm.clear_cache()

        # Verify cache is empty
        assert len(fm.unified_cache._cache) == 0

    def test_clear_cache_with_no_cache(self) -> None:
        """Test clear_cache when cache is disabled."""
        fm = MockFileManager(
            self.test_file, document=self.test_data, enable_cache=False
        )

        # Should not raise any errors
        fm.clear_cache()

    def test_invalidate_cache_all(self) -> None:
        """Test invalidate_cache without pattern (clear all)."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Cache some values
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            fm.get_value("database.host")
            fm.get_value("database.port")

        # Verify cache has entries
        initial_count = len(fm.unified_cache._cache)
        assert initial_count > 0

        # Invalidate all cache
        invalidated_count = fm.invalidate_cache()

        # Should return the number of invalidated entries
        assert invalidated_count == initial_count
        assert len(fm.unified_cache._cache) == 0

    def test_invalidate_cache_with_pattern(self) -> None:
        """Test invalidate_cache with pattern."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Cache some values
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            fm.get_value("database.host")
            fm.get_value("database.port")
            fm.get_value("api.timeout")

        # Mock the cache's invalidate_pattern method
        with patch.object(fm.unified_cache, "invalidate_pattern") as mock_invalidate:
            mock_invalidate.return_value = 2
            result = fm.invalidate_cache("database.*")

            assert result == 2
            mock_invalidate.assert_called_once_with("database.*")

    def test_invalidate_cache_with_no_cache(self) -> None:
        """Test invalidate_cache when cache is disabled."""
        fm = MockFileManager(
            self.test_file, document=self.test_data, enable_cache=False
        )

        # Should return 0 and not raise errors
        result = fm.invalidate_cache()
        assert result == 0

        result = fm.invalidate_cache("pattern.*")
        assert result == 0

    def test_cache_key_generation(self) -> None:
        """Test cache key generation."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Test with dot_key
        key1 = fm._generate_cache_key("database.host", None, None, "key")
        assert key1 == "key:database.host"

        # Test with path and key_name
        key2 = fm._generate_cache_key(None, ["database"], "host", "key")
        assert key2 == "key:database.host"

        # Test with no parameters
        key3 = fm._generate_cache_key(None, None, None, "key")
        assert key3 == "key:root"

    def test_cache_statistics(self) -> None:
        """Test cache statistics tracking."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Initial stats should be empty
        stats = fm.unified_cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Cache a value (miss)
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"
            fm.get_value("database.host")

        # Get from cache (hit)
        fm.get_value("database.host")

        # Check stats
        stats = fm.unified_cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_with_different_value_types(self) -> None:
        """Test caching different value types."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        test_values = [
            ("string", "test_string"),
            ("number", 42),
            ("float", 3.14),
            ("boolean", True),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value"}),
            ("none", None),
        ]

        for key, value in test_values:
            with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
                mock_get_key.return_value = value

                # First call (cache miss)
                result1 = fm.get_value(key)
                assert result1 == value

                # Second call (cache hit)
                result2 = fm.get_value(key)
                assert result2 == value

                # get_key should only be called once
                mock_get_key.assert_called_once()

    def test_cache_sentinel_object_handling(self) -> None:
        """Test that sentinel objects are handled correctly."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Test with a value that might be confused with sentinel
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = object()  # Return a unique object

            result1 = fm.get_value("test.key")
            result2 = fm.get_value("test.key")

            # Both should return the same object
            assert result1 is result2
            mock_get_key.assert_called_once()

    def test_concurrent_cache_access(self) -> None:
        """Test cache behavior under concurrent access simulation."""
        fm = MockFileManager(self.test_file, document=self.test_data)

        # Simulate concurrent access by calling get_value multiple times
        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"

            # Multiple calls should only result in one get_key call
            results = []
            for _ in range(5):
                results.append(fm.get_value("database.host"))

            # All results should be the same
            assert all(r == "localhost" for r in results)
            mock_get_key.assert_called_once()

    def test_cache_memory_management(self) -> None:
        """Test cache memory management."""
        # Create cache with small limits
        cache = SmartCache(max_size=2, max_memory_mb=0.001)
        fm = MockFileManager(self.test_file, document=self.test_data, cache=cache)

        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "value"

            # Add more items than cache can hold
            fm.get_value("key1")
            fm.get_value("key2")
            fm.get_value("key3")  # This should trigger eviction

            # Cache should not exceed max_size
            assert len(fm.unified_cache._cache) <= 2

    def test_cache_ttl_expiration(self) -> None:
        """Test cache TTL expiration."""
        # Create cache with very short TTL
        cache = SmartCache(default_ttl=0.001)  # 1ms TTL
        fm = MockFileManager(self.test_file, document=self.test_data, cache=cache)

        with patch.object(KeyOperationsMixin, "get_key") as mock_get_key:
            mock_get_key.return_value = "localhost"

            # First call
            fm.get_value("database.host")

            # Wait for TTL to expire
            import time

            time.sleep(0.01)  # 10ms

            # Second call should be a cache miss due to expiration
            fm.get_value("database.host")

            # get_key should be called twice (once for each call)
            assert mock_get_key.call_count == 2
