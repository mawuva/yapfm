"""
Tests for cache types.

This module tests the CacheEntry dataclass and its functionality.
"""

# mypy: ignore-errors

import time
from dataclasses import asdict

from yapfm.cache.types import CacheEntry


class TestCacheEntry:
    """Test cases for CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test basic CacheEntry creation."""
        value = "test_value"
        timestamp = time.time()

        entry = CacheEntry(value=value, timestamp=timestamp)

        assert entry.value == value
        assert entry.timestamp == timestamp
        assert entry.access_count == 0
        assert entry.last_access == 0.0
        assert entry.ttl is None
        assert entry.size == 0

    def test_cache_entry_with_all_params(self):
        """Test CacheEntry creation with all parameters."""
        value = {"key": "value"}
        timestamp = time.time()
        access_count = 5
        last_access = time.time() - 100
        ttl = 3600.0
        size = 1024

        entry = CacheEntry(
            value=value,
            timestamp=timestamp,
            access_count=access_count,
            last_access=last_access,
            ttl=ttl,
            size=size,
        )

        assert entry.value == value
        assert entry.timestamp == timestamp
        assert entry.access_count == access_count
        assert entry.last_access == last_access
        assert entry.ttl == ttl
        assert entry.size == size

    def test_cache_entry_default_values(self):
        """Test CacheEntry with default values."""
        value = 42
        timestamp = time.time()

        entry = CacheEntry(value=value, timestamp=timestamp)

        # Check default values
        assert entry.access_count == 0
        assert entry.last_access == 0.0
        assert entry.ttl is None
        assert entry.size == 0

    def test_cache_entry_immutability(self):
        """Test that CacheEntry fields can be modified."""
        entry = CacheEntry(value="test", timestamp=time.time())

        # Should be able to modify fields
        entry.access_count = 10
        entry.last_access = time.time()
        entry.ttl = 1800.0
        entry.size = 512

        assert entry.access_count == 10
        assert entry.last_access > 0
        assert entry.ttl == 1800.0
        assert entry.size == 512

    def test_cache_entry_with_different_value_types(self):
        """Test CacheEntry with different value types."""
        timestamp = time.time()

        # Test with string
        entry_str = CacheEntry(value="string", timestamp=timestamp)
        assert entry_str.value == "string"

        # Test with number
        entry_int = CacheEntry(value=42, timestamp=timestamp)
        assert entry_int.value == 42

        # Test with list
        entry_list = CacheEntry(value=[1, 2, 3], timestamp=timestamp)
        assert entry_list.value == [1, 2, 3]

        # Test with dict
        entry_dict = CacheEntry(value={"a": 1, "b": 2}, timestamp=timestamp)
        assert entry_dict.value == {"a": 1, "b": 2}

        # Test with None
        entry_none = CacheEntry(value=None, timestamp=timestamp)
        assert entry_none.value is None

    def test_cache_entry_ttl_scenarios(self):
        """Test CacheEntry with different TTL scenarios."""
        timestamp = time.time()

        # No TTL (None)
        entry_no_ttl = CacheEntry(value="test", timestamp=timestamp, ttl=None)
        assert entry_no_ttl.ttl is None

        # Positive TTL
        entry_positive_ttl = CacheEntry(value="test", timestamp=timestamp, ttl=3600.0)
        assert entry_positive_ttl.ttl == 3600.0

        # Zero TTL
        entry_zero_ttl = CacheEntry(value="test", timestamp=timestamp, ttl=0.0)
        assert entry_zero_ttl.ttl == 0.0

    def test_cache_entry_negative_values(self):
        """Test CacheEntry with negative values (edge cases)."""
        timestamp = time.time()

        # Negative access count
        entry = CacheEntry(value="test", timestamp=timestamp, access_count=-1)
        assert entry.access_count == -1

        # Negative last access
        entry = CacheEntry(value="test", timestamp=timestamp, last_access=-100.0)
        assert entry.last_access == -100.0

        # Negative TTL
        entry = CacheEntry(value="test", timestamp=timestamp, ttl=-3600.0)
        assert entry.ttl == -3600.0

        # Negative size
        entry = CacheEntry(value="test", timestamp=timestamp, size=-1024)
        assert entry.size == -1024

    def test_cache_entry_serialization(self):
        """Test CacheEntry serialization with asdict."""
        value = {"nested": {"data": [1, 2, 3]}}
        timestamp = time.time()
        access_count = 3
        last_access = time.time() - 50
        ttl = 1800.0
        size = 2048

        entry = CacheEntry(
            value=value,
            timestamp=timestamp,
            access_count=access_count,
            last_access=last_access,
            ttl=ttl,
            size=size,
        )

        # Convert to dict
        entry_dict = asdict(entry)

        assert entry_dict["value"] == value
        assert entry_dict["timestamp"] == timestamp
        assert entry_dict["access_count"] == access_count
        assert entry_dict["last_access"] == last_access
        assert entry_dict["ttl"] == ttl
        assert entry_dict["size"] == size

    def test_cache_entry_equality(self):
        """Test CacheEntry equality comparison."""
        timestamp = time.time()

        entry1 = CacheEntry(value="test", timestamp=timestamp)
        entry2 = CacheEntry(value="test", timestamp=timestamp)
        entry3 = CacheEntry(value="different", timestamp=timestamp)

        # Same values should be equal
        assert entry1.value == entry2.value
        assert entry1.timestamp == entry2.timestamp

        # Different values should not be equal
        assert entry1.value != entry3.value

    def test_cache_entry_repr(self):
        """Test CacheEntry string representation."""
        entry = CacheEntry(value="test", timestamp=1234567890.0)

        # Check that repr doesn't crash
        repr_str = repr(entry)
        assert isinstance(repr_str, str)
        assert "CacheEntry" in repr_str

    def test_cache_entry_with_complex_objects(self):
        """Test CacheEntry with complex objects."""
        timestamp = time.time()

        # Test with function
        def test_func():
            return "test"

        entry_func = CacheEntry(value=test_func, timestamp=timestamp)
        assert entry_func.value == test_func

        # Test with class instance
        class TestClass:
            def __init__(self):
                self.data = "test"

        instance = TestClass()
        entry_instance = CacheEntry(value=instance, timestamp=timestamp)
        assert entry_instance.value == instance
        assert entry_instance.value.data == "test"

    def test_cache_entry_edge_cases(self):
        """Test CacheEntry edge cases."""
        timestamp = time.time()

        # Very large numbers
        entry_large = CacheEntry(
            value="test",
            timestamp=timestamp,
            access_count=999999999,
            last_access=999999999.0,
            ttl=999999999.0,
            size=999999999,
        )

        assert entry_large.access_count == 999999999
        assert entry_large.last_access == 999999999.0
        assert entry_large.ttl == 999999999.0
        assert entry_large.size == 999999999

        # Very small numbers
        entry_small = CacheEntry(
            value="test",
            timestamp=timestamp,
            access_count=0,
            last_access=0.0,
            ttl=0.0,
            size=0,
        )

        assert entry_small.access_count == 0
        assert entry_small.last_access == 0.0
        assert entry_small.ttl == 0.0
        assert entry_small.size == 0
