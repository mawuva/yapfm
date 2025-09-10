# Quick Start Guide

Get up and running with YAPFM in just a few minutes! This guide will walk you through the essential features and common usage patterns.

## 🚀 Installation

First, install YAPFM:

```bash
pip install yapfm
```

## 📝 Basic Usage

### 1. Simple File Operations

```python
from yapfm import YAPFileManager

# Create a file manager for a JSON file
fm = YAPFileManager("config.json")

# Load the file (creates empty document if file doesn't exist)
fm.load()

# Set some configuration values
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key("myapp", dot_key="database.name")

# Save changes
fm.save()

# Read values back
host = fm.get_key(dot_key="database.host")
print(f"Database host: {host}")  # Output: Database host: localhost
```

### 2. Context Manager (Recommended)

```python
from yapfm import YAPFileManager

# Automatic loading and saving with context manager
with YAPFileManager("config.toml", auto_create=True) as fm:
    # Set configuration values
    fm.set_key("production", dot_key="environment")
    fm.set_key(True, dot_key="debug")
    
    # Set entire sections
    fm.set_section({
        "host": "localhost",
        "port": 8000,
        "workers": 4
    }, dot_key="server")
    
# File is automatically saved when exiting the context
```

## 🎯 Key Features

### Dot Notation Access

YAPFM uses dot notation to access nested data:

```python
# Set nested values
fm.set_key("value", dot_key="section.subsection.key")

# Get nested values with defaults
value = fm.get_key(dot_key="section.subsection.key", default="default")

# Check if key exists
exists = fm.has_key(dot_key="section.subsection.key")

# Delete keys
deleted = fm.delete_key(dot_key="section.subsection.key")
```

### Section Operations

Work with entire sections of configuration:

```python
# Set entire sections
fm.set_section({
    "host": "localhost",
    "port": 5432,
    "ssl": True
}, dot_key="database")

# Get entire sections
db_config = fm.get_section(dot_key="database")

# Check if section exists
has_section = fm.has_section(dot_key="database")
```

### Multiple File Formats

YAPFM automatically detects file format based on extension:

```python
# JSON file
json_fm = YAPFileManager("config.json")

# TOML file
toml_fm = YAPFileManager("config.toml")

# YAML file
yaml_fm = YAPFileManager("config.yaml")
```

### Using the open_file Helper

For a more convenient way to open files:

```python
from yapfm.helpers import open_file

# Automatic format detection
fm = open_file("config.json")

# Force a specific format regardless of extension
fm = open_file("config.txt", format="toml")

# Auto-create file if it doesn't exist
fm = open_file("new_config.json", auto_create=True)

# Use the file manager
with fm:
    fm.set_key("value", dot_key="key")
```

## 🔧 Common Patterns

### 1. Configuration Management

```python
from yapfm import YAPFileManager

def load_app_config():
    """Load application configuration with defaults."""
    with YAPFileManager("app_config.json", auto_create=True) as fm:
        # Set defaults if not present
        if not fm.has_key(dot_key="app.name"):
            fm.set_key("My App", dot_key="app.name")
        
        if not fm.has_key(dot_key="app.version"):
            fm.set_key("1.0.0", dot_key="app.version")
        
        if not fm.has_key(dot_key="database.host"):
            fm.set_key("localhost", dot_key="database.host")
        
        return fm.data

# Use the configuration
config = load_app_config()
print(f"App: {config['app']['name']} v{config['app']['version']}")
```

### 2. Environment-Specific Configuration

```python
import os
from yapfm import YAPFileManager

def get_config_for_environment(env="development"):
    """Load configuration for specific environment."""
    config_file = f"config_{env}.json"
    
    with YAPFileManager(config_file, auto_create=True) as fm:
        # Set environment-specific defaults
        fm.set_key(env, dot_key="environment")
        
        if env == "development":
            fm.set_key(True, dot_key="debug")
            fm.set_key("localhost", dot_key="database.host")
        elif env == "production":
            fm.set_key(False, dot_key="debug")
            fm.set_key("prod-db.example.com", dot_key="database.host")
        
        return fm.data

# Load configuration for current environment
env = os.getenv("ENVIRONMENT", "development")
config = get_config_for_environment(env)
```

### 3. Configuration Validation

```python
from yapfm import YAPFileManager

def validate_config(config):
    """Validate required configuration keys."""
    required_keys = [
        "database.host",
        "database.port",
        "app.name",
        "app.version"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not config.has_key(dot_key=key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    return True

# Use validation
with YAPFileManager("config.json") as fm:
    validate_config(fm)
    print("Configuration is valid!")
```

## 🎨 Advanced Usage

### Proxy with Logging

```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create file manager
fm = YAPFileManager("app_config.json")

# Create proxy with logging and metrics
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True
)

# All operations are logged and measured
with proxy:
    proxy.set_key("v1.0.0", dot_key="app.version")
    proxy.set_key("production", dot_key="app.environment")
```

### Custom Audit Hook

```python
def audit_hook(method, args, kwargs, result):
    """Custom audit hook for tracking changes."""
    print(f"🔍 AUDIT: {method} called with {args}, {kwargs} => {result}")

# Use custom audit hook
proxy = FileManagerProxy(
    fm,
    enable_audit=True,
    audit_hook=audit_hook
)
```

## 📊 File Status Operations

```python
from yapfm import YAPFileManager

fm = YAPFileManager("config.json")

# Check file status
print(f"File exists: {fm.exists()}")
print(f"File loaded: {fm.is_loaded()}")
print(f"File dirty: {fm.is_dirty()}")

# Manual operations
fm.load()      # Load from disk
fm.save()      # Save to disk
fm.reload()    # Reload from disk (discards changes)
fm.unload()    # Unload from memory
```

## 🔄 Lazy Save Context

```python
from yapfm import YAPFileManager

with YAPFileManager("config.json") as fm:
    # Make multiple changes
    with fm.lazy_save():
        fm.set_key("value1", dot_key="key1")
        fm.set_key("value2", dot_key="key2")
        fm.set_key("value3", dot_key="key3")
        # Save happens here when exiting the lazy_save context
```

## 🎯 Supported File Formats

| Format | Extension | Example |
|--------|-----------|---------|
| JSON | `.json` | `config.json` |
| TOML | `.toml` | `config.toml` |
| YAML | `.yml`, `.yaml` | `config.yaml` |

## 🚨 Error Handling

```python
from yapfm import YAPFileManager
from yapfm.exceptions import LoadFileError, FileWriteError

try:
    with YAPFileManager("config.json") as fm:
        fm.set_key("value", dot_key="key")
        fm.save()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
except FileWriteError as e:
    print(f"Failed to save file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📚 Next Steps

Now that you've got the basics down:

1. **Read the [User Guide](user_guide.md)** for comprehensive usage patterns
2. **Explore [Examples](examples.md)** for real-world scenarios
3. **Check the [API Reference](api_reference.md)** for complete documentation
4. **Learn [Advanced Features](advanced_features.md)** for power users

## 💡 Tips and Best Practices

1. **Use context managers** for automatic file handling
2. **Set `auto_create=True`** for configuration files that might not exist
3. **Use dot notation** for cleaner, more readable code
4. **Validate configuration** before using it in production
5. **Use proxy pattern** for logging and monitoring in production
6. **Handle exceptions** gracefully for better user experience

---

*Ready to dive deeper? Check out the [User Guide](user_guide.md) for comprehensive usage patterns and advanced features.*
