"""
Transform Mixin

This module provides transformation functionality for the FileManager.
The TransformMixin contains operations for flattening, unflattening, and transforming data.
"""

# mypy: ignore-errors

from typing import Any, Callable, Dict

from yapfm.helpers import transform_data_in_place, traverse_data_structure


class TransformMixin:
    """
    Mixin for data transformation operations.
    """

    def flatten(self, separator: str = ".") -> Dict[str, Any]:
        """
        Flatten the structure into a single-level dictionary.

        Args:
            separator: Separator to use for nested keys

        Returns:
            Flattened dictionary

        Example:
            >>> flat = fm.flatten()
            >>> print(flat)  # {'database.host': 'localhost', 'database.port': 5432}
        """
        flattened_items = []

        def collect_items(value, path):
            if not isinstance(value, (dict, list)):
                flattened_items.append((path, value))

        self.load_if_not_loaded()
        traverse_data_structure(
            self.document, "", collect_items, include_containers=False
        )

        return dict(flattened_items)

    def unflatten(self, separator: str = ".") -> Dict[str, Any]:
        """
        Reconstruct nested structure from flattened data.

        Args:
            separator: Separator used in flattened keys

        Returns:
            Nested dictionary

        Example:
            >>> flat_data = {'database.host': 'localhost', 'database.port': 5432}
            >>> nested = fm.unflatten_from_dict(flat_data)
        """

        def _unflatten_dict(flat_dict: Dict[str, Any]) -> Dict[str, Any]:
            result = {}
            for key, value in flat_dict.items():
                parts = key.split(separator)
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            return result

        if not self.is_loaded():
            self.load()

        # Get flattened data and reconstruct
        flat_data = self.flatten(separator)
        return _unflatten_dict(flat_data)

    def transform_values(
        self, transformer_func: Callable[[Any], Any], deep: bool = True
    ) -> None:
        """
        Transform all values using a function.

        Args:
            transformer_func: Function to transform values
            deep: If True, transforms recursively in nested structures

        Example:
            >>> fm.transform_values(lambda x: x.upper() if isinstance(x, str) else x)
            >>> fm.transform_values(lambda x: x * 2 if isinstance(x, int) else x)
        """
        self.load_if_not_loaded()
        transform_data_in_place(self.document, transformer_func, "value", deep)
        self.mark_as_dirty()

    def transform_keys(
        self, transformer_func: Callable[[str], str], deep: bool = True
    ) -> None:
        """
        Transform all keys using a function.

        Args:
            transformer_func: Function to transform keys
            deep: If True, transforms recursively in nested structures

        Example:
            >>> fm.transform_keys(str.upper)  # Convert all keys to uppercase
            >>> fm.transform_keys(lambda k: k.replace('_', '-'))  # Replace underscores
        """
        self.load_if_not_loaded()
        transform_data_in_place(self.document, transformer_func, "key", deep)
        self.mark_as_dirty()
