# Performance Optimization

## Lazy Loading Strategies

```python
from yapfm import YAPFileManager
from typing import Any, Dict, Optional
import threading
import time

class LazyFileManager:
    """File manager with lazy loading and caching."""
    
    def __init__(self, path: str, cache_ttl: int = 300):
        self.path = path
        self.cache_ttl = cache_ttl
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._lock = threading.RLock()
        self._fm = YAPFileManager(path, auto_create=True)
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache is None or self._cache_timestamp is None:
            return False
        
        return time.time() - self._cache_timestamp < self.cache_ttl
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from file."""
        with self._fm:
            return self._fm.data.copy()
    
    def get_data(self) -> Dict[str, Any]:
        """Get data with lazy loading."""
        with self._lock:
            if not self._is_cache_valid():
                self._cache = self._load_data()
                self._cache_timestamp = time.time()
            
            return self._cache.copy()
    
    def get_key(self, dot_key: str, default: Any = None) -> Any:
        """Get a key with lazy loading."""
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
    
    def invalidate_cache(self) -> None:
        """Invalidate the cache."""
        with self._lock:
            self._cache = None
            self._cache_timestamp = None

# Usage
lazy_fm = LazyFileManager("config.json", cache_ttl=60)  # 1 minute cache

# First access loads from file
data = lazy_fm.get_data()

# Subsequent accesses use cache
key_value = lazy_fm.get_key("database.host")
```

## Memory-Efficient Processing

```python
from yapfm import YAPFileManager
from typing import Iterator, Dict, Any
import json

class StreamingFileManager:
    """File manager for processing large files in chunks."""
    
    def __init__(self, path: str, chunk_size: int = 1000):
        self.path = path
        self.chunk_size = chunk_size
        self._fm = YAPFileManager(path, auto_create=True)
    
    def process_large_data(self, processor: callable) -> None:
        """Process large data in chunks."""
        with self._fm:
            data = self._fm.data
            
            # Process data in chunks
            items = list(data.items())
            for i in range(0, len(items), self.chunk_size):
                chunk = dict(items[i:i + self.chunk_size])
                processor(chunk)
    
    def stream_keys(self) -> Iterator[tuple]:
        """Stream keys and values for memory-efficient processing."""
        with self._fm:
            data = self._fm.data
            
            def _stream_dict(d: Dict[str, Any], prefix: str = "") -> Iterator[tuple]:
                for key, value in d.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    if isinstance(value, dict):
                        yield from _stream_dict(value, full_key)
                    else:
                        yield (full_key, value)
            
            yield from _stream_dict(data)
    
    def batch_update(self, updates: Dict[str, Any]) -> None:
        """Update multiple keys efficiently."""
        with self._fm:
            # Get current data
            current_data = self._fm.data.copy()
            
            # Apply updates
            for key, value in updates.items():
                keys = key.split('.')
                target = current_data
                
                # Navigate to target
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                
                # Set value
                target[keys[-1]] = value
            
            # Save updated data
            self._fm.data = current_data

# Usage
streaming_fm = StreamingFileManager("large_config.json")

# Process large data
def process_chunk(chunk: Dict[str, Any]) -> None:
    print(f"Processing chunk with {len(chunk)} items")

streaming_fm.process_large_data(process_chunk)

# Stream keys for memory-efficient processing
for key, value in streaming_fm.stream_keys():
    print(f"{key}: {value}")
```
