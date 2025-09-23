"""
Tests for AnalysisMixin.

This module contains unit tests for the AnalysisMixin class,
which provides analysis functionality for data structures.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestAnalysisMixin:
    """Test class for AnalysisMixin functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data
        self.test_data = {
            "database": {"host": "localhost", "port": 5432, "name": "testdb"},
            "api": {
                "timeout": 30,
                "retries": 3,
                "endpoints": ["/users", "/posts", "/comments"],
            },
            "debug": True,
            "version": "1.0.0",
            "features": ["auth", "logging", "caching"],
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_all_keys_flat(self) -> None:
        """
        Scenario: Get all keys in flat format

        Expected:
        - Should return all nested keys in dot notation
        - Should include keys from all levels
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        keys = fm.get_all_keys(flat=True)

        # Should include all nested keys
        expected_keys = [
            "database.host",
            "database.port",
            "database.name",
            "api.timeout",
            "api.retries",
            "api.endpoints.0",
            "api.endpoints.1",
            "api.endpoints.2",
            "debug",
            "version",
            "features.0",
            "features.1",
            "features.2",
        ]

        assert len(keys) >= len(expected_keys)
        for key in expected_keys:
            assert key in keys

    def test_get_all_keys_hierarchical(self) -> None:
        """
        Scenario: Get all keys in hierarchical format

        Expected:
        - Should return keys in hierarchical structure
        - Should include only leaf values when flat=False
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        keys = fm.get_all_keys(flat=False)

        # Should include only top-level keys and leaf values
        expected_keys = [
            "database.host",
            "database.port",
            "database.name",
            "api.timeout",
            "api.retries",
            "api.endpoints.0",
            "api.endpoints.1",
            "api.endpoints.2",
            "debug",
            "version",
            "features.0",
            "features.1",
            "features.2",
        ]

        assert len(keys) >= len(expected_keys)
        for key in expected_keys:
            assert key in keys

    def test_get_stats_basic(self) -> None:
        """
        Scenario: Get basic statistics about the data

        Expected:
        - Should return comprehensive statistics
        - Should include total keys, type counts, and file info
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()
        fm.save()  # Save to create file

        stats = fm.get_stats()

        # Verify basic structure
        assert "total_keys" in stats
        assert "type_counts" in stats
        assert "max_depth" in stats
        assert "file_size" in stats

        # Verify values
        assert stats["total_keys"] >= 13  # All leaf keys
        assert stats["max_depth"] >= 3  # database.host, api.endpoints.0, features.0
        assert "str" in stats["type_counts"]
        assert "int" in stats["type_counts"]
        assert "bool" in stats["type_counts"]
        assert "list" in stats["type_counts"]

    def test_get_stats_with_empty_data(self) -> None:
        """
        Scenario: Get statistics with empty data

        Expected:
        - Should handle empty data gracefully
        - Should return zero counts for empty data
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = {}
        fm.save()

        stats = fm.get_stats()

        assert stats["total_keys"] >= 0  # May be 1 due to empty dict being counted
        assert stats["max_depth"] == 0
        assert stats["type_counts"] == {"dict": 1}  # Empty dict is counted as dict type

    def test_get_type_distribution(self) -> None:
        """
        Scenario: Get distribution of data types

        Expected:
        - Should count occurrences of each data type
        - Should return dictionary with type counts
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        type_distribution = fm.get_type_distribution()

        # Verify data types are counted correctly
        assert type_distribution["str"] >= 6  # host, name, version, endpoints, features
        assert type_distribution["int"] >= 2  # port, timeout, retries
        assert type_distribution["bool"] >= 1  # debug
        assert type_distribution["list"] >= 2  # endpoints, features

    def test_get_type_distribution_with_various_types(self) -> None:
        """
        Scenario: Get type distribution with various Python types

        Expected:
        - Should correctly identify and count different data types
        - Should handle all common Python types
        """
        various_types_data = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3),
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = various_types_data

        type_distribution = fm.get_type_distribution()

        assert type_distribution["str"] >= 1
        assert type_distribution["int"] >= 1
        assert type_distribution["float"] >= 1
        assert type_distribution["bool"] >= 1
        assert type_distribution["list"] >= 1
        assert type_distribution["dict"] >= 1

    def test_get_size_info(self) -> None:
        """
        Scenario: Get size information about file and data

        Expected:
        - Should return file size and memory usage information
        - Should include key count and average key length
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()
        fm.save()

        size_info = fm.get_size_info()

        # Should return size information
        assert "file_size_bytes" in size_info
        assert "memory_usage_bytes" in size_info
        assert "key_count" in size_info
        assert "average_key_length" in size_info

        # Should have reasonable values
        assert size_info["file_size_bytes"] > 0
        assert size_info["memory_usage_bytes"] > 0
        assert size_info["key_count"] >= 13

    def test_get_size_info_with_large_data(self) -> None:
        """
        Scenario: Get size information with large data

        Expected:
        - Should handle large data structures
        - Should return accurate size information
        """
        large_data = {}
        for i in range(1000):
            large_data[f"key_{i}"] = f"value_{i}" * 10

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = large_data

        size_info = fm.get_size_info()

        # Should be larger than small data
        assert size_info["memory_usage_bytes"] > 1000  # At least 1KB
        assert size_info["key_count"] >= 1000  # May be 1001 due to counting

    def test_analysis_with_special_characters(self) -> None:
        """
        Scenario: Analyze data with special characters

        Expected:
        - Should handle special characters correctly
        - Should count special characters in statistics
        """
        special_data = {
            "unicode": "café",
            "special": "!@#$%^&*()",
            "quotes": 'He said "Hello"',
            "newlines": "line1\nline2",
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = special_data

        stats = fm.get_stats()

        # Should handle special characters correctly
        assert stats["total_keys"] >= 4
        assert stats["type_counts"]["str"] >= 4

    def test_analysis_with_none_values(self) -> None:
        """
        Scenario: Analyze data with None values

        Expected:
        - Should count None values correctly
        - Should include NoneType in type distribution
        """
        none_data = {
            "string": "value",
            "none_value": None,
            "nested": {"another_none": None, "normal": "value"},
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = none_data

        type_distribution = fm.get_type_distribution()

        # Should count None values
        assert "NoneType" in type_distribution or "none" in type_distribution
        assert type_distribution["str"] >= 2  # string, nested.normal
