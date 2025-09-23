"""
Dict utilities.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from .utils import join_dot_key


def navigate_dict_like(
    document: Union[Dict[str, Any], List[Any]],
    path: List[str],
    create: bool = False,
    create_dict_func: Optional[Callable[[], Any]] = None,
) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Generic function to navigate through dict-like structures (JSON, YAML, etc.).
    Descend into the structure, optionally creating intermediate containers.

    Args:
        document (Union[Dict[str, Any], List[Any]]): The document to navigate.
        path (List[str]): The path to the key.
        create (bool): Whether to create intermediate containers if they don't exist.
        create_dict_func (Optional[Callable[[], Any]]): Function to create new dict-like objects.
                                                    Defaults to creating empty dicts.

    Returns:
        Optional[Union[Dict[str, Any], List[Any]]]: The current node in the structure.
        None if the path doesn't exist and create is False.
    """
    if create_dict_func is None:

        def create_dict_func() -> Dict[str, Any]:
            return {}

    current = document

    for part in path:
        # Case 1: current node is a dictionary
        if isinstance(current, dict):
            if part not in current:
                if create:
                    current[part] = create_dict_func()
                else:
                    return None
            current = current[part]

        # Case 2: current node is a list
        elif isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                return None

            while len(current) <= idx:
                if create:
                    current.append(create_dict_func())
                else:
                    return None

            current = current[idx]

        # Case 3: current node is neither dict nor list
        else:
            return None

    return current


def traverse_data_structure(
    data: Any,
    current_path: str = "",
    visitor_func: Optional[Callable[[Any, str], None]] = None,
    include_containers: bool = True,
) -> None:
    """
    Generic function to traverse data structures with visitor pattern.

    Args:
        data: Data structure to traverse (dict, list, or any)
        current_path: Current path in the structure (dot-separated)
        visitor_func: Function called for each item (value, path) -> None
        include_containers: Whether to call visitor_func on dict/list containers

    Example:
        >>> def collect_keys(value, path):
        ...     if not isinstance(value, (dict, list)):
        ...         keys.append(path)
        >>> traverse_data_structure(data, "", collect_keys)
    """
    if visitor_func and include_containers:
        visitor_func(data, current_path)

    if isinstance(data, dict):
        for key, value in data.items():
            if current_path:
                key_path = join_dot_key([current_path], key)
            else:
                key_path = key
            if visitor_func:
                visitor_func(value, key_path)
            if isinstance(value, (dict, list)):
                traverse_data_structure(
                    value, key_path, visitor_func, include_containers
                )
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if current_path:
                key_path = join_dot_key([current_path], str(i))
            else:
                key_path = str(i)
            if visitor_func:
                visitor_func(value, key_path)
            if isinstance(value, (dict, list)):
                traverse_data_structure(
                    value, key_path, visitor_func, include_containers
                )


def transform_data_in_place(
    data: Any,
    transform_func: Callable[[Any], Any],
    transform_type: str = "value",
    deep: bool = True,
) -> None:
    """
    Generic function to transform data in place (values or keys).

    Args:
        data: Data structure to transform (dict, list, or any)
        transform_func: Function to transform values or keys
        transform_type: Either "value" or "key"
        deep: Whether to transform recursively in nested structures

    Example:
        >>> # Transform values
        >>> transform_data_in_place(data, lambda x: x.upper() if isinstance(x, str) else x, "value")
        >>> # Transform keys
        >>> transform_data_in_place(data, str.upper, "key")
    """
    if transform_type == "value":
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)) and deep:
                    transform_data_in_place(value, transform_func, transform_type, deep)
                else:
                    data[key] = transform_func(value)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                if isinstance(value, (dict, list)) and deep:
                    transform_data_in_place(value, transform_func, transform_type, deep)
                else:
                    data[i] = transform_func(value)

    elif transform_type == "key":
        if isinstance(data, dict):
            # Create new dict with transformed keys
            new_data = {}
            for key, value in data.items():
                new_key = transform_func(key)
                if isinstance(value, (dict, list)) and deep:
                    transform_data_in_place(value, transform_func, transform_type, deep)
                new_data[new_key] = value
            # Replace the original dict
            data.clear()
            data.update(new_data)
        elif isinstance(data, list):
            for value in data:
                if isinstance(value, (dict, list)) and deep:
                    transform_data_in_place(value, transform_func, transform_type, deep)


def deep_merge(base: dict, new: dict, overwrite: bool = True) -> dict:
    """
    Deep merge two dictionaries (generic, format-agnostic).

    Args:
        base (dict): Base dictionary to merge into.
        new (dict): New dictionary to merge from.
        overwrite (bool): Whether to overwrite existing keys.

    Returns:
        dict: Merged dictionary.
    """
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value, overwrite=overwrite)
        else:
            if overwrite or key not in base:
                base[key] = value
    return base
