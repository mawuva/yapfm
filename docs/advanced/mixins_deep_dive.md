# Mixins Deep Dive

## Advanced Multi-File Operations

YAPFM provides powerful multi-file operations with various merge strategies for complex configuration management scenarios.

### Merge Strategies Deep Dive

#### Deep Merge Strategy

The most commonly used strategy for configuration layering:

```python
from yapfm import YAPFileManager
from yapfm.multi_file.strategies import MergeStrategy

fm = YAPFileManager("config.json")

# Deep merge with custom options
data = fm.load_multiple_files([
    "base.json",
    "environment.json", 
    "user.json"
], strategy="deep")

# Deep merge with conflict resolution
def resolve_conflicts(key, value1, value2):
    """Custom conflict resolution function."""
    if key == "database.host":
        return value2  # Always use the newer value
    elif key == "logging.level":
        # Use the more verbose level
        levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        return value1 if levels.get(value1, 0) > levels.get(value2, 0) else value2
    else:
        return value2  # Default: newer value wins

data = fm.load_multiple_files(
    ["base.json", "override.json"],
    strategy="deep",
    conflict_resolver=resolve_conflicts
)
```

#### Namespace Strategy with Custom Prefixes

Organize configurations by environment or component:

```python
# Environment-based namespacing
data = fm.load_multiple_files([
    "database.json",
    "api.json",
    "cache.json"
], strategy="namespace", namespace_prefix="services")

# Result structure:
# {
#     "services": {
#         "database": {...},
#         "api": {...},
#         "cache": {...}
#     }
# }

# Component-based namespacing
data = fm.load_multiple_files([
    "frontend.json",
    "backend.json",
    "mobile.json"
], strategy="namespace", namespace_prefix="components")
```

#### Priority Strategy with Complex Rules

Handle complex precedence scenarios:

```python
# Define priority rules
priorities = {
    "user.json": 100,      # Highest priority
    "environment.json": 50, # Medium priority
    "base.json": 10        # Lowest priority
}

data = fm.load_multiple_files([
    "base.json",
    "environment.json",
    "user.json"
], strategy="priority", priorities=priorities)

# Conditional priority based on file content
def dynamic_priority(file_path, data):
    """Calculate priority based on file content."""
    if data.get("environment") == "production":
        return 100
    elif "override" in str(file_path):
        return 75
    else:
        return 25

data = fm.load_multiple_files(
    ["base.json", "override.json", "prod.json"],
    strategy="priority",
    priority_calculator=dynamic_priority
)
```

#### Conditional Strategy for Dynamic Loading

Load files based on runtime conditions:

```python
def load_environment_specific_files(environment):
    """Load files based on environment."""
    def condition(file_path, data):
        # Load base files always
        if "base" in str(file_path):
            return True
        
        # Load environment-specific files
        if environment in str(file_path):
            return True
            
        # Load files that match current environment
        if data.get("environment") == environment:
            return True
            
        return False
    
    return fm.load_multiple_files(
        ["base.json", "dev.json", "prod.json", "staging.json"],
        strategy="conditional",
        condition_func=condition
    )

# Load production configuration
prod_config = load_environment_specific_files("production")
```

### Advanced File Group Management

Organize complex multi-file scenarios:

```python
# Define comprehensive file groups
file_groups = {
    "core_services": {
        "files": ["database.json", "cache.json", "queue.json"],
        "strategy": "namespace",
        "namespace_prefix": "core"
    },
    "api_services": {
        "files": ["rest.json", "graphql.json", "websocket.json"],
        "strategy": "namespace", 
        "namespace_prefix": "api"
    },
    "environment_config": {
        "files": ["base.json", "dev.json", "prod.json"],
        "strategy": "priority",
        "priorities": {"prod.json": 100, "dev.json": 50, "base.json": 10}
    },
    "user_preferences": {
        "files": ["defaults.json", "user.json"],
        "strategy": "deep",
        "conditional_filter": lambda path, data: "user" in str(path)
    }
}

# Load specific groups
core_config = fm.load_file_group("core_services", file_groups)
api_config = fm.load_file_group("api_services", file_groups)

# Load all groups into a single configuration
all_config = {}
for group_name in file_groups:
    group_config = fm.load_file_group(group_name, file_groups)
    all_config.update(group_config)
```

### Performance Optimization with Caching

Optimize multi-file operations with intelligent caching:

```python
# Enable caching for multi-file operations
fm = YAPFileManager("config.json", enable_cache=True, cache_size=5000)

# Load with caching enabled
data = fm.load_multiple_files([
    "base.json",
    "environment.json",
    "user.json"
], strategy="deep", use_cache=True)

# Cache statistics for multi-file operations
stats = fm.get_cache_stats()
print(f"Multi-file cache hits: {stats['multi_file']['hits']}")
print(f"Cache efficiency: {stats['multi_file']['hit_rate']:.2%}")

# Invalidate specific file caches
fm.invalidate_multi_file_cache("environment.json")
```

### Error Handling and Validation

Robust error handling for multi-file operations:

```python
def safe_load_multiple_files(fm, files, strategy="deep", **kwargs):
    """Safely load multiple files with error handling."""
    try:
        return fm.load_multiple_files(files, strategy=strategy, **kwargs)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        # Try loading available files
        available_files = [f for f in files if Path(f).exists()]
        if available_files:
            return fm.load_multiple_files(available_files, strategy=strategy, **kwargs)
        return {}
    except Exception as e:
        print(f"Error loading files: {e}")
        return {}

# Usage with error handling
data = safe_load_multiple_files(
    fm, 
    ["base.json", "missing.json", "environment.json"],
    strategy="deep"
)
```

