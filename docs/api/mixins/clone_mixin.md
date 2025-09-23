# CloneMixin

Provides cloning and copying functionality for the file manager. The CloneMixin contains operations for cloning, copying, and merging data.

## Methods

### clone

```python
def clone(self) -> "YAPFileManager"
```

Create a complete copy of the manager.

**Returns:**
- `YAPFileManager`: New YAPFileManager with the same data

**Example:**
```python
original = YAPFileManager("config.json")
copy = original.clone()
print(copy.path != original.path)  # Different temporary file
```

### copy_to

```python
def copy_to(
    self, 
    destination: Union[str, Path], 
    strategy: Optional[BaseFileStrategy] = None
) -> "YAPFileManager"
```

Copy content to another file.

**Parameters:**
- `destination` (Union[str, Path]): Destination file path
- `strategy` (Optional[BaseFileStrategy]): Optional strategy for the destination file

**Returns:**
- `YAPFileManager`: New YAPFileManager for the destination file

**Example:**
```python
# Copy to JSON
fm.copy_to("backup.json")

# Copy to TOML with auto-detection
fm.copy_to("config.toml")
```

### merge_from

```python
def merge_from(
    self, 
    source: Union[str, Path, "YAPFileManager"], 
    strategy: str = "deep"
) -> None
```

Merge from another file or manager.

**Parameters:**
- `source` (Union[str, Path, "YAPFileManager"]): Source file or YAPFileManager
- `strategy` (str): Merge strategy ("deep", "shallow", "replace")

**Example:**
```python
# Deep merge
fm.merge_from("override.json", strategy="deep")

# Replace merge
fm.merge_from(other_manager, strategy="replace")
```
