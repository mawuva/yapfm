"""
Comprehensive test suite for all cache modules.

This module provides a single entry point to run all cache-related tests
and demonstrates the functionality of the cache system.
"""

# mypy: ignore-errors

import tempfile
import time
from pathlib import Path

import pytest

from yapfm.cache.lazy_loading import LazySectionLoader
from yapfm.cache.smart_cache import SmartCache
from yapfm.cache.streaming_reader import StreamingFileReader
from yapfm.cache.types import CacheEntry


class TestCacheIntegration:
    """Integration tests for the complete cache system."""

    def test_cache_system_integration(self):
        """Test the complete cache system working together."""
        # Create a smart cache
        cache = SmartCache(max_size=100, default_ttl=60.0)

        # Test basic operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test lazy loading with cache
        def loader_func():
            return {"data": "loaded_from_function"}

        loader = LazySectionLoader(loader_func, "section1", cache)

        # First load should call the function
        result = loader.get()
        assert result["data"] == "loaded_from_function"

        # Second load should come from cache
        result2 = loader.get()
        assert result2["data"] == "loaded_from_function"

        # Verify it's in the cache
        assert cache.has_key("section1")
        assert cache.get("section1")["data"] == "loaded_from_function"

    def test_streaming_with_cache_integration(self):
        """Test streaming reader with cache integration."""
        # Create test file
        content = "Line 1\nLine 2\nLine 3\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            # Use streaming reader
            with StreamingFileReader(file_path) as reader:
                lines = list(reader.read_lines())
                assert lines == ["Line 1", "Line 2", "Line 3"]

            # Cache the result
            cache = SmartCache()
            cache.set("file_content", lines)

            # Verify caching worked
            cached_lines = cache.get("file_content")
            assert cached_lines == ["Line 1", "Line 2", "Line 3"]

        finally:
            file_path.unlink()

    def test_cache_entry_with_real_data(self):
        """Test CacheEntry with real-world data."""
        # Create a complex data structure
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
            ],
            "config": {
                "database": {"host": "localhost", "port": 5432, "name": "myapp"},
                "cache": {"enabled": True, "ttl": 3600},
            },
            "metadata": {"version": "1.0.0", "created_at": time.time()},
        }

        # Create cache entry
        entry = CacheEntry(
            value=complex_data, timestamp=time.time(), ttl=3600.0, size=1024
        )

        # Test entry properties
        assert entry.value == complex_data
        assert entry.ttl == 3600.0
        assert entry.size == 1024
        assert entry.access_count == 0

        # Test access tracking
        entry.access_count += 1
        entry.last_access = time.time()

        assert entry.access_count == 1
        assert entry.last_access > 0

    def test_performance_characteristics(self):
        """Test performance characteristics of the cache system."""
        cache = SmartCache(max_size=1000, default_ttl=60.0)

        # Test bulk operations
        start_time = time.time()

        # Set many values
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")

        set_time = time.time() - start_time

        # Get many values
        start_time = time.time()

        for i in range(100):
            value = cache.get(f"key_{i}")
            assert value == f"value_{i}"

        get_time = time.time() - start_time

        # Performance should be reasonable
        assert set_time < 1.0  # Should set 100 values in less than 1 second
        assert get_time < 1.0  # Should get 100 values in less than 1 second

        # Test statistics
        stats = cache.get_stats()
        assert stats["hits"] == 100
        assert stats["misses"] == 0
        assert stats["size"] == 100

    def test_memory_management(self):
        """Test memory management features."""
        # Create cache with small memory limit
        cache = SmartCache(max_size=5, max_memory_mb=0.001)  # 1KB limit

        # Add large values that should trigger eviction
        large_data = "x" * 2000  # 2KB

        cache.set("large1", large_data)
        cache.set("large2", large_data)
        cache.set("large3", large_data)

        # Some values should be evicted due to memory limit
        stats = cache.get_stats()
        assert stats["evictions"] > 0

        # Cache size should be within limits
        assert stats["size"] <= 5

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        cache = SmartCache()

        # Test with problematic data
        cache.set("none_key", None)
        cache.set("empty_key", "")
        cache.set("zero_key", 0)
        cache.set("false_key", False)

        # All should be retrievable
        assert cache.get("none_key") is None
        assert cache.get("empty_key") == ""
        assert cache.get("zero_key") == 0
        assert cache.get("false_key") is False

        # Test lazy loader with error
        def error_loader():
            raise ValueError("Test error")

        loader = LazySectionLoader(error_loader, "error_section")

        # Should raise the error
        with pytest.raises(ValueError, match="Test error"):
            loader.get()

        # Should store the error
        assert loader.get_load_error() is not None
        assert isinstance(loader.get_load_error(), ValueError)

    def test_concurrent_access(self):
        """Test concurrent access to cache system."""
        import threading

        cache = SmartCache()
        results = []

        def worker(thread_id):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                cache.set(key, value)
                retrieved = cache.get(key)
                results.append((key, value, retrieved))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        for key, expected_value, actual_value in results:
            assert actual_value == expected_value

        # Verify cache has all the data
        stats = cache.get_stats()
        assert stats["size"] == 50  # 5 threads * 10 keys each

    def test_cache_lifecycle(self):
        """Test complete cache lifecycle."""
        # Create cache
        cache = SmartCache(max_size=10, default_ttl=1.0)  # 1 second TTL

        # Add data
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Verify data exists
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        # Wait for expiration
        time.sleep(1.1)

        # Data should be expired
        assert cache.get("key1") is None
        assert cache.get("key2") is None

        # Add new data
        cache.set("key3", "value3")
        assert cache.get("key3") == "value3"

        # Clear cache
        cache.clear()
        assert cache.get("key3") is None

        # Verify cache is empty
        stats = cache.get_stats()
        assert stats["size"] == 0

    def test_lazy_loading_lifecycle(self):
        """Test lazy loading lifecycle."""
        cache = SmartCache()
        call_count = 0

        def loader_func():
            nonlocal call_count
            call_count += 1
            return {"data": f"loaded_{call_count}"}

        loader = LazySectionLoader(loader_func, "test_section", cache)

        # First call should load
        result1 = loader.get()
        assert result1["data"] == "loaded_1"
        assert call_count == 1
        assert loader.is_loaded()

        # Second call should use cache
        result2 = loader.get()
        assert result2["data"] == "loaded_1"
        assert call_count == 1  # Should not call loader again

        # Invalidate and reload
        loader.invalidate()
        assert not loader.is_loaded()

        result3 = loader.get()
        assert result3["data"] == "loaded_2"
        assert call_count == 2

    def test_streaming_lifecycle(self):
        """Test streaming reader lifecycle."""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        try:
            # Test context manager
            with StreamingFileReader(file_path, chunk_size=10) as reader:
                assert reader._file_handle is not None

                # Read all lines
                lines = list(reader.read_lines())
                assert len(lines) == 5
                assert lines[0] == "Line 1"
                assert lines[4] == "Line 5"

                # Test progress
                progress = reader.get_progress()
                assert progress >= 0.8  # Should be near 100%

            # File should be closed
            assert reader._file_handle is None

        finally:
            file_path.unlink()


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v"])
