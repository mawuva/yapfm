# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with YAPFM, including error messages, performance problems, and configuration issues.

## 📚 Table of Contents

1. [Common Issues](#common-issues)
2. [Error Reference](#error-reference)
3. [Performance Issues](#performance-issues)
4. [Configuration Problems](#configuration-problems)
5. [File Format Issues](#file-format-issues)
6. [Memory and Resource Issues](#memory-and-resource-issues)
7. [Debugging Tips](#debugging-tips)
8. [Frequently Asked Questions](#frequently-asked-questions)

## 🚨 Common Issues

### File Not Found Errors

**Problem**: `FileNotFoundError` when trying to load a file.

**Solutions**:
```python
# 1. Use auto_create=True
fm = YAPFileManager("config.json", auto_create=True)

# 2. Check if file exists first
if fm.exists():
    fm.load()
else:
    print("File does not exist")

# 3. Create the file manually
fm.create_empty_file()
```

### Permission Denied Errors

**Problem**: `PermissionError` when trying to save a file.

**Solutions**:
```python
# 1. Check file permissions
import os
print(f"File permissions: {oct(os.stat('config.json').st_mode)[-3:]}")

# 2. Check directory permissions
print(f"Directory permissions: {oct(os.stat('.').st_mode)[-3:]}")

# 3. Run with appropriate permissions
# On Unix/Linux: chmod 644 config.json
# On Windows: Check file properties
```

### Strategy Not Found Errors

**Problem**: `StrategyError` when trying to use an unsupported file format.

**Solutions**:
```python
# 1. Check supported formats
from yapfm.registry import FileStrategyRegistry
print(f"Supported formats: {FileStrategyRegistry.get_supported_formats()}")

# 2. Register a custom strategy
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy(".xml")
class XmlStrategy:
    def load(self, file_path):
        # Implementation
        pass
    
    def save(self, file_path, data):
        # Implementation
        pass
    
    def navigate(self, document, path, create=False):
        # Implementation
        pass

# 3. Use a supported format
fm = YAPFileManager("config.json")  # Use .json instead of .xml
```

### Data Type Errors

**Problem**: `TypeError` when setting data that's not a dictionary.

**Solutions**:
```python
# 1. Ensure data is a dictionary
data = {"key": "value"}  # Correct
fm.data = data

# 2. Convert other types to dictionary
import json
json_string = '{"key": "value"}'
data = json.loads(json_string)
fm.data = data

# 3. Use proper data structure
# For lists, wrap in a dictionary
fm.data = {"items": [1, 2, 3]}  # Correct
# fm.data = [1, 2, 3]  # Incorrect
```

## ⚠️ Error Reference

### LoadFileError

**When it occurs**: Error loading a file from disk.

**Common causes**:
- File doesn't exist
- Invalid file format
- Corrupted file
- Permission issues

**Solutions**:
```python
from yapfm.exceptions import LoadFileError

try:
    fm.load()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
    # Handle the error appropriately
```

### FileWriteError

**When it occurs**: Error writing a file to disk.

**Common causes**:
- Permission denied
- Disk full
- Invalid data format
- File locked by another process

**Solutions**:
```python
from yapfm.exceptions import FileWriteError

try:
    fm.save()
except FileWriteError as e:
    print(f"Failed to save file: {e}")
    # Handle the error appropriately
```

### StrategyError

**When it occurs**: Error with file strategy.

**Common causes**:
- Unsupported file format
- Strategy not registered
- Invalid strategy implementation

**Solutions**:
```python
from yapfm.exceptions import StrategyError

try:
    fm = YAPFileManager("file.xyz")
except StrategyError as e:
    print(f"Strategy error: {e}")
    # Use a supported format or register a custom strategy
```

## ⚡ Performance Issues

### Slow File Operations

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

### Memory Usage Issues

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

### Thread Safety Issues

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

## ⚙️ Configuration Problems

### Invalid Configuration Structure

**Problem**: Configuration file has invalid structure.

**Solutions**:
```python
# 1. Validate configuration
def validate_config(data):
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a dictionary")
    
    required_keys = ["app", "database"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    return True

# 2. Use configuration validator
class ConfigValidator:
    def __init__(self, fm):
        self.fm = fm
    
    def validate(self):
        with self.fm:
            return validate_config(self.fm.data)

# 3. Fix common issues
def fix_config_issues(fm):
    with fm:
        data = fm.data
        
        # Ensure top-level is dictionary
        if not isinstance(data, dict):
            fm.data = {"config": data}
        
        # Add missing required keys
        if "app" not in data:
            data["app"] = {"name": "My App", "version": "1.0.0"}
        
        if "database" not in data:
            data["database"] = {"host": "localhost", "port": 5432}
```

### Environment-Specific Issues

**Problem**: Configuration not working in different environments.

**Solutions**:
```python
import os

# 1. Use environment variables
def load_env_config():
    env = os.getenv("ENVIRONMENT", "development")
    config_file = f"config_{env}.json"
    
    fm = YAPFileManager(config_file, auto_create=True)
    with fm:
        # Set environment-specific defaults
        if env == "development":
            fm.set_key(True, dot_key="debug")
        elif env == "production":
            fm.set_key(False, dot_key="debug")
    
    return fm

# 2. Use configuration inheritance
def load_merged_config():
    base_fm = YAPFileManager("base_config.json")
    env_fm = YAPFileManager(f"config_{os.getenv('ENVIRONMENT', 'development')}.json")
    
    with base_fm:
        base_data = base_fm.data
    
    with env_fm:
        env_data = env_fm.data
    
    # Merge configurations
    merged_data = {**base_data, **env_data}
    
    return merged_data
```

## 📄 File Format Issues

### JSON Format Issues

**Problem**: Invalid JSON format.

**Solutions**:
```python
# 1. Validate JSON before loading
import json

def validate_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

# 2. Fix common JSON issues
def fix_json_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix common issues
    content = content.replace("'", '"')  # Replace single quotes
    content = content.replace("True", "true")  # Fix boolean values
    content = content.replace("False", "false")
    content = content.replace("None", "null")
    
    with open(file_path, 'w') as f:
        f.write(content)

# 3. Use proper JSON formatting
def format_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### TOML Format Issues

**Problem**: Invalid TOML format.

**Solutions**:
```python
# 1. Validate TOML
import toml

def validate_toml_file(file_path):
    try:
        with open(file_path, 'r') as f:
            toml.load(f)
        return True
    except toml.TomlDecodeError as e:
        print(f"Invalid TOML: {e}")
        return False

# 2. Fix common TOML issues
def fix_toml_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix common issues
    content = content.replace("True", "true")
    content = content.replace("False", "false")
    content = content.replace("None", "null")
    
    with open(file_path, 'w') as f:
        f.write(content)
```

### YAML Format Issues

**Problem**: Invalid YAML format.

**Solutions**:
```python
# 1. Validate YAML
import yaml

def validate_yaml_file(file_path):
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError as e:
        print(f"Invalid YAML: {e}")
        return False

# 2. Fix common YAML issues
def fix_yaml_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix common issues
    content = content.replace("True", "true")
    content = content.replace("False", "false")
    content = content.replace("None", "null")
    
    with open(file_path, 'w') as f:
        f.write(content)
```

## 🧠 Memory and Resource Issues

### Memory Leaks

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

### Resource Exhaustion

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

## 🔍 Debugging Tips

### Enable Debug Logging

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

### Use Debug Mode

```python
# Enable debug mode for more verbose output
import os
os.environ["YAPFM_DEBUG"] = "1"

# Or set debug flag
fm = YAPFileManager("config.json", debug=True)
```

### Inspect File State

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

### Trace Operations

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

## ❓ Frequently Asked Questions

### Q: How do I handle large configuration files?

**A**: Use streaming and chunked processing:

```python
# For very large files, process in chunks
def process_large_config(fm):
    with fm:
        data = fm.data
        
        # Process in chunks
        chunk_size = 1000
        items = list(data.items())
        
        for i in range(0, len(items), chunk_size):
            chunk = dict(items[i:i + chunk_size])
            process_chunk(chunk)
```

### Q: Can I use YAPFM with multiple file formats in the same application?

**A**: Yes, you can use different file managers for different formats:

```python
# Different file managers for different formats
json_fm = YAPFileManager("config.json")
toml_fm = YAPFileManager("config.toml")
yaml_fm = YAPFileManager("config.yaml")

# Or use a single manager with different files
configs = {
    "json": YAPFileManager("config.json"),
    "toml": YAPFileManager("config.toml"),
    "yaml": YAPFileManager("config.yaml")
}
```

### Q: How do I handle configuration validation?

**A**: Use a validation mixin or custom validation:

```python
class ConfigValidator:
    def __init__(self, fm):
        self.fm = fm
        self.rules = {}
    
    def add_rule(self, key, rule, message):
        self.rules[key] = {"rule": rule, "message": message}
    
    def validate(self):
        errors = []
        with self.fm:
            data = self.fm.data
            
            for key, rule_info in self.rules.items():
                if not rule_info["rule"](data.get(key)):
                    errors.append(rule_info["message"])
        
        return errors
```

### Q: Can I use YAPFM in a multi-threaded environment?

**A**: Yes, but you need to handle thread safety:

```python
import threading

# Use locks for thread safety
lock = threading.Lock()

def thread_safe_operation(fm):
    with lock:
        fm.set_key("value", dot_key="key")

# Or use a thread-safe wrapper
class ThreadSafeFileManager:
    def __init__(self, path):
        self.fm = YAPFileManager(path)
        self.lock = threading.RLock()
    
    def __getattr__(self, name):
        attr = getattr(self.fm, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                with self.lock:
                    return attr(*args, **kwargs)
            return wrapper
        return attr
```

### Q: How do I handle configuration updates in production?

**A**: Use safe update patterns:

```python
def safe_config_update(fm, updates):
    # Create backup
    backup_file = f"{fm.path}.backup"
    if fm.exists():
        import shutil
        shutil.copy2(fm.path, backup_file)
    
    try:
        # Apply updates
        with fm:
            for key, value in updates.items():
                fm.set_key(value, dot_key=key)
        
        # Validate configuration
        if validate_config(fm.data):
            fm.save()
        else:
            raise ValueError("Configuration validation failed")
    
    except Exception as e:
        # Restore from backup
        if os.path.exists(backup_file):
            import shutil
            shutil.copy2(backup_file, fm.path)
        raise e
```

### Q: How do I monitor configuration changes?

**A**: Use the proxy pattern with audit hooks:

```python
def audit_hook(method, args, kwargs, result):
    print(f"Configuration changed: {method} with {args}")
    
    # Log to file
    with open("config_changes.log", "a") as f:
        f.write(f"{datetime.now()}: {method} - {args}\n")

proxy = FileManagerProxy(
    fm,
    enable_audit=True,
    audit_hook=audit_hook
)
```

### Q: How do I handle configuration encryption?

**A**: Use a custom mixin or wrapper:

```python
from cryptography.fernet import Fernet

class EncryptedFileManager:
    def __init__(self, path, key):
        self.fm = YAPFileManager(path)
        self.cipher = Fernet(key)
    
    def set_encrypted_key(self, value, dot_key):
        encrypted = self.cipher.encrypt(value.encode())
        self.fm.set_key(encrypted.decode(), dot_key=dot_key)
    
    def get_encrypted_key(self, dot_key, default=None):
        encrypted = self.fm.get_key(dot_key=dot_key, default=default)
        if encrypted:
            return self.cipher.decrypt(encrypted.encode()).decode()
        return default
```

---

*If you're still experiencing issues, please check the [GitHub Issues](https://github.com/mawuva/yapfm/issues) or create a new issue with detailed information about your problem.*
