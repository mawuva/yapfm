# LazySectionsMixin

Provides lazy loading functionality for entire sections to optimize memory usage and performance.

## Features

- **Lazy Loading**: Sections are loaded only when accessed
- **Memory Efficient**: Prevents loading large sections unnecessarily
- **Cache Integration**: Works with the unified cache system
- **Automatic Invalidation**: Cache invalidation when sections are modified
- **Statistics Tracking**: Monitor lazy loading performance

## Methods

### get_section

```python
def get_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    default: Any = None,
    lazy: bool = True
) -> Any
```

Get an entire section from the file with lazy loading.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `key_name` (Optional[str]): The name of the section
- `default` (Any): The default value if the section is not found
- `lazy` (bool): Whether to use lazy loading. Default: True

**Returns:**
- `Any`: The section data or default

**Example:**
```python
# Lazy loading (default behavior)
db_section = fm.get_section("database", lazy=True)

# Force immediate loading
db_section = fm.get_section("database", lazy=False)
```

### set_section

```python
def set_section(
    self,
    data: Dict[str, Any],
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    overwrite: bool = True,
    update_lazy_cache: bool = True
) -> None
```

Set an entire section in the file with lazy cache invalidation.

**Parameters:**
- `data` (Dict[str, Any]): The section data to set
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `key_name` (Optional[str]): The name of the section
- `overwrite` (bool): Whether to overwrite the existing section. Default: True
- `update_lazy_cache` (bool): Whether to invalidate lazy cache. Default: True

**Example:**
```python
fm.set_section({
    "host": "localhost",
    "port": 5432,
    "ssl": True
}, dot_key="database")
```

### delete_section

```python
def delete_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None
) -> bool
```

Delete an entire section from the file with lazy cache invalidation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `key_name` (Optional[str]): The name of the section

**Returns:**
- `bool`: True if the section was deleted, False if it didn't exist

**Example:**
```python
deleted = fm.delete_section(dot_key="database")
```

### clear_lazy_cache

```python
def clear_lazy_cache(self) -> None
```

Clear all lazy-loaded sections from cache.

**Example:**
```python
fm.clear_lazy_cache()  # Clears all lazy-loaded sections
```

### get_lazy_stats

```python
def get_lazy_stats(self) -> Dict[str, Any]
```

Get statistics about lazy loading.

**Returns:**
- `Dict[str, Any]`: Statistics including total sections, loaded sections, etc.

**Example:**
```python
stats = fm.get_lazy_stats()
print(f"Total sections: {stats['total_sections']}")
print(f"Loaded sections: {stats['loaded_sections']}")
```
