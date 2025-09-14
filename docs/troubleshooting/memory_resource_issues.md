# Memory and Resource Issues

## Memory Leaks

**Problem**: Memory usage keeps increasing.

**Solutions**:
```python
# 1. Use context managers
with YAPFileManager("config.json") as fm:
    # Use file manager
    pass
# Automatically cleaned up

# 2. Explicitly unload
fm.unload()  # Free memory

# 3. Use weak references
import weakref

class MemoryEfficientManager:
    def __init__(self, path):
        self.fm = YAPFileManager(path)
        self._cache = weakref.WeakValueDictionary()
    
    def get_data(self):
        if 'data' not in self._cache:
            with self.fm:
                self._cache['data'] = self.fm.data.copy()
        return self._cache['data']
```

## Resource Exhaustion

**Problem**: Too many file handles or other resources.

**Solutions**:
```python
# 1. Use context managers
with YAPFileManager("config.json") as fm:
    # File is automatically closed
    pass

# 2. Limit concurrent operations
import threading

class ResourceLimitedManager:
    def __init__(self, path, max_concurrent=5):
        self.fm = YAPFileManager(path)
        self.semaphore = threading.Semaphore(max_concurrent)
    
    def operation(self):
        with self.semaphore:
            with self.fm:
                # Perform operation
                pass
```
