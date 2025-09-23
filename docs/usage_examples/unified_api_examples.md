# Unified API Examples

This document provides comprehensive examples of YAPFM's unified API and advanced features.

## Basic Unified API Usage

### Simple File Operations

```python
from yapfm import YAPFileManager

# Create a file manager
fm = YAPFileManager("config.json", auto_create=True)

# Unified API - simple and intuitive
fm.set("database.host", "localhost")
fm.set("database.port", 5432)
fm.set("api.version", "v2")

# Dictionary-like syntax
fm["logging.level"] = "INFO"
fm["logging.file"] = "app.log"

# Retrieve values
host = fm.get("database.host")
port = fm.get("database.port", 5432)  # with default
level = fm["logging.level"]

# Check existence
if fm.has("database.host"):
    print("Database host is configured")

# Delete keys
fm.delete("temp.key")
del fm["old.key"]
```

### Context Management

```python
# Automatic loading and saving
with YAPFileManager("config.json") as fm:
    fm.set("database.host", "localhost")
    fm.set("api.timeout", 30)
    # File is automatically saved when exiting context

# Lazy saving for multiple operations
with fm.lazy_save():
    fm.set("key1", "value1")
    fm.set("key2", "value2")
    fm.set("key3", "value3")
    # All changes saved at once when exiting lazy_save context
```

## Batch Operations

### Efficient Multi-Key Operations

```python
# Set multiple values at once
fm.set_multiple({
    "database.host": "localhost",
    "database.port": 5432,
    "database.ssl": True,
    "api.version": "v2",
    "api.timeout": 30,
    "logging.level": "INFO",
    "logging.file": "app.log"
})

# Get multiple values
values = fm.get_multiple([
    "database.host",
    "database.port",
    "api.timeout"
])

# Get multiple values with specific defaults
values = fm.get_multiple([
    "database.host",
    "database.port",
    "api.timeout",
    "missing.key"
], defaults={
    "database.host": "localhost",
    "database.port": 5432,
    "api.timeout": 30,
    "missing.key": "default_value"
})

# Check existence of multiple keys
exists = fm.has_multiple([
    "database.host",
    "database.port",
    "api.timeout",
    "missing.key"
])
# Returns: {"database.host": True, "database.port": True, "api.timeout": True, "missing.key": False}

# Delete multiple keys
deleted_count = fm.delete_multiple([
    "temp.key1",
    "temp.key2",
    "temp.key3"
])
print(f"Deleted {deleted_count} keys")
```

### Performance Comparison

```python
import time

# Individual operations (slower)
start = time.time()
for i in range(1000):
    fm.set(f"key{i}", f"value{i}")
individual_time = time.time() - start

# Batch operations (faster)
start = time.time()
batch_data = {f"batch_key{i}": f"value{i}" for i in range(1000)}
fm.set_multiple(batch_data)
batch_time = time.time() - start

print(f"Individual operations: {individual_time:.3f}s")
print(f"Batch operations: {batch_time:.3f}s")
print(f"Speedup: {individual_time/batch_time:.1f}x")
```

## Multi-File Operations

### Basic Multi-File Loading

```python
# Load multiple files with deep merge
data = fm.load_multiple_files([
    "base.json",
    "environment.json",
    "user.json"
], strategy="deep")

# Load with namespace strategy
data = fm.load_multiple_files([
    "database.json",
    "api.json",
    "cache.json"
], strategy="namespace", namespace_prefix="services")

# Load with priority strategy
data = fm.load_multiple_files([
    "base.json",
    "override.json"
], strategy="priority", priorities={"override.json": 2, "base.json": 1})
```

### Advanced Merge Strategies

```python
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

# Conditional loading based on environment
def load_environment_config(environment):
    """Load configuration based on environment."""
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
prod_config = load_environment_config("production")
```

### File Group Management

```python
# Define file groups
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
    }
}

# Load specific groups
core_config = fm.load_file_group("core_services", file_groups)
api_config = fm.load_file_group("api_services", file_groups)

# Load all groups
all_config = {}
for group_name in file_groups:
    group_config = fm.load_file_group(group_name, file_groups)
    all_config.update(group_config)
```

## Advanced Caching

### Cache Configuration

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
```

### Cache Statistics and Management

```python
# Get comprehensive cache statistics
stats = fm.get_cache_stats()
print(f"Cache hit rate: {stats['unified_cache']['hit_rate']:.2%}")
print(f"Cache size: {stats['unified_cache']['size']}")
print(f"Memory usage: {stats['unified_cache']['memory_usage']} bytes")
print(f"Lazy sections: {stats['lazy_sections']['total_sections']}")

# Cache invalidation
fm.invalidate_cache("database.*")  # Invalidate all database keys
fm.clear_cache()  # Clear all cache
fm.clear_key_cache()  # Clear key generation cache
```

## Data Analysis and Transformation

### Data Analysis

```python
# Get comprehensive statistics
stats = fm.get_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Max depth: {stats['max_depth']}")
print(f"File size: {stats['file_size']} bytes")
print(f"Type distribution: {stats['type_counts']}")

# Find duplicates
duplicates = fm.find_duplicates()
for value, keys in duplicates.items():
    if len(keys) > 1:
        print(f"Value '{value}' found in: {keys}")

