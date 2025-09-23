"""
Tests for SearchMixin.

This module contains unit tests for the SearchMixin class,
which provides search functionality for keys and values.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestSearchMixin:
    """Test class for SearchMixin functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data
        self.test_data = {
            "database": {"host": "localhost", "port": 5432, "name": "testdb"},
            "api": {"timeout": 30, "retries": 3, "version": "v1.0"},
            "debug": True,
            "features": ["auth", "logging", "caching"],
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_key_with_wildcards(self) -> None:
        """
        Scenario: Find keys using wildcard patterns

        Expected:
        - Should find all keys matching the pattern
        - Should support wildcard characters like * and ?
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test wildcard patterns
        results = fm.find_key("database.*")
        assert "database.host" in results
        assert "database.port" in results
        assert "database.name" in results

        results = fm.find_key("api.*")
        assert "api.timeout" in results
        assert "api.retries" in results
        assert "api.version" in results

    def test_find_key_without_wildcards(self) -> None:
        """
        Scenario: Find keys using simple substring search

        Expected:
        - Should find keys containing the substring
        - Should not use wildcard matching when disabled
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test substring search
        results = fm.find_key("host", use_wildcards=False)
        assert "database.host" in results

        results = fm.find_key("timeout", use_wildcards=False)
        assert "api.timeout" in results

    def test_find_value_basic(self) -> None:
        """
        Scenario: Find all keys containing a specific value

        Expected:
        - Should find keys with exact value matches
        - Should work with different data types
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test finding string values
        results = fm.find_value("localhost")
        assert "database.host" in results

        results = fm.find_value(30)
        assert "api.timeout" in results

        results = fm.find_value(True)
        assert "debug" in results

    def test_find_value_deep_search(self) -> None:
        """
        Scenario: Find values in nested structures

        Expected:
        - Should search recursively in nested data
        - Should find values at any depth
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test deep search
        results = fm.find_value("localhost", deep=True)
        assert "database.host" in results

        results = fm.find_value("auth", deep=True)
        assert "features.0" in results

    def test_find_value_shallow_search(self) -> None:
        """
        Scenario: Find values only at top level

        Expected:
        - Should only search at the top level when deep=False
        - Should not search in nested structures
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test shallow search
        results = fm.find_value("localhost", deep=False)
        assert len(results) == 0  # localhost is nested, not at top level

        results = fm.find_value(True, deep=False)
        assert "debug" in results  # debug is at top level

    def test_search_in_values_basic(self) -> None:
        """
        Scenario: Search for text in string values

        Expected:
        - Should find text within string values
        - Should return key-value pairs containing the text
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Test text search
        results = fm.search_in_values("localhost")
        assert len(results) > 0
        assert any("localhost" in str(result) for result in results)

    def test_search_in_values_case_sensitive(self) -> None:
        """
        Scenario: Search with case sensitivity control

        Expected:
        - Should respect case sensitivity setting
        - Should find matches based on case sensitivity
        """
        data = {"Name": "John", "name": "jane", "NAME": "BOB"}

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = data

        # Test case sensitive search
        results = fm.search_in_values("John", case_sensitive=True)
        assert len(results) > 0
        assert any("John" in str(result) for result in results)

        # Test case insensitive search
        results = fm.search_in_values("john", case_sensitive=False)
        assert len(results) > 0

    def test_search_in_values_with_empty_data(self) -> None:
        """
        Scenario: Search in empty data

        Expected:
        - Should return empty results for empty data
        - Should not raise errors
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = {}

        # All searches should return empty results
        assert fm.find_key("anything") == []
        assert fm.find_value("anything") == []
        assert fm.search_in_values("anything") == []

    def test_search_performance_with_large_data(self) -> None:
        """
        Scenario: Search performance with large data

        Expected:
        - Should complete search in reasonable time
        - Should find correct results in large datasets
        """
        large_data = {}
        for i in range(1000):
            large_data[f"key_{i}"] = f"value_{i}"

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = large_data

        # Test that search completes in reasonable time
        results = fm.find_key("key_*")
        assert len(results) == 1000

        results = fm.find_value("value_500")
        assert "key_500" in results

    def test_search_with_special_characters(self) -> None:
        """
        Scenario: Search with special characters in data

        Expected:
        - Should handle special characters correctly
        - Should find values with special characters
        """
        special_data = {
            "unicode": "café",
            "quotes": 'He said "Hello"',
            "special": "!@#$%^&*()",
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = special_data

        # Test finding special characters
        results = fm.find_value("café")
        assert "unicode" in results

        results = fm.search_in_values("Hello")
        assert len(results) > 0