## Unified API and Batch Operations

YAPFM provides a unified API that simplifies common operations while maintaining the power of individual mixins.

### Unified API Benefits

The unified API provides:
- **Simplified syntax**: `fm.set()` instead of `fm.set_key()`
- **Dictionary-like interface**: `fm["key"]` for natural Python syntax
- **Consistent behavior**: All operations work the same way across formats
- **Performance optimization**: Batch operations for efficiency

### Batch Operations Deep Dive

#### Efficient Multi-Key Operations

```python
from yapfm import YAPFileManager

fm = YAPFileManager("config.json")

# Traditional approach (inefficient)
fm.set("database.host", "localhost")
fm.set("database.port", 5432)
fm.set("database.ssl", True)
fm.set("api.version", "v2")
fm.set("api.timeout", 30)

# Batch approach (efficient)
fm.set_multiple({
    "database.host": "localhost",
    "database.port": 5432,
    "database.ssl": True,
    "api.version": "v2",
    "api.timeout": 30
})

# Batch operations with error handling
try:
    fm.set_multiple({
        "valid.key": "value",
        "invalid.key": None  # This might fail
    })
except ValueError as e:
    print(f"Some keys failed to set: {e}")
```

#### Advanced Batch Retrieval

```python
# Get multiple values with different defaults
values = fm.get_multiple([
    "database.host",
    "database.port", 
    "api.timeout",
    "logging.level"
], defaults={
    "database.host": "localhost",
    "database.port": 5432,
    "api.timeout": 30,
    "logging.level": "INFO"
})

# Check existence of multiple keys
exists = fm.has_multiple([
    "database.host",
    "database.port",
    "missing.key"
])
# Returns: {"database.host": True, "database.port": True, "missing.key": False}

# Delete multiple keys with validation
deleted_count = fm.delete_multiple([
    "temp.key1",
    "temp.key2",
    "temp.key3"
])
print(f"Deleted {deleted_count} keys")
```

#### Performance Optimization with Batch Operations

```python
import time
from yapfm import YAPFileManager

fm = YAPFileManager("large_config.json", enable_cache=True)

# Measure performance difference
def measure_performance():
    # Individual operations
    start = time.time()
    for i in range(1000):
        fm.set(f"key{i}", f"value{i}")
    individual_time = time.time() - start
    
    # Batch operations
    start = time.time()
    batch_data = {f"batch_key{i}": f"value{i}" for i in range(1000)}
    fm.set_multiple(batch_data)
    batch_time = time.time() - start
    
    print(f"Individual operations: {individual_time:.3f}s")
    print(f"Batch operations: {batch_time:.3f}s")
    print(f"Speedup: {individual_time/batch_time:.1f}x")

measure_performance()
```

### Dictionary-like Interface

YAPFM supports full dictionary-like syntax for seamless integration:

```python
# Natural Python syntax
fm["database.host"] = "localhost"
host = fm["database.host"]
"database.host" in fm
del fm["database.host"]

# Iteration support
for key in fm:
    print(f"Key: {key}")

for key, value in fm.items():
    print(f"{key}: {value}")

# Dictionary methods
fm.update({
    "new.key1": "value1",
    "new.key2": "value2"
})

# Pop with default
value = fm.pop("key", "default_value")

# Clear all data
fm.clear()
```

### Advanced Caching with Unified API

```python
# Enable advanced caching
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=2000,
    cache_ttl=7200  # 2 hours
)

# Cache-aware operations
fm.set("database.host", "localhost")  # Automatically cached
host = fm.get("database.host")        # Retrieved from cache

# Batch operations with cache optimization
fm.set_multiple({
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
})  # All keys cached efficiently

# Cache statistics
stats = fm.get_cache_stats()
print(f"Cache hit rate: {stats['unified_cache']['hit_rate']:.2%}")
print(f"Cache size: {stats['unified_cache']['size']}")
print(f"Memory usage: {stats['unified_cache']['memory_usage']} bytes")

# Cache invalidation
fm.invalidate_cache("database.*")  # Invalidate all database keys
fm.clear_cache()  # Clear all cache
```

### Error Handling and Validation

```python
def safe_batch_operations(fm, operations):
    """Safely perform batch operations with error handling."""
    results = {
        "successful": [],
        "failed": [],
        "skipped": []
    }
    
    for operation_type, data in operations.items():
        try:
            if operation_type == "set":
                fm.set_multiple(data)
                results["successful"].extend(data.keys())
            elif operation_type == "delete":
                deleted = fm.delete_multiple(data)
                results["successful"].extend(data[:deleted])
                results["skipped"].extend(data[deleted:])
            elif operation_type == "get":
                values = fm.get_multiple(data)
                results["successful"].extend(values.keys())
        except Exception as e:
            results["failed"].append({
                "operation": operation_type,
                "data": data,
                "error": str(e)
            })
    
    return results

# Usage
operations = {
    "set": {"key1": "value1", "key2": "value2"},
    "delete": ["old_key1", "old_key2"],
    "get": ["key1", "key2", "key3"]
}

results = safe_batch_operations(fm, operations)
print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
print(f"Skipped: {len(results['skipped'])}")
```

## Creating Custom Mixins

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

## Using Custom Mixins

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
