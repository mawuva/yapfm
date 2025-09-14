# Best Practices

## 1. Use Context Managers

```python
# ✅ Good: Automatic cleanup
with YAPFileManager("config.json", auto_create=True) as fm:
    fm.set_key("value", dot_key="key")

# ❌ Avoid: Manual cleanup
fm = YAPFileManager("config.json")
fm.load()
fm.set_key("value", dot_key="key")
fm.save()
```

## 2. Set Defaults

```python
# ✅ Good: Always provide defaults
host = fm.get_key(dot_key="database.host", default="localhost")

# ❌ Avoid: No defaults
host = fm.get_key(dot_key="database.host")  # Could be None
```

## 3. Validate Configuration

```python
# ✅ Good: Validate before use
def load_config():
    with YAPFileManager("config.json", auto_create=True) as fm:
        # Set required defaults
        if not fm.has_key(dot_key="database.host"):
            fm.set_key("localhost", dot_key="database.host")
        
        return fm.data

# ❌ Avoid: No validation
def load_config():
    with YAPFileManager("config.json") as fm:
        return fm.data  # Could be missing required keys
```

## 4. Handle Errors Gracefully

```python
# ✅ Good: Comprehensive error handling
try:
    with YAPFileManager("config.json") as fm:
        fm.set_key("value", dot_key="key")
except LoadFileError as e:
    logger.error(f"Failed to load config: {e}")
    # Fallback to default config
except FileWriteError as e:
    logger.error(f"Failed to save config: {e}")
    # Handle save failure
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors

# ❌ Avoid: No error handling
with YAPFileManager("config.json") as fm:
    fm.set_key("value", dot_key="key")  # Could fail silently
```

## 5. Use Meaningful Key Names

```python
# ✅ Good: Clear, descriptive keys
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key("myapp", dot_key="database.name")

# ❌ Avoid: Unclear keys
fm.set_key("localhost", dot_key="db.h")
fm.set_key(5432, dot_key="db.p")
fm.set_key("myapp", dot_key="db.n")
```
