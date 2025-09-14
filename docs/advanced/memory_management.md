# Memory Management

## Memory-Efficient File Manager

```python
from yapfm import YAPFileManager
from typing import Any, Dict, Optional
import weakref
import gc

class MemoryEfficientFileManager:
    """File manager with memory management features."""
    
    def __init__(self, path: str, max_memory_mb: int = 100):
        self.path = path
        self.max_memory_mb = max_memory_mb
        self._fm = YAPFileManager(path, auto_create=True)
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_refs = weakref.WeakValueDictionary()
    
    def _check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb < self.max_memory_mb
    
    def _cleanup_memory(self) -> None:
        """Clean up memory by clearing cache and running garbage collection."""
        self._cache = None
        self._cache_refs.clear()
        gc.collect()
    
    def get_data(self) -> Dict[str, Any]:
        """Get data with memory management."""
        if not self._check_memory_usage():
            self._cleanup_memory()
        
        if self._cache is None:
            with self._fm:
                self._cache = self._fm.data.copy()
        
        return self._cache.copy()
    
    def get_key(self, dot_key: str, default: Any = None) -> Any:
        """Get key with memory management."""
        data = self.get_data()
        
        # Navigate through nested keys
        keys = dot_key.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_key(self, value: Any, dot_key: str) -> None:
        """Set key with memory management."""
        with self._fm:
            self._fm.set_key(value, dot_key=dot_key)
        
        # Invalidate cache
        self._cache = None
    
    def optimize_memory(self) -> None:
        """Optimize memory usage."""
        self._cleanup_memory()
        
        # Force garbage collection
        gc.collect()
        
        print(f"Memory optimized. Current usage: {self._get_memory_usage():.2f} MB")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

# Usage
memory_fm = MemoryEfficientFileManager("memory_config.json", max_memory_mb=50)

# Use the file manager
data = memory_fm.get_data()
memory_fm.set_key("value", "key")

# Optimize memory when needed
memory_fm.optimize_memory()
```
