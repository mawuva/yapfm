"""
Search Mixin

This module provides search functionality for the FileManager.
The SearchMixin contains operations for finding keys, values, and searching content.
"""

# mypy: ignore-errors

import fnmatch
from typing import Any, List

from yapfm.helpers import traverse_data_structure


class SearchMixin:
    """
    Mixin for search operations.
    """

    def find_key(self, pattern: str, use_wildcards: bool = True) -> List[str]:
        """
        Find all keys matching a pattern.

        Args:
            pattern: Search pattern (supports wildcards like *, ?, [])
            use_wildcards: If True, uses fnmatch wildcards, otherwise simple substring search

        Returns:
            List of matching keys

        Example:
            >>> fm.find_key("database.*")  # Find database.host, database.port
            >>> fm.find_key("api.v[0-9]*")  # Find api.v1, api.v2, etc.
            >>> fm.find_key("host", use_wildcards=False)  # Simple substring search
        """
        all_keys = self.get_all_keys(flat=True)

        if use_wildcards:
            return [key for key in all_keys if fnmatch.fnmatch(key, pattern)]
        else:
            return [key for key in all_keys if pattern in key]

    def find_value(self, value: Any, deep: bool = True) -> List[str]:
        """
        Find all keys containing a specific value.

        Args:
            value: Value to search for
            deep: If True, searches recursively in nested structures

        Returns:
            List of keys containing the value

        Example:
            >>> fm.find_value("localhost")  # Find all keys with "localhost"
            >>> fm.find_value(5432)  # Find all keys with port 5432
        """
        matching_keys = []

        def visitor_func(val, key_path):
            if val == value:
                matching_keys.append(key_path)

        self.load_if_not_loaded()

        if deep:
            traverse_data_structure(self.document, "", visitor_func)
        else:
            # Only search at the top level
            if isinstance(self.document, dict):
                for key, val in self.document.items():
                    if val == value:
                        matching_keys.append(key)

        return matching_keys

    def search_in_values(self, query: str, case_sensitive: bool = True) -> List[tuple]:
        """
        Search for text in string values.

        Args:
            query: Text to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            List of tuples (key, value) containing the query

        Example:
            >>> fm.search_in_values("localhost")  # Find all string values containing "localhost"
            >>> fm.search_in_values("API", case_sensitive=False)  # Case insensitive search
        """
        results = []

        def visitor_func(val, key_path):
            if isinstance(val, str):
                search_text = val if case_sensitive else val.lower()
                search_query = query if case_sensitive else query.lower()
                if search_query in search_text:
                    results.append((key_path, val))

        self.load_if_not_loaded()
        traverse_data_structure(self.document, "", visitor_func)
        return results
