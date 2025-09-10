# Advanced Features

This guide covers advanced features of YAPFM, including proxy patterns, custom strategies, mixins, and performance optimization techniques.

## 📚 Table of Contents

1. [Proxy Pattern](#proxy-pattern)
2. [Custom Strategies](#custom-strategies)
3. [Mixins Deep Dive](#mixins-deep-dive)
4. [Performance Optimization](#performance-optimization)
5. [Thread Safety](#thread-safety)
6. [Memory Management](#memory-management)
7. [Advanced Context Management](#advanced-context-management)
8. [Plugin Architecture](#plugin-architecture)

## 🎭 Proxy Pattern

The `FileManagerProxy` provides powerful capabilities for monitoring, logging, and auditing file operations without modifying the core functionality.

### Basic Proxy Usage

```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_proxy")

# Create file manager
fm = YAPFileManager("config.json", auto_create=True)

# Create proxy with monitoring
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True,
    logger=logger
)

# Use proxy like the original manager
with proxy:
    proxy.set_key("value", dot_key="key")
    # All operations are logged and measured
```

### Custom Audit Hooks

```python
def custom_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    """Custom audit hook for tracking configuration changes."""
    print(f"🔍 AUDIT: {method} called with {args}, {kwargs} => {result}")
    
    # Track specific operations
    if method == "set_key":
        key = args[1] if len(args) > 1 else kwargs.get('dot_key', 'unknown')
        value = args[0] if len(args) > 0 else 'unknown'
        print(f"Configuration changed: {key} = {value}")
    
    elif method == "delete_key":
        key = args[0] if len(args) > 0 else kwargs.get('dot_key', 'unknown')
        print(f"Configuration deleted: {key}")

# Use custom audit hook
proxy = FileManagerProxy(
    fm,
    enable_audit=True,
    audit_hook=custom_audit_hook
)
```

### Metrics Collection

```python
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.operation_times = defaultdict(list)
        self.operation_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    def collect_metrics(self, method: str, args: tuple, kwargs: dict, result: Any, execution_time: float) -> None:
        """Collect metrics for operations."""
        self.operation_times[method].append(execution_time)
        self.operation_counts[method] += 1
        
        if isinstance(result, Exception):
            self.error_counts[method] += 1
    
    def get_stats(self) -> dict:
        """Get collected statistics."""
        stats = {}
        for method, times in self.operation_times.items():
            stats[method] = {
                "count": self.operation_counts[method],
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "errors": self.error_counts[method]
            }
        return stats

# Use metrics collector
metrics = MetricsCollector()

def metrics_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    # This would be called by the proxy with execution time
    pass

proxy = FileManagerProxy(
    fm,
    enable_metrics=True,
    enable_audit=True,
    audit_hook=metrics_audit_hook
)
```

### Production Monitoring

```python
import json
from datetime import datetime
from typing import Dict, Any

class ProductionMonitor:
    def __init__(self, log_file: str = "config_operations.log"):
        self.log_file = log_file
        self.operations = []
    
    def log_operation(self, method: str, args: tuple, kwargs: dict, result: Any, execution_time: float) -> None:
        """Log operation for production monitoring."""
        operation = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "args": str(args),
            "kwargs": str(kwargs),
            "result_type": type(result).__name__,
            "execution_time_ms": execution_time * 1000,
            "success": not isinstance(result, Exception)
        }
        
        self.operations.append(operation)
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(operation) + "\n")
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of operations."""
        if not self.operations:
            return {}
        
        total_operations = len(self.operations)
        successful_operations = sum(1 for op in self.operations if op["success"])
        avg_execution_time = sum(op["execution_time_ms"] for op in self.operations) / total_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations,
            "average_execution_time_ms": avg_execution_time
        }

# Use production monitor
monitor = ProductionMonitor()

def monitor_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    # This would be called by the proxy with execution time
    pass

proxy = FileManagerProxy(
    fm,
    enable_metrics=True,
    enable_audit=True,
    audit_hook=monitor_audit_hook
)
```

## 🛠️ Custom Strategies

Creating custom strategies allows you to support new file formats or customize existing ones.

### Basic Custom Strategy

```python
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy
from pathlib import Path
from typing import Any, List, Optional, Union
import csv

@register_file_strategy(".csv")
class CsvStrategy:
    """Custom strategy for CSV files."""
    
    def load(self, file_path: Union[Path, str]) -> List[Dict[str, Any]]:
        """Load CSV file as list of dictionaries."""
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    
    def save(self, file_path: Union[Path, str], data: List[Dict[str, Any]]) -> None:
        """Save list of dictionaries as CSV file."""
        if not data:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def navigate(self, document: List[Dict[str, Any]], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate CSV document structure."""
        if not path:
            return document
        
        # For CSV, we can navigate by row index and column name
        if len(path) == 1:
            # Get all values for a column
            column = path[0]
            return [row.get(column) for row in document if column in row]
        elif len(path) == 2:
            # Get specific cell value
            try:
                row_index = int(path[0])
                column = path[1]
                if 0 <= row_index < len(document):
                    return document[row_index].get(column)
            except (ValueError, IndexError):
                pass
        
        return None

# Usage
fm = YAPFileManager("data.csv")  # Automatically uses CsvStrategy
```

### Advanced Custom Strategy with Validation

```python
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy([".json", ".yaml", ".yml"])
class MultiFormatStrategy:
    """Strategy that can handle multiple formats based on file extension."""
    
    def load(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Load file based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if extension == '.json':
            return json.loads(content)
        elif extension in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def save(self, file_path: Union[Path, str], data: Dict[str, Any]) -> None:
        """Save file based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.json':
            content = json.dumps(data, indent=2, ensure_ascii=False)
        elif extension in ['.yaml', '.yml']:
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    
    def navigate(self, document: Dict[str, Any], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate document structure."""
        current = document
        
        for part in path:
            if isinstance(current, dict):
                if part not in current:
                    if create:
                        current[part] = {}
                    else:
                        return None
                current = current[part]
            else:
                return None
        
        return current

# Usage
json_fm = YAPFileManager("config.json")  # Uses MultiFormatStrategy
yaml_fm = YAPFileManager("config.yaml")  # Uses MultiFormatStrategy
```

### Strategy with Caching

```python
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy(".json")
class CachedJsonStrategy:
    """JSON strategy with caching capabilities."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # path -> (data, timestamp)
        self._cache_ttl = 300  # 5 minutes
    
    def load(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Load JSON file with caching."""
        file_path = str(file_path)
        current_time = time.time()
        
        # Check cache
        if file_path in self._cache:
            data, timestamp = self._cache[file_path]
            if current_time - timestamp < self._cache_ttl:
                return data
        
        # Load from file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Update cache
        self._cache[file_path] = (data, current_time)
        
        return data
    
    def save(self, file_path: Union[Path, str], data: Dict[str, Any]) -> None:
        """Save JSON file and update cache."""
        file_path = str(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        # Update cache
        self._cache[file_path] = (data, time.time())
    
    def navigate(self, document: Dict[str, Any], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate document structure."""
        current = document
        
        for part in path:
            if isinstance(current, dict):
                if part not in current:
                    if create:
                        current[part] = {}
                    else:
                        return None
                current = current[part]
            else:
                return None
        
        return current
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for data, timestamp in self._cache.values():
            if current_time - timestamp < self._cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self._cache_ttl
        }
```

## 🔧 Mixins Deep Dive

### Creating Custom Mixins

```python
from yapfm.mixins import FileOperationsMixin
from typing import Any, Dict, List, Optional
import hashlib

class ValidationMixin:
    """Mixin for configuration validation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validation_rules: Dict[str, Any] = {}
        self._validation_errors: List[str] = []
    
    def add_validation_rule(self, key: str, rule: callable, message: str = None) -> None:
        """Add a validation rule for a configuration key."""
        self._validation_rules[key] = {
            "rule": rule,
            "message": message or f"Validation failed for key: {key}"
        }
    
    def validate_key(self, key: str, value: Any) -> bool:
        """Validate a single key."""
        if key not in self._validation_rules:
            return True
        
        rule = self._validation_rules[key]["rule"]
        try:
            result = rule(value)
            if not result:
                self._validation_errors.append(self._validation_rules[key]["message"])
            return result
        except Exception as e:
            self._validation_errors.append(f"Validation error for {key}: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Validate all configuration keys."""
        self._validation_errors.clear()
        
        if not self.is_loaded():
            self.load()
        
        # Validate all keys in the document
        self._validate_dict(self.data, "")
        
        return len(self._validation_errors) == 0
    
    def _validate_dict(self, data: Dict[str, Any], prefix: str) -> None:
        """Recursively validate dictionary data."""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._validate_dict(value, full_key)
            else:
                self.validate_key(full_key, value)
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        return self._validation_errors.copy()
    
    def set_key_with_validation(self, value: Any, dot_key: str) -> bool:
        """Set a key with validation."""
        if self.validate_key(dot_key, value):
            self.set_key(value, dot_key=dot_key)
            return True
        return False

class EncryptionMixin:
    """Mixin for configuration encryption."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._encryption_key: Optional[bytes] = None
    
    def set_encryption_key(self, key: str) -> None:
        """Set encryption key."""
        self._encryption_key = key.encode('utf-8')
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a string value."""
        if not self._encryption_key:
            return value
        
        from cryptography.fernet import Fernet
        f = Fernet(self._encryption_key)
        return f.encrypt(value.encode('utf-8')).decode('utf-8')
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value."""
        if not self._encryption_key:
            return encrypted_value
        
        from cryptography.fernet import Fernet
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    
    def set_encrypted_key(self, value: str, dot_key: str) -> None:
        """Set an encrypted configuration key."""
        encrypted_value = self.encrypt_value(value)
        self.set_key(encrypted_value, dot_key=dot_key)
    
    def get_encrypted_key(self, dot_key: str, default: str = None) -> str:
        """Get and decrypt a configuration key."""
        encrypted_value = self.get_key(dot_key=dot_key, default=default)
        if encrypted_value is None:
            return default
        
        return self.decrypt_value(encrypted_value)

# Create a custom file manager with mixins
class AdvancedFileManager(
    FileOperationsMixin,
    ValidationMixin,
    EncryptionMixin
):
    def __init__(self, path, **kwargs):
        self.path = path
        super().__init__(**kwargs)
```

### Using Custom Mixins

```python
# Create advanced file manager
fm = AdvancedFileManager("secure_config.json", auto_create=True)

# Set up validation rules
fm.add_validation_rule("database.port", lambda x: isinstance(x, int) and 1 <= x <= 65535)
fm.add_validation_rule("app.version", lambda x: isinstance(x, str) and len(x) > 0)

# Set up encryption
fm.set_encryption_key("my-secret-key")

# Use validation
fm.set_key_with_validation(5432, dot_key="database.port")  # Valid
fm.set_key_with_validation("invalid", dot_key="database.port")  # Invalid

# Use encryption
fm.set_encrypted_key("secret-password", dot_key="database.password")
password = fm.get_encrypted_key(dot_key="database.password")
```

## ⚡ Performance Optimization

### Lazy Loading Strategies

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

### Memory-Efficient Processing

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

## 🔒 Thread Safety

### Thread-Safe File Manager

```python
from yapfm import YAPFileManager
import threading
from typing import Any, Dict, Optional
import time

class ThreadSafeFileManager:
    """Thread-safe wrapper for file manager."""
    
    def __init__(self, path: str, **kwargs):
        self._fm = YAPFileManager(path, **kwargs)
        self._lock = threading.RLock()
        self._readers = 0
        self._writers = 0
        self._read_ready = threading.Condition(self._lock)
        self._write_ready = threading.Condition(self._lock)
    
    def read_operation(self, operation: callable) -> Any:
        """Perform a read operation with reader-writer lock."""
        with self._lock:
            while self._writers > 0:
                self._read_ready.wait()
            self._readers += 1
        
        try:
            return operation(self._fm)
        finally:
            with self._lock:
                self._readers -= 1
                if self._readers == 0:
                    self._write_ready.notify_all()
    
    def write_operation(self, operation: callable) -> Any:
        """Perform a write operation with reader-writer lock."""
        with self._lock:
            while self._readers > 0 or self._writers > 0:
                self._write_ready.wait()
            self._writers += 1
        
        try:
            return operation(self._fm)
        finally:
            with self._lock:
                self._writers -= 1
                self._read_ready.notify_all()
                self._write_ready.notify_all()
    
    def get_key(self, dot_key: str, default: Any = None) -> Any:
        """Thread-safe get key operation."""
        return self.read_operation(lambda fm: fm.get_key(dot_key=dot_key, default=default))
    
    def set_key(self, value: Any, dot_key: str) -> None:
        """Thread-safe set key operation."""
        self.write_operation(lambda fm: fm.set_key(value, dot_key=dot_key))
    
    def load(self) -> None:
        """Thread-safe load operation."""
        self.write_operation(lambda fm: fm.load())
    
    def save(self) -> None:
        """Thread-safe save operation."""
        self.write_operation(lambda fm: fm.save())

# Usage
thread_safe_fm = ThreadSafeFileManager("thread_safe_config.json")

# Multiple threads can safely access the file manager
def reader_thread():
    for i in range(10):
        value = thread_safe_fm.get_key("counter", default=0)
        print(f"Reader: {value}")
        time.sleep(0.1)

def writer_thread():
    for i in range(10):
        thread_safe_fm.set_key(i, "counter")
        print(f"Writer: {i}")
        time.sleep(0.1)

# Start threads
threading.Thread(target=reader_thread).start()
threading.Thread(target=writer_thread).start()
```

## 🧠 Memory Management

### Memory-Efficient File Manager

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

## 🔄 Advanced Context Management

### Nested Context Managers

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

## 🔌 Plugin Architecture

### Plugin System

```python
from yapfm import YAPFileManager
from typing import Any, Dict, List, Optional, Protocol
import importlib
import os

class Plugin(Protocol):
    """Plugin protocol for extending file manager functionality."""
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        """Initialize the plugin with the file manager."""
        ...
    
    def before_load(self, file_manager: YAPFileManager) -> None:
        """Called before loading the file."""
        ...
    
    def after_load(self, file_manager: YAPFileManager) -> None:
        """Called after loading the file."""
        ...
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        """Called before saving the file."""
        ...
    
    def after_save(self, file_manager: YAPFileManager) -> None:
        """Called after saving the file."""
        ...

class PluginManager:
    """Manager for file manager plugins."""
    
    def __init__(self, file_manager: YAPFileManager):
        self.file_manager = file_manager
        self.plugins: List[Plugin] = []
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        plugin.initialize(self.file_manager)
        self.plugins.append(plugin)
    
    def load_plugins_from_directory(self, directory: str) -> None:
        """Load plugins from a directory."""
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                module = importlib.import_module(f"{directory}.{module_name}")
                
                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, 'initialize') and
                        hasattr(attr, 'before_load')):
                        plugin = attr()
                        self.register_plugin(plugin)
    
    def before_load(self) -> None:
        """Call before_load on all plugins."""
        for plugin in self.plugins:
            plugin.before_load(self.file_manager)
    
    def after_load(self) -> None:
        """Call after_load on all plugins."""
        for plugin in self.plugins:
            plugin.after_load(self.file_manager)
    
    def before_save(self) -> None:
        """Call before_save on all plugins."""
        for plugin in self.plugins:
            plugin.before_save(self.file_manager)
    
    def after_save(self) -> None:
        """Call after_save on all plugins."""
        for plugin in self.plugins:
            plugin.after_save(self.file_manager)

class LoggingPlugin:
    """Plugin for logging file operations."""
    
    def __init__(self):
        self.logger = None
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        import logging
        self.logger = logging.getLogger("file_manager_plugin")
    
    def before_load(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"Loading file: {file_manager.path}")
    
    def after_load(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"File loaded: {file_manager.path}")
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"Saving file: {file_manager.path}")
    
    def after_save(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"File saved: {file_manager.path}")

class ValidationPlugin:
    """Plugin for validating configuration."""
    
    def __init__(self):
        self.validation_rules = {}
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        pass
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        # Validate configuration before saving
        if not self._validate_config(file_manager.data):
            raise ValueError("Configuration validation failed")
    
    def _validate_config(self, data: Dict[str, Any]) -> bool:
        # Add your validation logic here
        return True

# Usage
fm = YAPFileManager("plugin_config.json", auto_create=True)
plugin_manager = PluginManager(fm)

# Register plugins
plugin_manager.register_plugin(LoggingPlugin())
plugin_manager.register_plugin(ValidationPlugin())

# Use file manager with plugins
with fm:
    plugin_manager.before_load()
    fm.load()
    plugin_manager.after_load()
    
    fm.set_key("value", dot_key="key")
    
    plugin_manager.before_save()
    fm.save()
    plugin_manager.after_save()
```

---

*These advanced features demonstrate the extensibility and power of YAPFM. For troubleshooting and common issues, see the [Troubleshooting Guide](troubleshooting.md).*