# Get type distribution
types = fm.get_type_distribution()
print(f"String values: {types.get('str', 0)}")
print(f"Integer values: {types.get('int', 0)}")
```

### Data Transformation

```python
# Flatten nested structure
flat_data = fm.flatten()
print(flat_data)  # {'database.host': 'localhost', 'database.port': 5432}

# Transform all string values to uppercase
fm.transform_values(lambda x: x.upper() if isinstance(x, str) else x)

# Transform all keys to lowercase
fm.transform_keys(str.lower)

# Convert snake_case to camelCase
def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

fm.transform_keys(snake_to_camel)
```

### Data Cleanup

```python
# Remove null values
nulls_removed = fm.remove_nulls()
print(f"Removed {nulls_removed} null values")

# Remove empty sections
empty_sections_removed = fm.clean_empty_sections()
print(f"Removed {empty_sections_removed} empty sections")

# Compact data (remove nulls and empty sections)
result = fm.compact()
print(f"Total operations: {result['total_operations']}")
```

## Security Features

### Sensitive Data Handling

```python
# Mask sensitive data
masked_data = fm.mask_sensitive()
print(masked_data)  # Sensitive values replaced with "***"

# Mask specific keys
masked_data = fm.mask_sensitive(["password", "secret"], "HIDDEN")

# Get public configuration (sensitive data removed)
public_config = fm.get_public_config()

# Freeze file for read-only access
fm.freeze()
# fm.set("new.key", "value")  # This would raise PermissionError

# Unfreeze to allow modifications
fm.unfreeze()
fm.set("new.key", "value")  # Now works
```

## Export and Format Conversion

### Export to Different Formats

```python
# Export to different formats
json_str = fm.to_json(pretty=True)
yaml_str = fm.to_yaml()
toml_str = fm.to_toml()

# Export specific sections
db_config = fm.export_section("database", "json")
api_config = fm.export_section("api", "yaml", "api_config.yaml")

# Export entire data to file
fm.export_to_file("backup.json")
fm.export_to_file("config.yaml", "yaml")
```

## Error Handling and Validation

### Robust Error Handling

```python
def safe_operations(fm, operations):
    """Safely perform operations with error handling."""
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

results = safe_operations(fm, operations)
print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
print(f"Skipped: {len(results['skipped'])}")
```

## Complete Example: Application Configuration Management

```python
from yapfm import YAPFileManager
from pathlib import Path

class AppConfigManager:
    """Complete application configuration management example."""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Main configuration file
        self.main_config = YAPFileManager(
            self.config_dir / "main.json",
            auto_create=True,
            enable_cache=True,
            cache_size=1000
        )
        
        # Environment-specific files
        self.env_files = {
            "dev": self.config_dir / "dev.json",
            "prod": self.config_dir / "prod.json",
            "test": self.config_dir / "test.json"
        }
    
    def load_environment_config(self, environment):
        """Load configuration for specific environment."""
        files = [self.config_dir / "base.json"]
        
        if environment in self.env_files:
            files.append(self.env_files[environment])
        
        return self.main_config.load_multiple_files(
            files,
            strategy="deep"
        )
    
    def setup_database_config(self, environment):
        """Setup database configuration."""
        db_config = {
            "database.host": "localhost",
            "database.port": 5432,
            "database.ssl": False
        }
        
        if environment == "prod":
            db_config.update({
                "database.host": "prod-db-server",
                "database.ssl": True,
                "database.pool_size": 20
            })
        
        self.main_config.set_multiple(db_config)
    
    def setup_api_config(self):
        """Setup API configuration."""
        api_config = {
            "api.version": "v2",
            "api.timeout": 30,
            "api.rate_limit": 1000,
            "api.cors_origins": ["http://localhost:3000"]
        }
        
        self.main_config.set_multiple(api_config)
    
    def setup_logging_config(self, level="INFO"):
        """Setup logging configuration."""
        logging_config = {
            "logging.level": level,
            "logging.file": "app.log",
            "logging.max_size": "10MB",
            "logging.backup_count": 5
        }
        
        self.main_config.set_multiple(logging_config)
    
    def get_public_config(self):
        """Get public configuration (sensitive data masked)."""
        return self.main_config.get_public_config()
    
    def backup_config(self, backup_path):
        """Backup current configuration."""
        self.main_config.export_to_file(backup_path)
    
    def restore_config(self, backup_path):
        """Restore configuration from backup."""
        backup_fm = YAPFileManager(backup_path)
        self.main_config.data = backup_fm.data
        self.main_config.save()
    
    def validate_config(self):
        """Validate configuration."""
        # Check required keys
        required_keys = [
            "database.host",
            "database.port",
            "api.version",
            "logging.level"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not self.main_config.has(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        # Validate database port
        port = self.main_config.get("database.port")
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Invalid database port")
        
        return True

# Usage example
config_manager = AppConfigManager("my_app_config")

# Setup configuration for development
config_manager.setup_database_config("dev")
config_manager.setup_api_config()
config_manager.setup_logging_config("DEBUG")

# Validate configuration
try:
    config_manager.validate_config()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")

# Get public configuration for client
public_config = config_manager.get_public_config()

# Backup configuration
config_manager.backup_config("config_backup.json")
```

This comprehensive example demonstrates how to use YAPFM's unified API and advanced features for real-world application configuration management.
