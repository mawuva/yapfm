# User Guide

This comprehensive guide covers all aspects of using YAPFM in your projects, from basic operations to advanced patterns and best practices.

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [File Operations](#file-operations)
4. [Data Access Patterns](#data-access-patterns)
5. [Context Management](#context-management)
6. [Error Handling](#error-handling)
7. [Performance Considerations](#performance-considerations)
8. [Best Practices](#best-practices)
9. [Common Patterns](#common-patterns)

## 🚀 Getting Started

### Basic Setup

```python
from yapfm import YAPFileManager

# Create a file manager
fm = YAPFileManager("config.json")

# Load the file
fm.load()

# Your file is now ready to use!
```

### Using the open_file Helper

For a more convenient approach:

```python
from yapfm.helpers import open_file

# Open file with automatic format detection
fm = open_file("config.json")

# Force a specific format
fm = open_file("config.txt", format="toml")

# Auto-create if file doesn't exist
fm = open_file("new_config.json", auto_create=True)

# Use the file manager
with fm:
    fm.set_key("value", dot_key="key")
```

### With Context Manager (Recommended)

```python
from yapfm import YAPFileManager

# Automatic loading and saving
with YAPFileManager("config.json", auto_create=True) as fm:
    # Work with your configuration
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting the context
```

## 🧠 Core Concepts

### File Manager

The `YAPFileManager` is the main class that combines all functionality through mixins:

- **FileOperationsMixin**: Basic file operations (load, save, exists)
- **KeyOperationsMixin**: Key-based data access with dot notation
- **SectionOperationsMixin**: Section-based data management
- **ContextMixin**: Context manager support

### Strategies

YAPFM uses the Strategy pattern to handle different file formats:

- **JsonStrategy**: Handles JSON files
- **TomlStrategy**: Handles TOML files with comment preservation
- **YamlStrategy**: Handles YAML files with safe loading

### Dot Notation

YAPFM uses dot notation to access nested data:

```python
# Instead of: data["section"]["subsection"]["key"]
fm.get_key(dot_key="section.subsection.key")

# Instead of: data["section"]["subsection"]["key"] = "value"
fm.set_key("value", dot_key="section.subsection.key")
```

## 📁 File Operations

### Loading Files

```python
from yapfm import YAPFileManager

# Basic loading
fm = YAPFileManager("config.json")
fm.load()

# Auto-create if file doesn't exist
fm = YAPFileManager("config.json", auto_create=True)
fm.load()  # Creates empty file if it doesn't exist

# Check if file exists before loading
if fm.exists():
    fm.load()
else:
    print("File doesn't exist")
```

### Saving Files

```python
# Basic saving
fm.save()

# Save only if file has been modified
fm.save_if_dirty()

# Check if file needs saving
if fm.is_dirty():
    fm.save()
```

### File Status

```python
# Check various file states
print(f"File exists: {fm.exists()}")
print(f"File loaded: {fm.is_loaded()}")
print(f"File dirty: {fm.is_dirty()}")

# Manual state management
fm.mark_as_dirty()    # Mark as modified
fm.mark_as_clean()    # Mark as clean
fm.mark_as_loaded()   # Mark as loaded
```

### File Lifecycle

```python
# Complete file lifecycle
fm = YAPFileManager("config.json")

# 1. Load file
fm.load()

# 2. Make changes
fm.set_key("value", dot_key="key")

# 3. Save changes
fm.save()

# 4. Reload if needed (discards unsaved changes)
fm.reload()

# 5. Unload from memory
fm.unload()
```

## 🔑 Data Access Patterns

### Key Operations

#### Setting Values

```python
# Set single values
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key(True, dot_key="database.ssl")

# Set with path and key name
fm.set_key("localhost", path=["database"], key_name="host")

# Set with overwrite control
fm.set_key("new_value", dot_key="key", overwrite=True)   # Default
fm.set_key("new_value", dot_key="key", overwrite=False)  # Only if key doesn't exist
```

#### Getting Values

```python
# Get values with defaults
host = fm.get_key(dot_key="database.host", default="localhost")
port = fm.get_key(dot_key="database.port", default=5432)

# Get with path and key name
host = fm.get_key(path=["database"], key_name="host", default="localhost")

# Get without default (returns None if not found)
host = fm.get_key(dot_key="database.host")
```

#### Checking Existence

```python
# Check if key exists
if fm.has_key(dot_key="database.host"):
    print("Database host is configured")

# Check with path and key name
if fm.has_key(path=["database"], key_name="host"):
    print("Database host is configured")
```

#### Deleting Keys

```python
# Delete single keys
deleted = fm.delete_key(dot_key="database.host")
if deleted:
    print("Database host removed")

# Delete with path and key name
deleted = fm.delete_key(path=["database"], key_name="host")
```

### Section Operations

#### Setting Sections

```python
# Set entire sections
database_config = {
    "host": "localhost",
    "port": 5432,
    "name": "myapp",
    "ssl": True
}
fm.set_section(database_config, dot_key="database")

# Set nested sections
api_config = {
    "version": "v1",
    "timeout": 30,
    "cors": {
        "enabled": True,
        "origins": ["http://localhost:3000"]
    }
}
fm.set_section(api_config, dot_key="api")
```

#### Getting Sections

```python
# Get entire sections
database_config = fm.get_section(dot_key="database")
if database_config:
    print(f"Database: {database_config['host']}:{database_config['port']}")

# Get nested sections
cors_config = fm.get_section(dot_key="api.cors")
if cors_config:
    print(f"CORS origins: {cors_config['origins']}")
```

#### Checking Section Existence

```python
# Check if section exists
if fm.has_section(dot_key="database"):
    print("Database configuration exists")

# Check nested sections
if fm.has_section(dot_key="api.cors"):
    print("CORS configuration exists")
```

### Direct Data Access

```python
# Access data directly (auto-loads if not loaded)
data = fm.data
print(f"All data: {data}")

# Set data directly
fm.data = {
    "app": {"name": "My App", "version": "1.0.0"},
    "database": {"host": "localhost", "port": 5432}
}

# Modify data directly
fm.data["app"]["version"] = "1.1.0"
fm.mark_as_dirty()  # Remember to mark as dirty
```

## 🔄 Context Management

### Basic Context Manager

```python
from yapfm import YAPFileManager

# Automatic loading and saving
with YAPFileManager("config.json", auto_create=True) as fm:
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting the context
```

### Lazy Save Context

```python
# Save only when exiting the lazy_save context
with YAPFileManager("config.json") as fm:
    with fm.lazy_save():
        fm.set_key("value1", dot_key="key1")
        fm.set_key("value2", dot_key="key2")
        fm.set_key("value3", dot_key="key3")
        # Save happens here when exiting lazy_save context
```

### Auto Save Context

```python
# Auto-save context (similar to lazy_save)
with YAPFileManager("config.json") as fm:
    with fm.auto_save():
        fm.set_key("value", dot_key="key")
        # Save happens here when exiting auto_save context
```

### Context Manager with Error Handling

```python
try:
    with YAPFileManager("config.json", auto_create=True) as fm:
        fm.set_key("value", dot_key="key")
        # Some operation that might fail
        risky_operation()
except Exception as e:
    print(f"Error occurred: {e}")
    # File is still saved if no exception occurred
```

## ⚠️ Error Handling

### Common Exceptions

```python
from yapfm.exceptions import LoadFileError, FileWriteError, StrategyError

try:
    with YAPFileManager("config.json") as fm:
        fm.set_key("value", dot_key="key")
        fm.save()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
except FileWriteError as e:
    print(f"Failed to save file: {e}")
except StrategyError as e:
    print(f"Strategy error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Graceful Error Handling

```python
def safe_config_operation(config_file, key, value):
    """Safely set a configuration value with error handling."""
    try:
        with YAPFileManager(config_file, auto_create=True) as fm:
            fm.set_key(value, dot_key=key)
            return True
    except LoadFileError:
        print(f"Could not load configuration file: {config_file}")
        return False
    except FileWriteError:
        print(f"Could not save configuration file: {config_file}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Use the safe function
success = safe_config_operation("config.json", "database.host", "localhost")
if success:
    print("Configuration updated successfully")
```

### Validation and Error Prevention

```python
def validate_config_file(config_file):
    """Validate that a configuration file is usable."""
    try:
        fm = YAPFileManager(config_file)
        
        # Check if file exists
        if not fm.exists():
            print(f"Configuration file does not exist: {config_file}")
            return False
        
        # Try to load the file
        fm.load()
        
        # Check if file is valid
        if not isinstance(fm.data, dict):
            print(f"Configuration file is not a valid dictionary: {config_file}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Configuration file validation failed: {e}")
        return False

# Use validation
if validate_config_file("config.json"):
    print("Configuration file is valid")
else:
    print("Configuration file has issues")
```

## ⚡ Performance Considerations

### Lazy Loading

```python
# File is only loaded when first accessed
fm = YAPFileManager("config.json")
# File is not loaded yet

# Access data (triggers loading)
data = fm.data  # File is loaded here

# Or explicitly load
fm.load()  # File is loaded here
```

### Memory Management

```python
# Unload file from memory when done
fm = YAPFileManager("config.json")
fm.load()
# ... use the file ...
fm.unload()  # Free memory

# Or use context manager for automatic cleanup
with YAPFileManager("config.json") as fm:
    # ... use the file ...
    # File is automatically unloaded when exiting context
```

### Batch Operations

```python
# Batch multiple operations to reduce I/O
with YAPFileManager("config.json") as fm:
    with fm.lazy_save():
        # Multiple operations, single save
        fm.set_key("value1", dot_key="key1")
        fm.set_key("value2", dot_key="key2")
        fm.set_key("value3", dot_key="key3")
        # Single save at the end
```

## 🎯 Best Practices

### 1. Use Context Managers

```python
# ✅ Good: Automatic cleanup
with YAPFileManager("config.json", auto_create=True) as fm:
    fm.set_key("value", dot_key="key")

# ❌ Avoid: Manual cleanup
fm = YAPFileManager("config.json")
fm.load()
fm.set_key("value", dot_key="key")
fm.save()
```

### 2. Set Defaults

```python
# ✅ Good: Always provide defaults
host = fm.get_key(dot_key="database.host", default="localhost")

# ❌ Avoid: No defaults
host = fm.get_key(dot_key="database.host")  # Could be None
```

### 3. Validate Configuration

```python
# ✅ Good: Validate before use
def load_config():
    with YAPFileManager("config.json", auto_create=True) as fm:
        # Set required defaults
        if not fm.has_key(dot_key="database.host"):
            fm.set_key("localhost", dot_key="database.host")
        
        return fm.data

# ❌ Avoid: No validation
def load_config():
    with YAPFileManager("config.json") as fm:
        return fm.data  # Could be missing required keys
```

### 4. Handle Errors Gracefully

```python
# ✅ Good: Comprehensive error handling
try:
    with YAPFileManager("config.json") as fm:
        fm.set_key("value", dot_key="key")
except LoadFileError as e:
    logger.error(f"Failed to load config: {e}")
    # Fallback to default config
except FileWriteError as e:
    logger.error(f"Failed to save config: {e}")
    # Handle save failure
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors

# ❌ Avoid: No error handling
with YAPFileManager("config.json") as fm:
    fm.set_key("value", dot_key="key")  # Could fail silently
```

### 5. Use Meaningful Key Names

```python
# ✅ Good: Clear, descriptive keys
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key("myapp", dot_key="database.name")

# ❌ Avoid: Unclear keys
fm.set_key("localhost", dot_key="db.h")
fm.set_key(5432, dot_key="db.p")
fm.set_key("myapp", dot_key="db.n")
```

## 🎨 Common Patterns

### 1. Configuration Management

```python
class AppConfig:
    def __init__(self, config_file="config.json"):
        self.fm = YAPFileManager(config_file, auto_create=True)
    
    def load(self):
        """Load configuration with defaults."""
        with self.fm:
            # Set defaults if not present
            defaults = {
                "app.name": "My App",
                "app.version": "1.0.0",
                "database.host": "localhost",
                "database.port": 5432,
                "debug": False
            }
            
            for key, value in defaults.items():
                if not self.fm.has_key(dot_key=key):
                    self.fm.set_key(value, dot_key=key)
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.fm.get_key(dot_key=key, default=default)
    
    def set(self, key, value):
        """Set configuration value."""
        self.fm.set_key(value, dot_key=key)
        self.fm.save()

# Use the configuration manager
config = AppConfig("my_app_config.json")
config.load()
app_name = config.get("app.name")
config.set("debug", True)
```

### 2. Environment-Specific Configuration

```python
import os
from yapfm import YAPFileManager

class EnvironmentConfig:
    def __init__(self, base_config="config.json"):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.config_file = f"config_{self.env}.json"
        self.fm = YAPFileManager(self.config_file, auto_create=True)
    
    def load(self):
        """Load environment-specific configuration."""
        with self.fm:
            # Set environment
            self.fm.set_key(self.env, dot_key="environment")
            
            # Set environment-specific defaults
            if self.env == "development":
                self.fm.set_key(True, dot_key="debug")
                self.fm.set_key("localhost", dot_key="database.host")
            elif self.env == "production":
                self.fm.set_key(False, dot_key="debug")
                self.fm.set_key("prod-db.example.com", dot_key="database.host")
    
    def get_database_url(self):
        """Get database URL for current environment."""
        host = self.fm.get_key(dot_key="database.host")
        port = self.fm.get_key(dot_key="database.port")
        name = self.fm.get_key(dot_key="database.name")
        return f"postgresql://{host}:{port}/{name}"

# Use environment-specific configuration
config = EnvironmentConfig()
config.load()
db_url = config.get_database_url()
```

### 3. Configuration Validation

```python
from yapfm import YAPFileManager

class ConfigValidator:
    def __init__(self, config_file):
        self.fm = YAPFileManager(config_file)
    
    def validate(self):
        """Validate configuration file."""
        errors = []
        
        # Required keys
        required_keys = [
            "app.name",
            "app.version",
            "database.host",
            "database.port"
        ]
        
        for key in required_keys:
            if not self.fm.has_key(dot_key=key):
                errors.append(f"Missing required key: {key}")
        
        # Validate specific values
        if self.fm.has_key(dot_key="database.port"):
            port = self.fm.get_key(dot_key="database.port")
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append("Invalid database port")
        
        if self.fm.has_key(dot_key="debug"):
            debug = self.fm.get_key(dot_key="debug")
            if not isinstance(debug, bool):
                errors.append("Debug flag must be boolean")
        
        return errors
    
    def is_valid(self):
        """Check if configuration is valid."""
        return len(self.validate()) == 0

# Use configuration validator
validator = ConfigValidator("config.json")
if validator.is_valid():
    print("Configuration is valid")
else:
    errors = validator.validate()
    print(f"Configuration errors: {errors}")
```

---

*Ready to explore more advanced features? Check out the [Advanced Features Guide](advanced_features.md) for proxy patterns, custom strategies, and performance optimization.*
