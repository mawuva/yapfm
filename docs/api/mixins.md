# Mixins

## FileOperationsMixin

Provides basic file operations.

### Methods

#### exists

```python
def exists(self) -> bool
```

Check if the file exists.

**Returns:**
- `bool`: True if the file exists, False otherwise

**Example:**
```python
if fm.exists():
    print("File exists")
```

#### is_dirty

```python
def is_dirty(self) -> bool
```

Check if the file is dirty (has unsaved changes).

**Returns:**
- `bool`: True if the file has unsaved changes, False otherwise

**Example:**
```python
if fm.is_dirty():
    print("File has unsaved changes")
```

#### is_loaded

```python
def is_loaded(self) -> bool
```

Check if the file is loaded in memory.

**Returns:**
- `bool`: True if the file is loaded, False otherwise

**Example:**
```python
if fm.is_loaded():
    print("File is loaded in memory")
```

#### load

```python
def load(self) -> None
```

Load data from the file.

**Raises:**
- `FileNotFoundError`: If the file doesn't exist and auto_create is False
- `ValueError`: If the file format is invalid or corrupted
- `LoadFileError`: If there's an error during the loading process

**Example:**
```python
fm.load()  # Loads the file content into memory
```

#### save

```python
def save(self) -> None
```

Save data to the file.

**Raises:**
- `PermissionError`: If the file cannot be written due to permissions
- `ValueError`: If the data format is invalid for the file type
- `FileWriteError`: If there's an error during the writing process

**Example:**
```python
fm.save()  # Saves the current data to disk
```

#### save_if_dirty

```python
def save_if_dirty(self) -> None
```

Save the file only if it has been modified.

**Example:**
```python
fm.save_if_dirty()  # Only saves if there are unsaved changes
```

#### reload

```python
def reload(self) -> None
```

Reload data from the file, discarding any unsaved changes.

**Example:**
```python
fm.reload()  # Reloads from disk, discards unsaved changes
```

#### mark_as_dirty

```python
def mark_as_dirty(self) -> None
```

Mark the file as dirty (has unsaved changes).

**Example:**
```python
fm.mark_as_dirty()  # Mark as having unsaved changes
```

#### mark_as_clean

```python
def mark_as_clean(self) -> None
```

Mark the file as clean (no unsaved changes).

**Example:**
```python
fm.mark_as_clean()  # Mark as clean
```

#### mark_as_loaded

```python
def mark_as_loaded(self) -> None
```

Mark the file as loaded in memory.

**Example:**
```python
fm.mark_as_loaded()  # Mark as loaded
```

#### unload

```python
def unload(self) -> None
```

Unload the file from memory.

**Example:**
```python
fm.unload()  # Free memory
```

#### create_empty_file

```python
def create_empty_file(self) -> None
```

Create an empty file.

**Example:**
```python
fm.create_empty_file()  # Creates empty file
```

#### load_if_not_loaded

```python
def load_if_not_loaded(self) -> None
```

Load the file if it is not loaded.

**Example:**
```python
fm.load_if_not_loaded()  # Load only if not already loaded
```

## KeyOperationsMixin

Provides key-based data access with dot notation.

### Methods

#### set_key

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

#### get_key

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

#### has_key

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

#### delete_key

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

## SectionOperationsMixin

Provides section-based data management.

### Methods

#### set_section

```python
def set_section(
    self,
    section_data: Dict[str, Any],
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None,
    overwrite: bool = True
) -> None
```

Set an entire section in the file.

**Parameters:**
- `section_data` (Dict[str, Any]): The section data to set
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section
- `overwrite` (bool): Whether to overwrite the existing section. Default: True

**Example:**
```python
# Using dot notation
fm.set_section({
    "host": "localhost",
    "port": 5432,
    "ssl": True
}, dot_key="database")

# Using path and section name
fm.set_section({
    "version": "v1",
    "timeout": 30
}, path=["api"], section_name="config")
```

#### get_section

```python
def get_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None,
    default: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]
```

Get an entire section from the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section
- `default` (Optional[Dict[str, Any]]): The default value if the section is not found

**Returns:**
- `Optional[Dict[str, Any]]`: The section data or default

**Example:**
```python
# Using dot notation
db_config = fm.get_section(dot_key="database")

# Using path and section name
api_config = fm.get_section(path=["api"], section_name="config")
```

#### has_section

```python
def has_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None
) -> bool
```

Check if a section exists in the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section

**Returns:**
- `bool`: True if the section exists, False otherwise

**Example:**
```python
# Using dot notation
if fm.has_section(dot_key="database"):
    print("Database section exists")

# Using path and section name
if fm.has_section(path=["api"], section_name="config"):
    print("API config section exists")
```

#### delete_section

```python
def delete_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None
) -> bool
```

Delete an entire section from the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section

**Returns:**
- `bool`: True if the section was deleted, False if it didn't exist

**Example:**
```python
# Using dot notation
deleted = fm.delete_section(dot_key="database")

# Using path and section name
deleted = fm.delete_section(path=["api"], section_name="config")
```

## ContextMixin

Provides context manager functionality.

### Methods

#### __enter__

```python
def __enter__(self) -> Self
```

Enter the context manager and load the file.

**Returns:**
- `Self`: The file manager instance

**Example:**
```python
with YAPFileManager("config.json") as fm:
    # File is automatically loaded
    fm.set_key("value", dot_key="key")
```

#### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb) -> None
```

Exit the context manager and save if dirty.

**Parameters:**
- `exc_type`: Exception type
- `exc_val`: Exception value
- `exc_tb`: Exception traceback

**Example:**
```python
with YAPFileManager("config.json") as fm:
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting context
```

#### lazy_save

```python
@contextmanager
def lazy_save(self, save_on_exit: bool = True) -> Iterator[Self]
```

Context manager for lazy saving.

**Parameters:**
- `save_on_exit` (bool): Whether to save when exiting the context. Default: True

**Returns:**
- `Iterator[Self]`: The file manager instance

**Example:**
```python
with fm.lazy_save():
    fm.set_key("value1", dot_key="key1")
    fm.set_key("value2", dot_key="key2")
    # Save happens here when exiting lazy_save context
```

#### auto_save

```python
@contextmanager
def auto_save(self, save_on_exit: bool = True) -> Iterator[Self]
```

Context manager for automatic saving.

**Parameters:**
- `save_on_exit` (bool): Whether to save when exiting the context. Default: True

**Returns:**
- `Iterator[Self]`: The file manager instance

**Example:**
```python
with fm.auto_save():
    fm.set_key("value", dot_key="key")
    # Save happens here when exiting auto_save context
```
