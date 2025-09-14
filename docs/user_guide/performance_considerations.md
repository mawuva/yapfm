# Performance Considerations

## Lazy Loading

```python
# File is only loaded when first accessed
fm = YAPFileManager("config.json")
# File is not loaded yet

# Access data (triggers loading)
data = fm.data  # File is loaded here

# Or explicitly load
fm.load()  # File is loaded here
```

## Memory Management

```python
# Unload file from memory when done
fm = YAPFileManager("config.json")
fm.load()
# ... use the file ...
fm.unload()  # Free memory

# Or use context manager for automatic cleanup
with YAPFileManager("config.json") as fm:
    # ... use the file ...
    # File is automatically unloaded when exiting context
```

## Batch Operations

```python
# Batch multiple operations to reduce I/O
with YAPFileManager("config.json") as fm:
    with fm.lazy_save():
        # Multiple operations, single save
        fm.set_key("value1", dot_key="key1")
        fm.set_key("value2", dot_key="key2")
        fm.set_key("value3", dot_key="key3")
        # Single save at the end
```
