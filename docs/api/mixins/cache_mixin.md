# CacheMixin

Provides intelligent caching functionality for individual keys with TTL, LRU eviction, and statistics tracking.

## Features

- **Smart Caching**: Automatic caching of individual key values
- **TTL Support**: Time-to-live for cached entries
- **LRU Eviction**: Least Recently Used eviction when cache is full
- **Memory Management**: Size-based eviction to prevent memory issues
- **Statistics Tracking**: Hit/miss ratios and performance metrics
- **Pattern Invalidation**: Invalidate cache entries using patterns
- **Thread Safety**: Safe for use in multi-threaded environments

## Methods

### get_value

```python
def get_value(
    self,
    key: str = None,
    default: Any = None
) -> Any
```

Get a value from the file using key with intelligent caching.

**Parameters:**
- `key` (str): The key
- `default` (Any): The default value if the key is not found

**Returns:**
- `Any`: The value at the specified key or default

**Example:**
```python
# Using with caching
host = fm.get_value("database.host", default="localhost")

# First call loads from file and caches
# Subsequent calls return from cache (much faster)
```

### set_value

```python
def set_value(
    self,
    key: str,
    value: Any,
    overwrite: bool = True
) -> None
```

Set a value in the file using key.

The cache will be automatically updated on the next get_value() call.

**Parameters:**
- `key` (str): The key to set
- `value` (Any): The value to set
- `overwrite` (bool): Whether to overwrite existing values

**Example:**
```python
fm.set_value("database.host", "localhost")
fm.set_value("database.port", 5432, overwrite=False)
```

### clear_cache

```python
def clear_cache(self) -> None
```

Clear all cached keys.

**Example:**
```python
fm.clear_cache()  # Clears all cached values
```

### invalidate_cache

```python
def invalidate_cache(self, pattern: Optional[str] = None) -> int
```

Invalidate cache entries, optionally using a pattern.

**Parameters:**
- `pattern` (Optional[str]): Pattern to match keys (supports wildcards). If None, invalidates all

**Returns:**
- `int`: Number of entries invalidated

**Example:**
```python
# Invalidate all cache entries
count = fm.invalidate_cache()

# Invalidate only database-related entries
count = fm.invalidate_cache("key:database.*")
```
