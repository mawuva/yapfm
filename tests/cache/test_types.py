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
        """
        Scenario: Create basic CacheEntry instance

        Expected:
        - Should create CacheEntry with required parameters
        - Should set default values for optional parameters
        - Should maintain correct field values
        """
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
        """
        Scenario: Create CacheEntry with all parameters

        Expected:
        - Should create CacheEntry with all specified parameters
        - Should maintain all custom values
        - Should handle complex data types correctly
        """
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
        """
        Scenario: Create CacheEntry with default values

        Expected:
        - Should use default values for optional parameters
        - Should maintain correct default field values
        - Should allow modification of default values
        """
        value = 42
        timestamp = time.time()

        entry = CacheEntry(value=value, timestamp=timestamp)

        # Check default values
        assert entry.access_count == 0
        assert entry.last_access == 0.0
        assert entry.ttl is None
        assert entry.size == 0

    def test_cache_entry_immutability(self):
        """
        Scenario: Test CacheEntry field modification

        Expected:
        - Should allow modification of all fields
        - Should maintain updated values
        - Should support field updates after creation
        """
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
        """
        Scenario: Test CacheEntry with different value types

        Expected:
        - Should handle string values correctly
        - Should handle numeric values correctly
        - Should handle list and dict values correctly
        - Should handle None values correctly
        """
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
        """
        Scenario: Test CacheEntry with different TTL scenarios

        Expected:
        - Should handle None TTL correctly
        - Should handle positive TTL values
        - Should handle zero TTL values
        - Should maintain TTL values accurately
        """
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
        """
        Scenario: Test CacheEntry with negative values (edge cases)

        Expected:
        - Should handle negative access count
        - Should handle negative last access time
        - Should handle negative TTL values
        - Should handle negative size values
        """
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
        """
        Scenario: Test CacheEntry serialization with asdict

        Expected:
        - Should serialize to dictionary correctly
        - Should preserve all field values
        - Should handle complex nested data structures
        """
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
        """
        Scenario: Test CacheEntry equality comparison

        Expected:
        - Should compare entries with same values as equal
        - Should compare entries with different values as not equal
        - Should handle field-by-field comparison correctly
        """
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
        """
        Scenario: Test CacheEntry string representation

        Expected:
        - Should generate valid string representation
        - Should include class name in representation
        - Should not crash on repr() call
        """
        entry = CacheEntry(value="test", timestamp=1234567890.0)

        # Check that repr doesn't crash
        repr_str = repr(entry)
        assert isinstance(repr_str, str)
        assert "CacheEntry" in repr_str

    def test_cache_entry_with_complex_objects(self):
        """
        Scenario: Test CacheEntry with complex objects

        Expected:
        - Should handle function objects correctly
        - Should handle class instances correctly
        - Should preserve object references
        """
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
        """
        Scenario: Test CacheEntry edge cases

        Expected:
        - Should handle very large numeric values
        - Should handle very small numeric values
        - Should maintain precision with extreme values
        """
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
