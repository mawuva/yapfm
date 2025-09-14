# Performance Issues

## Slow File Operations

**Problem**: File operations are taking too long.

**Solutions**:
```python
# 1. Use lazy loading
fm = YAPFileManager("config.json")
# File is only loaded when first accessed
data = fm.data  # Loads here

# 2. Use batch operations
with fm.lazy_save():
    fm.set_key("value1", dot_key="key1")
    fm.set_key("value2", dot_key="key2")
    fm.set_key("value3", dot_key="key3")
    # Single save at the end

# 3. Use caching
from yapfm import FileManagerProxy
import time

class CachedFileManager:
    def __init__(self, path, cache_ttl=300):
        self.fm = YAPFileManager(path)
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.last_load = 0
    
    def get_data(self):
        if time.time() - self.last_load > self.cache_ttl:
            with self.fm:
                self.cache = self.fm.data.copy()
                self.last_load = time.time()
        return self.cache
```

## Memory Usage Issues

**Problem**: High memory usage with large files.

**Solutions**:
```python
# 1. Use streaming for large files
def process_large_file(fm):
    with fm:
        data = fm.data
        # Process data in chunks
        for key, value in data.items():
            # Process each item
            process_item(key, value)

# 2. Unload when not needed
fm.unload()  # Free memory

# 3. Use context managers
with YAPFileManager("config.json") as fm:
    # Use file manager
    pass
# Automatically unloaded when exiting context
```

## Thread Safety Issues

**Problem**: Race conditions in multi-threaded environments.

**Solutions**:
```python
import threading

# 1. Use locks
lock = threading.Lock()

def thread_safe_operation():
    with lock:
        fm.set_key("value", dot_key="key")

# 2. Use thread-safe file manager
class ThreadSafeFileManager:
    def __init__(self, path):
        self.fm = YAPFileManager(path)
        self.lock = threading.RLock()
    
    def set_key(self, value, dot_key):
        with self.lock:
            self.fm.set_key(value, dot_key=dot_key)
    
    def get_key(self, dot_key, default=None):
        with self.lock:
            return self.fm.get_key(dot_key=dot_key, default=default)
```
