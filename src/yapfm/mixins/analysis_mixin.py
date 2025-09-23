"""
Analysis Mixin

This module provides analysis functionality for the FileManager.
The AnalysisMixin contains operations for analyzing data structure, types, and statistics.
"""

# mypy: ignore-errors

from collections import Counter
from typing import Any, Dict, List

from yapfm.helpers import traverse_data_structure


class AnalysisMixin:
    """
    Mixin for analysis operations.
    """

    def get_all_keys(self, flat: bool = True) -> List[str]:
        """
        Get all keys in the file.

        Args:
            flat: If True, returns in dot notation (database.host)
                If False, returns hierarchical structure

        Returns:
            List of keys

        Example:
            >>> fm.get_all_keys()  # ['database.host', 'database.port', 'api.version']
            >>> fm.get_all_keys(flat=False)  # ['database', 'api']
        """
        keys = []

        def collect_keys(value, path):
            if flat:
                keys.append(path)
            elif not isinstance(value, (dict, list)):
                keys.append(path)

        self.load_if_not_loaded()
        traverse_data_structure(self.document, "", collect_keys)
        return keys

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the content.

        Returns:
            Dictionary with detailed statistics

        Example:
            >>> stats = fm.get_stats()
            >>> print(f"Total keys: {stats['total_keys']}")
            >>> print(f"Max depth: {stats['max_depth']}")
        """
        stats = {
            "total_keys": 0,
            "max_depth": 0,
            "type_counts": {},
            "sections": 0,
            "arrays": 0,
            "primitives": 0,
        }

        def analyze_item(value, path):
            stats["total_keys"] += 1
            value_type = type(value).__name__
            stats["type_counts"][value_type] = (
                stats["type_counts"].get(value_type, 0) + 1
            )

            # Calculate depth from path
            depth = path.count(".") + 1 if path else 0
            stats["max_depth"] = max(stats["max_depth"], depth)

            if isinstance(value, dict):
                stats["sections"] += 1
            elif isinstance(value, list):
                stats["arrays"] += 1
            else:
                stats["primitives"] += 1

        self.load_if_not_loaded()
        traverse_data_structure(self.document, "", analyze_item)

        # Add file-specific stats
        stats.update(
            {
                "file_size": self.path.stat().st_size if self.exists() else 0,
                "file_format": self.path.suffix,
                "is_loaded": self.is_loaded(),
                "is_dirty": self.is_dirty(),
                "cache_enabled": self.enable_cache,
                "cache_stats": self.get_cache_stats() if self.enable_cache else None,
            }
        )

        return stats

    def get_type_distribution(self) -> Dict[str, int]:
        """
        Get distribution of data types in the file.

        Returns:
            Dictionary with type counts

        Example:
            >>> types = fm.get_type_distribution()
            >>> print(f"Strings: {types['str']}, Numbers: {types['int'] + types['float']}")
        """
        type_counts = Counter()

        def count_type(value, path):
            type_counts[type(value).__name__] += 1

        self.load_if_not_loaded()
        traverse_data_structure(self.document, "", count_type)
        return dict(type_counts)

    def get_size_info(self) -> Dict[str, Any]:
        """
        Get size information about the file and data.

        Returns:
            Dictionary with size information

        Example:
            >>> size_info = fm.get_size_info()
            >>> print(f"File size: {size_info['file_size_bytes']} bytes")
            >>> print(f"Memory usage: {size_info['memory_usage_bytes']} bytes")
        """
        import sys

        self.load_if_not_loaded()

        # File size
        file_size = self.path.stat().st_size if self.exists() else 0

        # Memory usage estimation
        memory_usage = sys.getsizeof(self.document)

        # Key count and average length
        all_keys = self.get_all_keys(flat=True)
        key_count = len(all_keys)
        avg_key_length = (
            sum(len(key) for key in all_keys) / key_count if key_count > 0 else 0
        )

        return {
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "memory_usage_bytes": memory_usage,
            "memory_usage_mb": memory_usage / (1024 * 1024),
            "key_count": key_count,
            "average_key_length": avg_key_length,
            "compression_ratio": file_size / memory_usage if memory_usage > 0 else 0,
        }

    def find_duplicates(self) -> Dict[Any, List[str]]:
        """
        Find duplicate values and their keys.

        Returns:
            Dictionary mapping values to lists of keys that contain them

        Example:
            >>> duplicates = fm.find_duplicates()
            >>> for value, keys in duplicates.items():
            ...     if len(keys) > 1:
            ...         print(f"Value '{value}' found in: {keys}")
        """
        value_to_keys = {}

        def track_value(value, path):
            # Only track hashable values
            try:
                if value not in value_to_keys:
                    value_to_keys[value] = []
                value_to_keys[value].append(path)
            except TypeError:
                # Skip unhashable types
                pass

        self.load_if_not_loaded()
        traverse_data_structure(self.document, "", track_value)

        # Return only values that appear more than once
        return {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}
