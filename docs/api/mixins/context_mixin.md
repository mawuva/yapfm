# ContextMixin

Provides context manager functionality.

## Methods

### __enter__

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

### __exit__

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

### lazy_save

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

### auto_save

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
