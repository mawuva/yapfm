# Merge Strategies

YAPFM provides multiple merge strategies for combining data from multiple files. Each strategy defines how files should be merged into a single dictionary.

## Available Strategies

### Deep Merge Strategy

Recursively merges dictionaries, combining nested structures.

```python
from yapfm.multi_file.strategies import MergeStrategy

# Using enum
strategy = MergeStrategy.DEEP

# Using string
strategy = "deep"
```

**Behavior:**
- Recursively merges nested dictionaries
- Preserves all values from all files
- Later files override earlier files for conflicting keys
- Arrays are replaced (not merged)

**Example:**
```python
# File 1: base.json
{
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "logging": {
        "level": "INFO"
    }
}

# File 2: override.json
{
    "database": {
        "host": "prod-server",
        "ssl": true
    },
    "api": {
        "version": "v2"
    }
}

# Result after deep merge
{
    "database": {
        "host": "prod-server",  # Overridden
        "port": 5432,           # Preserved
        "ssl": true             # Added
    },
    "logging": {
        "level": "INFO"         # Preserved
    },
    "api": {
        "version": "v2"         # Added
    }
}
```

### Namespace Merge Strategy

Merges files into separate namespaces based on file names.

```python
strategy = MergeStrategy.NAMESPACE
```

**Parameters:**
- `namespace_prefix` (str): Prefix for namespaces (default: file name without extension)

**Behavior:**
- Each file becomes a separate namespace
- File names are used as namespace keys
- No conflicts between files

**Example:**
```python
# File: database.json
{
    "host": "localhost",
    "port": 5432
}

# File: api.json
{
    "version": "v2",
    "timeout": 30
}

# Result with namespace merge
{
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "api": {
        "version": "v2",
        "timeout": 30
    }
}
```

### Priority Merge Strategy

Merges files with priority-based overwriting.

```python
strategy = MergeStrategy.PRIORITY
```

**Parameters:**
- `priorities` (Dict[str, int]): File priorities (higher number = higher priority)

**Behavior:**
- Files with higher priority override lower priority files
- Priority is determined by file order or explicit priorities
- Only conflicting keys are overridden

**Example:**
```python
# File 1: base.json (priority: 1)
{
    "database": {
        "host": "localhost",
        "port": 5432
    }
}

# File 2: prod.json (priority: 2)
{
    "database": {
        "host": "prod-server"
    }
}

# Result: prod.json overrides base.json for conflicting keys
{
    "database": {
        "host": "prod-server",  # Overridden by higher priority
        "port": 5432            # Preserved from base
    }
}
```

### Append Merge Strategy

Appends values to lists instead of replacing them.

```python
strategy = MergeStrategy.APPEND
```

**Behavior:**
- Arrays are concatenated instead of replaced
- Dictionaries are merged normally
- Useful for collecting values from multiple sources

**Example:**
```python
# File 1: servers.json
{
    "servers": ["server1", "server2"],
    "config": {
        "timeout": 30
    }
}

# File 2: more_servers.json
{
    "servers": ["server3", "server4"],
    "config": {
        "retries": 3
    }
}

# Result: arrays are appended
{
    "servers": ["server1", "server2", "server3", "server4"],
    "config": {
        "timeout": 30,
        "retries": 3
    }
}
```

### Replace Merge Strategy

Completely replaces data with the last file.

```python
strategy = MergeStrategy.REPLACE
```

**Behavior:**
- Each file completely replaces the previous data
- Only the last file's data is kept
- Useful for configuration overrides

**Example:**
```python
# File 1: base.json
{
    "database": {"host": "localhost"},
    "logging": {"level": "INFO"}
}

# File 2: override.json
{
    "database": {"host": "prod-server"}
}

# Result: only override.json data is kept
{
    "database": {"host": "prod-server"}
}
```

### Conditional Merge Strategy

Merges files based on conditions.

```python
strategy = MergeStrategy.CONDITIONAL
```

**Parameters:**
- `condition_func` (Callable): Function that determines if a file should be merged
- `condition_args` (Dict): Arguments passed to the condition function

**Behavior:**
- Only files that meet the condition are merged
- Condition function receives file path and data
- Useful for environment-specific configurations

**Example:**
```python
def is_production_file(file_path, data):
    return "prod" in str(file_path) or data.get("environment") == "production"

# Only production files will be merged
strategy = MergeStrategy.CONDITIONAL
condition_func = is_production_file
```

## Using Merge Strategies

### With MultiFileMixin

```python
from yapfm import YAPFileManager

fm = YAPFileManager("config.json")

# Load multiple files with deep merge
data = fm.load_multiple_files([
    "base.json",
    "override.json"
], strategy="deep")

# Load with namespace strategy
data = fm.load_multiple_files([
    "database.json",
    "api.json"
], strategy="namespace", namespace_prefix="app")

# Load with priority strategy
data = fm.load_multiple_files([
    "base.json",
    "prod.json"
], strategy="priority", priorities={"prod.json": 2, "base.json": 1})
```

### With File Groups

```python
# Define file groups in configuration
config = {
    "app_config": {
        "files": ["base.json", "override.json"],
        "strategy": "deep"
    },
    "environment_config": {
        "files": ["dev.json", "prod.json"],
        "strategy": "namespace",
        "namespace_prefix": "env"
    }
}

# Load file groups
app_data = fm.load_file_group("app_config", config)
env_data = fm.load_file_group("environment_config", config)
```

### Custom Merge Strategies

You can create custom merge strategies by extending `BaseMergeStrategy`:

```python
from yapfm.multi_file.merge_strategies.base import BaseMergeStrategy

class CustomMergeStrategy(BaseMergeStrategy):
    def merge(self, file_data: List[Tuple[Path, Dict[str, Any]]]) -> Dict[str, Any]:
        # Custom merge logic
        result = {}
        for file_path, data in file_data:
            # Your custom merge logic here
            result.update(data)
        return result

# Use custom strategy
strategy = CustomMergeStrategy()
data = fm.load_multiple_files(["file1.json", "file2.json"], strategy=strategy)
```

## Strategy Selection Guidelines

- **Deep Merge**: Best for configuration files that need to be layered
- **Namespace**: Best for organizing different types of configuration
- **Priority**: Best when you have clear precedence rules
- **Append**: Best for collecting lists from multiple sources
- **Replace**: Best for complete configuration overrides
- **Conditional**: Best for environment-specific or dynamic configurations
