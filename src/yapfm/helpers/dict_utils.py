"""
Dict utilities.
"""

from typing import Any, Callable, Dict, List, Optional, Union


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
