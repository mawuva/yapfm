"""
Tests for SmartCache system.

This module tests the SmartCache class and its functionality including
TTL, LRU eviction, memory management, and statistics.
"""

# mypy: ignore-errors

import threading
import time

from yapfm.cache.smart_cache import SmartCache


class TestSmartCache:
    """Test cases for SmartCache class."""

    def test_smart_cache_initialization(self):
        """
        Scenario: Initialize SmartCache with default parameters

        Expected:
        - Should create SmartCache instance with default values
        - Should have correct default configuration
        - Should initialize with empty cache
        """
        cache = SmartCache()

        assert cache.max_size == 1000
        assert cache.max_memory_bytes == 100.0 * 1024 * 1024  # 100MB
        assert cache.default_ttl is None
        assert cache.cleanup_interval == 60.0
        assert cache.track_stats is True
        assert len(cache._cache) == 0
        assert cache._total_memory == 0

    def test_smart_cache_initialization_custom_params(self):
        """
        Scenario: Initialize SmartCache with custom parameters

        Expected:
        - Should create SmartCache with custom configuration
        - Should respect all custom parameter values
        - Should maintain custom settings correctly
        """
        cache = SmartCache(
            max_size=500,
            max_memory_mb=50.0,
            default_ttl=1800.0,
            cleanup_interval=30.0,
            track_stats=False,
        )

        assert cache.max_size == 500
        assert cache.max_memory_bytes == 50.0 * 1024 * 1024  # 50MB
        assert cache.default_ttl == 1800.0
        assert cache.cleanup_interval == 30.0
        assert cache.track_stats is False

    def test_smart_cache_basic_operations(self):
        """
        Scenario: Perform basic cache operations

        Expected:
        - Should set and retrieve values correctly
        - Should check key existence properly
        - Should delete keys successfully
        - Should handle nonexistent keys gracefully
        """
        cache = SmartCache()

        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.has_key("key1") is True

        # Test get with default
        assert cache.get("nonexistent", "default") == "default"

        # Test delete
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.has_key("key1") is False

        # Test delete nonexistent key
        assert cache.delete("nonexistent") is False

    def test_smart_cache_ttl_functionality(self):
        """
        Scenario: Test TTL (Time-To-Live) functionality

        Expected:
        - Should expire entries after TTL period
        - Should return None for expired entries
        - Should handle TTL timing correctly
        """
        cache = SmartCache(default_ttl=0.1)  # 100ms TTL

        # Set value with TTL
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None
        assert cache.has_key("key1") is False

    def test_smart_cache_custom_ttl(self):
        """
        Scenario: Test custom TTL per entry

        Expected:
        - Should allow custom TTL per entry
        - Should use default TTL when not specified
        - Should handle mixed TTL scenarios correctly
        """
        cache = SmartCache(default_ttl=3600.0)  # 1 hour default

        # Set with custom TTL
        cache.set("key1", "value1", ttl=0.1)  # 100ms
        cache.set("key2", "value2")  # Uses default TTL

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        # Wait for first key to expire
        time.sleep(0.2)
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"  # Still valid

    def test_smart_cache_lru_eviction(self):
        """
        Scenario: Test LRU (Least Recently Used) eviction policy

        Expected:
        - Should evict least recently used entries when full
        - Should maintain access order correctly
        - Should preserve most recently used entries
        """
        cache = SmartCache(max_size=3)

        # Fill cache to capacity
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert len(cache._cache) == 3

        # Access key1 to make it most recently used
        cache.get("key1")

        # Add new key - should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert len(cache._cache) == 3
        assert cache.has_key("key1") is True  # Most recently used
        assert cache.has_key("key2") is False  # Evicted
        assert cache.has_key("key3") is True
        assert cache.has_key("key4") is True

    def test_smart_cache_memory_eviction(self):
        """
        Scenario: Test memory-based eviction

        Expected:
        - Should evict entries when memory limit is exceeded
        - Should respect memory constraints
        - Should handle large data entries properly
        """
        cache = SmartCache(max_memory_mb=0.001)  # 1KB limit

        # Add large value
        large_data = "x" * 2000  # 2KB
        cache.set("large", large_data)

        # Should be evicted due to memory limit
        assert cache.get("large") is None

    def test_smart_cache_size_estimation(self):
        """
        Scenario: Test size estimation functionality

        Expected:
        - Should estimate size for different data types
        - Should return positive size values
        - Should handle various data structures
        """
        cache = SmartCache()

        # Test with different data types
        cache.set("string", "test")
        cache.set("number", 42)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"a": 1, "b": 2})

        # All should have size > 0
        for key in ["string", "number", "list", "dict"]:
            entry = cache._cache[key]
            assert entry.size > 0

    def test_smart_cache_cleanup_functionality(self):
        """
        Scenario: Test automatic cleanup of expired entries

        Expected:
        - Should automatically clean up expired entries
        - Should respect cleanup interval timing
        - Should remove expired entries from cache
        """
        cache = SmartCache(cleanup_interval=0.1)  # 100ms cleanup interval

        # Set value with short TTL
        cache.set("key1", "value1", ttl=0.05)  # 50ms TTL

        # Wait for expiration but before cleanup
        time.sleep(0.06)
        assert cache.get("key1") is None  # Should be expired

        # Wait for cleanup interval
        time.sleep(0.1)
        cache.get("dummy")  # Trigger cleanup

        # Expired entry should be removed from cache
        assert "key1" not in cache._cache

    def test_smart_cache_statistics(self):
        """
        Scenario: Test cache statistics tracking

        Expected:
        - Should track hits and misses correctly
        - Should calculate hit rate properly
        - Should maintain accurate cache size
        """
        cache = SmartCache(track_stats=True)

        # Initial stats
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0

        # Test hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["hit_rate"] == 0.5

    def test_smart_cache_no_stats_tracking(self):
        """
        Scenario: Test cache without statistics tracking

        Expected:
        - Should not track statistics when disabled
        - Should return zero stats when tracking is off
        - Should perform operations without stat overhead
        """
        cache = SmartCache(track_stats=False)

        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_smart_cache_pattern_invalidation(self):
        """
        Scenario: Test pattern-based invalidation

        Expected:
        - Should invalidate keys matching pattern
        - Should return count of invalidated keys
        - Should preserve non-matching keys
        """
        cache = SmartCache()

        # Add multiple keys
        cache.set("user:1", "alice")
        cache.set("user:2", "bob")
        cache.set("config:db", "localhost")
        cache.set("config:port", "5432")

        # Invalidate user keys
        invalidated = cache.invalidate_pattern("user:*")
        assert invalidated == 2

        assert cache.has_key("user:1") is False
        assert cache.has_key("user:2") is False
        assert cache.has_key("config:db") is True
        assert cache.has_key("config:port") is True

    def test_smart_cache_clear(self):
        """
        Scenario: Test cache clearing

        Expected:
        - Should remove all entries from cache
        - Should reset memory usage to zero
        - Should maintain cache configuration
        """
        cache = SmartCache()

        # Add some data
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert len(cache._cache) == 2

        # Clear cache
        cache.clear()

        assert len(cache._cache) == 0
        assert cache._total_memory == 0

    def test_smart_cache_thread_safety(self):
        """
        Scenario: Test thread safety of cache operations

        Expected:
        - Should handle concurrent access safely
        - Should maintain data consistency
        - Should not cause race conditions
        """
        cache = SmartCache()
        results = []

        def worker(thread_id):
            for i in range(100):
                key = f"key_{thread_id}_{i}"
                value = f"value_{thread_id}_{i}"
                cache.set(key, value)
                retrieved = cache.get(key)
                results.append((key, value, retrieved))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations were successful
        for key, expected_value, actual_value in results:
            assert actual_value == expected_value

    def test_smart_cache_access_count_tracking(self):
        """
        Scenario: Test access count tracking

        Expected:
        - Should track number of accesses per key
        - Should increment count on each access
        - Should maintain accurate access statistics
        """
        cache = SmartCache()

        cache.set("key1", "value1")

        # Access multiple times
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")

        entry = cache._cache["key1"]
        assert entry.access_count == 3

    def test_smart_cache_last_access_tracking(self):
        """
        Scenario: Test last access time tracking

        Expected:
        - Should track last access time for each key
        - Should update timestamp on each access
        - Should maintain accurate timing information
        """
        cache = SmartCache()

        cache.set("key1", "value1")
        initial_time = time.time()

        # Access after a delay
        time.sleep(0.01)
        cache.get("key1")

        entry = cache._cache["key1"]
        assert entry.last_access > initial_time

    def test_smart_cache_replace_existing_key(self):
        """
        Scenario: Test replacing existing key

        Expected:
        - Should replace value for existing key
        - Should maintain single entry per key
        - Should update value correctly
        """
        cache = SmartCache()

        # Set initial value
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Replace with new value
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

        # Should still be only one entry
        assert len(cache._cache) == 1

    def test_smart_cache_memory_usage_calculation(self):
        """
        Scenario: Test memory usage calculation

        Expected:
        - Should calculate memory usage correctly
        - Should track total memory consumption
        - Should provide accurate memory statistics
        """
        cache = SmartCache()

        # Add some data
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()
        assert stats["memory_usage_mb"] > 0
        assert stats["max_memory_mb"] == 100.0

    def test_smart_cache_edge_cases(self):
        """
        Scenario: Test edge cases and error conditions

        Expected:
        - Should handle empty string keys
        - Should handle None values
        - Should handle very long keys
        """
        cache = SmartCache()

        # Test with empty string key
        cache.set("", "empty_key")
        assert cache.get("") == "empty_key"

        # Test with None value
        cache.set("none", None)
        assert cache.get("none") is None

        # Test with very long key
        long_key = "x" * 1000
        cache.set(long_key, "long_key_value")
        assert cache.get(long_key) == "long_key_value"

    def test_smart_cache_eviction_stats(self):
        """
        Scenario: Test eviction statistics

        Expected:
        - Should track number of evictions
        - Should increment eviction count when cache is full
        - Should maintain accurate eviction statistics
        """
        cache = SmartCache(max_size=2)

        # Fill cache and trigger evictions
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        stats = cache.get_stats()
        assert stats["evictions"] >= 1

    def test_smart_cache_expired_cleanup_stats(self):
        """
        Scenario: Test expired cleanup statistics

        Expected:
        - Should track number of expired cleanups
        - Should increment cleanup count when expired entries are removed
        - Should maintain accurate cleanup statistics
        """
        cache = SmartCache(cleanup_interval=0.1)

        # Set value with short TTL
        cache.set("key1", "value1", ttl=0.05)

        # Wait for expiration and cleanup
        time.sleep(0.2)
        cache.get("dummy")  # Trigger cleanup

        stats = cache.get_stats()
        assert stats["expired_cleanups"] >= 1

    def test_smart_cache_with_custom_size(self):
        """
        Scenario: Test cache with custom size estimation

        Expected:
        - Should accept custom size values
        - Should use custom size instead of estimation
        - Should respect custom size in memory calculations
        """
        cache = SmartCache()

        # Set with custom size
        cache.set("key1", "value1", size=2048)

        entry = cache._cache["key1"]
        assert entry.size == 2048

    def test_smart_cache_hit_rate_calculation(self):
        """
        Scenario: Test hit rate calculation

        Expected:
        - Should calculate hit rate as hits/(hits+misses)
        - Should return 0.0 when no requests made
        - Should provide accurate hit rate statistics
        """
        cache = SmartCache()

        # No requests yet
        stats = cache.get_stats()
        assert stats["hit_rate"] == 0.0

        # Add some hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["hit_rate"] == 2 / 3  # 2 hits out of 3 requests
