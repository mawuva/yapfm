# KeyOperationsMixin

Provides key-based data access with dot notation.

## Methods

### set_key

```python
def set_key(
    self,
    value: Any,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    overwrite: bool = True
) -> None
```

Set a value in the file using dot notation.

**Parameters:**
- `value` (Any): The value to set
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key
- `overwrite` (bool): Whether to overwrite the existing value. Default: True

**Example:**
```python
# Using dot notation
fm.set_key("localhost", dot_key="database.host")

# Using path and key name
fm.set_key(5432, path=["database"], key_name="port")

# Only set if key doesn't exist
fm.set_key("default", dot_key="database.host", overwrite=False)
```

### get_key

```python
def get_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    default: Any = None
) -> Any
```

Get a value from the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key
- `default` (Any): The default value if the key is not found

**Returns:**
- `Any`: The value at the specified path or default

**Example:**
```python
# Using dot notation
host = fm.get_key(dot_key="database.host", default="localhost")

# Using path and key name
port = fm.get_key(path=["database"], key_name="port", default=5432)
```

### has_key

```python
def has_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None
) -> bool
```

Check if a key exists in the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key

**Returns:**
- `bool`: True if the key exists, False otherwise

**Example:**
```python
# Using dot notation
if fm.has_key(dot_key="database.host"):
    print("Database host exists")

# Using path and key name
if fm.has_key(path=["database"], key_name="port"):
    print("Database port exists")
```

### delete_key

```python
def delete_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None
) -> bool
```

Delete a key from the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key

**Returns:**
- `bool`: True if the key was deleted, False if it didn't exist

**Example:**
```python
# Using dot notation
deleted = fm.delete_key(dot_key="database.host")

# Using path and key name
deleted = fm.delete_key(path=["database"], key_name="port")
```
