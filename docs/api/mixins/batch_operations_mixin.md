# Batch Operations

YAPFileManager includes built-in batch operations for efficient handling of multiple keys at once.

## Methods

### set_multiple

```python
def set_multiple(self, items: Dict[str, Any], overwrite: bool = True) -> None
```

Set multiple key-value pairs efficiently.

**Parameters:**
- `items` (Dict[str, Any]): Dictionary of key-value pairs to set
- `overwrite` (bool): Whether to overwrite existing values

**Raises:**
- `ValueError`: If any key fails to be set

**Example:**
```python
fm.set_multiple({
    "database.host": "localhost",
    "database.port": 5432,
    "logging.level": "INFO"
})
```

### get_multiple

```python
def get_multiple(
    self,
    keys: List[str],
    default: Any = None,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

Get multiple values efficiently.

**Parameters:**
- `keys` (List[str]): List of keys to get
- `default` (Any): Default value for missing keys
- `defaults` (Optional[Dict[str, Any]]): Optional dictionary with specific default values per key

**Returns:**
- `Dict[str, Any]`: Dictionary with key-value pairs

**Example:**
```python
# Get multiple values with same default
values = fm.get_multiple(["database.host", "database.port"])

# Get multiple values with specific defaults
values = fm.get_multiple(
    ["database.host", "database.port"],
    defaults={"database.host": "localhost", "database.port": 5432}
)
```

### delete_multiple

```python
def delete_multiple(self, keys: List[str]) -> int
```

Delete multiple keys efficiently.

**Parameters:**
- `keys` (List[str]): List of keys to delete

**Returns:**
- `int`: Number of keys deleted

**Raises:**
- `ValueError`: If keys is not a list or contains invalid keys

**Example:**
```python
deleted_count = fm.delete_multiple(["database.host", "database.port"])
print(f"Deleted {deleted_count} keys")
```
