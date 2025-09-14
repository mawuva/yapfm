# Advanced Context Management

## Nested Context Managers

```python
from yapfm import YAPFileManager
from contextlib import contextmanager
from typing import Iterator, Dict, Any

class NestedContextManager:
    """Advanced context manager with nested operations."""
    
    def __init__(self, path: str):
        self.path = path
        self._fm = YAPFileManager(path, auto_create=True)
        self._context_level = 0
    
    @contextmanager
    def transaction(self) -> Iterator[Dict[str, Any]]:
        """Transaction context with rollback capability."""
        self._context_level += 1
        original_data = None
        
        try:
            with self._fm:
                # Save original state
                original_data = self._fm.data.copy()
                yield self._fm.data
        except Exception as e:
            # Rollback on error
            if original_data is not None:
                with self._fm:
                    self._fm.data = original_data
            raise e
        finally:
            self._context_level -= 1
    
    @contextmanager
    def batch_operations(self) -> Iterator[Dict[str, Any]]:
        """Batch operations context."""
        with self._fm:
            with self._fm.lazy_save():
                yield self._fm.data
    
    @contextmanager
    def read_only(self) -> Iterator[Dict[str, Any]]:
        """Read-only context that prevents modifications."""
        with self._fm:
            # Create a read-only view
            class ReadOnlyView:
                def __init__(self, data):
                    self._data = data
                
                def __getitem__(self, key):
                    return self._data[key]
                
                def __setitem__(self, key, value):
                    raise RuntimeError("Modifications not allowed in read-only context")
                
                def get(self, key, default=None):
                    return self._data.get(key, default)
                
                def keys(self):
                    return self._data.keys()
                
                def values(self):
                    return self._data.values()
                
                def items(self):
                    return self._data.items()
            
            yield ReadOnlyView(self._fm.data)

# Usage
nested_fm = NestedContextManager("nested_config.json")

# Transaction context
try:
    with nested_fm.transaction() as data:
        data["key1"] = "value1"
        data["key2"] = "value2"
        # If an exception occurs here, changes are rolled back
except Exception as e:
    print(f"Transaction failed: {e}")

# Batch operations
with nested_fm.batch_operations() as data:
    data["key3"] = "value3"
    data["key4"] = "value4"
    # All changes are saved when exiting the context

# Read-only context
with nested_fm.read_only() as data:
    value = data["key1"]  # OK
    # data["key5"] = "value5"  # This would raise an error
```
