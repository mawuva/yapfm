# Core Classes

## YAPFileManager

The main class that combines all functionality through mixins.

```python
from yapfm import YAPFileManager
```

### Constructor

```python
YAPFileManager(
    path: Union[str, Path],
    strategy: Optional[BaseFileStrategy] = None,
    *,
    auto_create: bool = False,
    enable_context: bool = True,
    enable_cache: bool = True,
    cache_size: int = 1000,
    cache_ttl: Optional[float] = 3600,
    enable_streaming: bool = False,
    enable_lazy_loading: bool = False,
    **kwargs: Any
) -> None
```

**Parameters:**
- `path` (Union[str, Path]): Path to the file to manage
- `strategy` (Optional[BaseFileStrategy]): Custom strategy for file handling. If None, auto-detects based on file extension
- `auto_create` (bool): Whether to create the file if it doesn't exist. Default: False
- `enable_context` (bool): Enable context manager functionality. Default: True
- `enable_cache` (bool): Enable intelligent caching. Default: True
- `cache_size` (int): Maximum number of keys to cache. Default: 1000
- `cache_ttl` (Optional[float]): Cache time-to-live in seconds. Default: 3600 (1 hour)
- `enable_streaming` (bool): Enable streaming for large files. Default: False
- `enable_lazy_loading` (bool): Enable lazy loading for sections. Default: False
- `**kwargs` (Any): Additional keyword arguments passed to mixins

**Example:**
```python
# Basic usage
fm = YAPFileManager("config.json")

# With auto-creation
fm = YAPFileManager("config.json", auto_create=True)

# With custom strategy
from yapfm.strategies import JsonStrategy
fm = YAPFileManager("config.json", strategy=JsonStrategy())

# With advanced features
fm = YAPFileManager(
    "large_config.json",
    enable_cache=True,
    cache_size=2000,
    cache_ttl=7200,  # 2 hours
    enable_streaming=True,
    enable_lazy_loading=True
)
```

### Properties

#### data

```python
@property
data -> Dict[str, Any]
```

Get or set the file data. Automatically loads the file on first access if not loaded.

**Getter:**
- Returns: Dictionary containing the file data
- Note: Automatically loads the file on first access if it hasn't been loaded yet

**Setter:**
- Parameters: `value` (Dict[str, Any]): Dictionary containing the data to set
- Raises: `TypeError` if value is not a dictionary

**Example:**
```python
# Get data (auto-loads if needed)
data = fm.data

# Set data
fm.data = {"key": "value"}
```

### Unified API Methods

YAPFileManager provides a simplified, unified API that delegates to the appropriate mixins:

#### Basic Operations

```python
def set(key: str, value: Any, overwrite: bool = True) -> None
def get(key: str, default: Any = None) -> Any
def has(key: str) -> bool
def delete(key: str) -> bool
```

**Example:**
```python
# Set a value
fm.set("database.host", "localhost")

# Get a value
host = fm.get("database.host", "localhost")

# Check if key exists
if fm.has("database.host"):
    print("Database host is configured")

# Delete a key
fm.delete("database.host")
```

#### Dictionary-like Interface

YAPFileManager supports dictionary-like syntax for seamless integration:

```python
# Dictionary-like access
fm["database.host"] = "localhost"
host = fm["database.host"]
"database.host" in fm
del fm["database.host"]

# Dictionary methods
for key in fm:  # Iterate over keys
    print(key)

for key, value in fm.items():  # Iterate over items
    print(f"{key}: {value}")

# Other dict methods
fm.update({"new.key": "value"})
fm.clear()
value = fm.pop("key", "default")
```

#### Batch Operations

Efficient operations for handling multiple keys at once:

```python
def set_multiple(items: Dict[str, Any], overwrite: bool = True) -> None
def get_multiple(keys: List[str], default: Any = None, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
def delete_multiple(keys: List[str]) -> int
def has_multiple(keys: List[str]) -> Dict[str, bool]
```

**Example:**
```python
# Set multiple values efficiently
fm.set_multiple({
    "database.host": "localhost",
    "database.port": 5432,
    "logging.level": "INFO"
})

# Get multiple values
values = fm.get_multiple(["database.host", "database.port"])

# Get multiple values with specific defaults
values = fm.get_multiple(
    ["database.host", "database.port"],
    defaults={"database.host": "localhost", "database.port": 5432}
)

# Check existence of multiple keys
exists = fm.has_multiple(["database.host", "database.port"])
# Returns: {"database.host": True, "database.port": False}

# Delete multiple keys
deleted_count = fm.delete_multiple(["database.host", "database.port"])
```

#### Cache Management

```python
def get_cache_stats() -> Dict[str, Any]
def clear_key_cache() -> None
```

**Example:**
```python
# Get comprehensive cache statistics
stats = fm.get_cache_stats()
print(f"Cache hits: {stats['unified_cache']['hits']}")
print(f"Cache misses: {stats['unified_cache']['misses']}")
print(f"Lazy sections: {stats['lazy_sections']['total_sections']}")

# Clear key generation cache
fm.clear_key_cache()
```

### Advanced Features

All advanced functionality is available through mixins. See [Mixins](mixins/index.md) section for detailed documentation:

- **File Operations**: Basic file management (load, save, exists, etc.)
- **Key Operations**: Dot notation access and manipulation
- **Section Operations**: Section-based data management
- **Context Management**: Automatic loading/saving with context managers
- **Batch Operations**: Efficient multi-key operations
- **Caching**: Intelligent caching with TTL and LRU eviction
- **Lazy Loading**: Memory-efficient section loading
- **Streaming**: Large file processing capabilities
- **Multi-File**: Multiple file loading and merging
- **Search**: Key and value searching
- **Analysis**: Data analysis and statistics
- **Transform**: Data transformation and restructuring
- **Cleanup**: Data cleanup and optimization
- **Clone**: Data cloning and copying
- **Export**: Export to different formats
- **Security**: Sensitive data handling and masking

## FileManagerProxy

Proxy wrapper that adds logging, metrics, and auditing capabilities.

```python
from yapfm import FileManagerProxy
```

### Constructor

```python
FileManagerProxy(
    manager: Any,
    *,
    enable_logging: bool = False,
    enable_metrics: bool = False,
    enable_audit: bool = False,
    logger: Optional[logging.Logger] = None,
    audit_hook: Optional[Callable[[str, tuple, dict, Any], None]] = None
) -> None
```

**Parameters:**
- `manager` (Any): The underlying FileManager instance to proxy
- `enable_logging` (bool): Enable debug logging of method calls and results. Default: False
- `enable_metrics` (bool): Enable execution time measurement. Default: False
- `enable_audit` (bool): Enable audit hook execution. Default: False
- `logger` (Optional[logging.Logger]): Custom logger. Defaults to `logging.getLogger(__name__)`
- `audit_hook` (Optional[Callable]): Custom hook called as `audit_hook(method: str, args: tuple, kwargs: dict, result: Any)`

**Example:**
```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Create file manager
fm = YAPFileManager("config.json")

# Create proxy with logging and metrics
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True
)

# Use proxy like the original manager
with proxy:
    proxy.set_key("value", dot_key="key")
```
