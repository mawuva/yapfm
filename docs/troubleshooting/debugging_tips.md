# Debugging Tips

## Enable Debug Logging

```python
import logging

# Set up debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("yapfm")

# Use proxy with logging
from yapfm import FileManagerProxy

fm = YAPFileManager("config.json")
proxy = FileManagerProxy(fm, enable_logging=True, logger=logger)

# All operations will be logged
with proxy:
    proxy.set_key("value", dot_key="key")
```

## Use Debug Mode

```python
# Enable debug mode for more verbose output
import os
os.environ["YAPFM_DEBUG"] = "1"

# Or set debug flag
fm = YAPFileManager("config.json", debug=True)
```

## Inspect File State

```python
def debug_file_state(fm):
    print(f"File exists: {fm.exists()}")
    print(f"File loaded: {fm.is_loaded()}")
    print(f"File dirty: {fm.is_dirty()}")
    print(f"File path: {fm.path}")
    print(f"File size: {fm.path.stat().st_size if fm.exists() else 'N/A'}")
    
    if fm.is_loaded():
        print(f"Data keys: {list(fm.data.keys())}")
        print(f"Data type: {type(fm.data)}")
```

## Trace Operations

```python
def trace_operations(fm):
    original_set_key = fm.set_key
    original_get_key = fm.get_key
    
    def traced_set_key(value, dot_key=None, **kwargs):
        print(f"SET: {dot_key} = {value}")
        return original_set_key(value, dot_key=dot_key, **kwargs)
    
    def traced_get_key(dot_key=None, **kwargs):
        result = original_get_key(dot_key=dot_key, **kwargs)
        print(f"GET: {dot_key} = {result}")
        return result
    
    fm.set_key = traced_set_key
    fm.get_key = traced_get_key
```
