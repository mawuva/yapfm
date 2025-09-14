# Context Management

## Basic Context Manager

```python
from yapfm import YAPFileManager

# Automatic loading and saving
with YAPFileManager("config.json", auto_create=True) as fm:
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting the context
```

## Lazy Save Context

```python
# Save only when exiting the lazy_save context
with YAPFileManager("config.json") as fm:
    with fm.lazy_save():
        fm.set_key("value1", dot_key="key1")
        fm.set_key("value2", dot_key="key2")
        fm.set_key("value3", dot_key="key3")
        # Save happens here when exiting lazy_save context
```

## Auto Save Context

```python
# Auto-save context (similar to lazy_save)
with YAPFileManager("config.json") as fm:
    with fm.auto_save():
        fm.set_key("value", dot_key="key")
        # Save happens here when exiting auto_save context
```

## Context Manager with Error Handling

```python
try:
    with YAPFileManager("config.json", auto_create=True) as fm:
        fm.set_key("value", dot_key="key")
        # Some operation that might fail
        risky_operation()
except Exception as e:
    print(f"Error occurred: {e}")
    # File is still saved if no exception occurred
```
