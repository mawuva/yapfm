# File Operations

## Loading Files

```python
from yapfm import YAPFileManager

# Basic loading
fm = YAPFileManager("config.json")
fm.load()

# Auto-create if file doesn't exist
fm = YAPFileManager("config.json", auto_create=True)
fm.load()  # Creates empty file if it doesn't exist

# Check if file exists before loading
if fm.exists():
    fm.load()
else:
    print("File doesn't exist")
```

## Saving Files

```python
# Basic saving
fm.save()

# Save only if file has been modified
fm.save_if_dirty()

# Check if file needs saving
if fm.is_dirty():
    fm.save()
```

## File Status

```python
# Check various file states
print(f"File exists: {fm.exists()}")
print(f"File loaded: {fm.is_loaded()}")
print(f"File dirty: {fm.is_dirty()}")

# Manual state management
fm.mark_as_dirty()    # Mark as modified
fm.mark_as_clean()    # Mark as clean
fm.mark_as_loaded()   # Mark as loaded
```

## File Lifecycle

```python
# Complete file lifecycle
fm = YAPFileManager("config.json")

# 1. Load file
fm.load()

# 2. Make changes
fm.set_key("value", dot_key="key")

# 3. Save changes
fm.save()

# 4. Reload if needed (discards unsaved changes)
fm.reload()

# 5. Unload from memory
fm.unload()
```
