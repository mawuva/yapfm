# FileOperationsMixin

Provides basic file operations.

## Methods

### exists

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

### is_dirty

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

### is_loaded

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

### load

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

### save

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

### save_if_dirty

```python
def save_if_dirty(self) -> None
```

Save the file only if it has been modified.

**Example:**
```python
fm.save_if_dirty()  # Only saves if there are unsaved changes
```

### reload

```python
def reload(self) -> None
```

Reload data from the file, discarding any unsaved changes.

**Example:**
```python
fm.reload()  # Reloads from disk, discards unsaved changes
```

### mark_as_dirty

```python
def mark_as_dirty(self) -> None
```

Mark the file as dirty (has unsaved changes).

**Example:**
```python
fm.mark_as_dirty()  # Mark as having unsaved changes
```

### mark_as_clean

```python
def mark_as_clean(self) -> None
```

Mark the file as clean (no unsaved changes).

**Example:**
```python
fm.mark_as_clean()  # Mark as clean
```

### mark_as_loaded

```python
def mark_as_loaded(self) -> None
```

Mark the file as loaded in memory.

**Example:**
```python
fm.mark_as_loaded()  # Mark as loaded
```

### unload

```python
def unload(self) -> None
```

Unload the file from memory.

**Example:**
```python
fm.unload()  # Free memory
```

### create_empty_file

```python
def create_empty_file(self) -> None
```

Create an empty file.

**Example:**
```python
fm.create_empty_file()  # Creates empty file
```

### load_if_not_loaded

```python
def load_if_not_loaded(self) -> None
```

Load the file if it is not loaded.

**Example:**
```python
fm.load_if_not_loaded()  # Load only if not already loaded
```
