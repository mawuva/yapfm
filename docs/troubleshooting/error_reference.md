# Error Reference

## LoadFileError

**When it occurs**: Error loading a file from disk.

**Common causes**:
- File doesn't exist
- Invalid file format
- Corrupted file
- Permission issues

**Solutions**:
```python
from yapfm.exceptions import LoadFileError

try:
    fm.load()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
    # Handle the error appropriately
```

## FileWriteError

**When it occurs**: Error writing a file to disk.

**Common causes**:
- Permission denied
- Disk full
- Invalid data format
- File locked by another process

**Solutions**:
```python
from yapfm.exceptions import FileWriteError

try:
    fm.save()
except FileWriteError as e:
    print(f"Failed to save file: {e}")
    # Handle the error appropriately
```

## StrategyError

**When it occurs**: Error with file strategy.

**Common causes**:
- Unsupported file format
- Strategy not registered
- Invalid strategy implementation

**Solutions**:
```python
from yapfm.exceptions import StrategyError

try:
    fm = YAPFileManager("file.xyz")
except StrategyError as e:
    print(f"Strategy error: {e}")
    # Use a supported format or register a custom strategy
```
