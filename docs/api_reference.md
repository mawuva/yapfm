# API Reference

Complete API documentation for YAPFM, including all classes, methods, and their parameters.

## 📚 Table of Contents

1. [Core Classes](#core-classes)
2. [Strategies](#strategies)
3. [Mixins](#mixins)
4. [Registry](#registry)
5. [Proxy](#proxy)
6. [Exceptions](#exceptions)
7. [Helpers](#helpers)

## 🏗️ Core Classes

### YAPFileManager

The main class that combines all functionality through mixins.

```python
from yapfm import YAPFileManager
```

#### Constructor

```python
YAPFileManager(
    path: Union[str, Path],
    strategy: Optional[BaseFileStrategy] = None,
    *,
    auto_create: bool = False,
    **kwargs: Any
) -> None
```

**Parameters:**
- `path` (Union[str, Path]): Path to the file to manage
- `strategy` (Optional[BaseFileStrategy]): Custom strategy for file handling. If None, auto-detects based on file extension
- `auto_create` (bool): Whether to create the file if it doesn't exist. Default: False
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
```

#### Properties

##### data

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

#### Methods

All methods from the mixins are available. See [Mixins](#mixins) section for detailed documentation.

### FileManagerProxy

Proxy wrapper that adds logging, metrics, and auditing capabilities.

```python
from yapfm import FileManagerProxy
```

#### Constructor

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

## 🎯 Strategies

### BaseFileStrategy

Abstract base protocol for all file handling strategies.

```python
from yapfm.strategies import BaseFileStrategy
```

#### Methods

##### load

```python
def load(self, file_path: Union[Path, str]) -> Any
```

Load data from a file.

**Parameters:**
- `file_path` (Union[Path, str]): Path to the file to load

**Returns:**
- `Any`: The parsed file contents, typically a dictionary or list

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `ValueError`: If the file format is invalid

**Example:**
```python
strategy = TomlStrategy()
data = strategy.load("config.toml")
print(data["database"]["host"])
```

##### save

```python
def save(self, file_path: Union[Path, str], data: Any) -> None
```

Save data to a file.

**Parameters:**
- `file_path` (Union[Path, str]): Path where to save the file
- `data` (Any): The data to save, typically a dictionary or list

**Raises:**
- `PermissionError`: If the file cannot be written due to permissions
- `ValueError`: If the data cannot be serialized to the target format

**Example:**
```python
strategy = TomlStrategy()
data = {"database": {"host": "localhost", "port": 5432}}
strategy.save("config.toml", data)
```

##### navigate

```python
def navigate(
    self, 
    document: Any, 
    path: List[str], 
    create: bool = False
) -> Optional[Any]
```

Navigate through the document structure.

**Parameters:**
- `document` (Any): The document to navigate through
- `path` (List[str]): List of keys representing the path to traverse
- `create` (bool): Whether to create missing intermediate structures

**Returns:**
- `Optional[Any]`: The value at the specified path, or None if not found and create is False

**Example:**
```python
strategy = TomlStrategy()
document = {"database": {"host": "localhost"}}
value = strategy.navigate(document, ["database", "host"])
print(value)  # "localhost"

# Create missing path
value = strategy.navigate(document, ["cache", "redis"], create=True)
print(document)  # {"database": {...}, "cache": {"redis": None}}
```

### JsonStrategy

Strategy for handling JSON files.

```python
from yapfm.strategies import JsonStrategy
```

**Features:**
- Standard JSON with pretty printing
- 2-space indentation
- UTF-8 encoding support

**Example:**
```python
strategy = JsonStrategy()
data = strategy.load("config.json")
strategy.save("output.json", data)
```

### TomlStrategy

Strategy for handling TOML files.

```python
from yapfm.strategies import TomlStrategy
```

**Features:**
- Full TOML specification support
- Comment and formatting preservation
- Type-safe operations with tomlkit
- Support for nested tables and arrays

**Example:**
```python
strategy = TomlStrategy()
data = strategy.load("config.toml")
strategy.save("output.toml", data)
```

### YamlStrategy

Strategy for handling YAML files.

```python
from yapfm.strategies import YamlStrategy
```

**Features:**
- YAML 1.2 with safe loading
- UTF-8 encoding support
- Pretty printing with proper indentation

**Example:**
```python
strategy = YamlStrategy()
data = strategy.load("config.yaml")
strategy.save("output.yaml", data)
```

## 🔧 Mixins

### FileOperationsMixin

Provides basic file operations.

#### Methods

##### exists

```python
def exists(self) -> bool
```

Check if the file exists.

**Returns:**
- `bool`: True if the file exists, False otherwise

**Example:**
```python
if fm.exists():
    print("File exists")
```

##### is_dirty

```python
def is_dirty(self) -> bool
```

Check if the file is dirty (has unsaved changes).

**Returns:**
- `bool`: True if the file has unsaved changes, False otherwise

**Example:**
```python
if fm.is_dirty():
    print("File has unsaved changes")
```

##### is_loaded

```python
def is_loaded(self) -> bool
```

Check if the file is loaded in memory.

**Returns:**
- `bool`: True if the file is loaded, False otherwise

**Example:**
```python
if fm.is_loaded():
    print("File is loaded in memory")
```

##### load

```python
def load(self) -> None
```

Load data from the file.

**Raises:**
- `FileNotFoundError`: If the file doesn't exist and auto_create is False
- `ValueError`: If the file format is invalid or corrupted
- `LoadFileError`: If there's an error during the loading process

**Example:**
```python
fm.load()  # Loads the file content into memory
```

##### save

```python
def save(self) -> None
```

Save data to the file.

**Raises:**
- `PermissionError`: If the file cannot be written due to permissions
- `ValueError`: If the data format is invalid for the file type
- `FileWriteError`: If there's an error during the writing process

**Example:**
```python
fm.save()  # Saves the current data to disk
```

##### save_if_dirty

```python
def save_if_dirty(self) -> None
```

Save the file only if it has been modified.

**Example:**
```python
fm.save_if_dirty()  # Only saves if there are unsaved changes
```

##### reload

```python
def reload(self) -> None
```

Reload data from the file, discarding any unsaved changes.

**Example:**
```python
fm.reload()  # Reloads from disk, discards unsaved changes
```

##### mark_as_dirty

```python
def mark_as_dirty(self) -> None
```

Mark the file as dirty (has unsaved changes).

**Example:**
```python
fm.mark_as_dirty()  # Mark as having unsaved changes
```

##### mark_as_clean

```python
def mark_as_clean(self) -> None
```

Mark the file as clean (no unsaved changes).

**Example:**
```python
fm.mark_as_clean()  # Mark as clean
```

##### mark_as_loaded

```python
def mark_as_loaded(self) -> None
```

Mark the file as loaded in memory.

**Example:**
```python
fm.mark_as_loaded()  # Mark as loaded
```

##### unload

```python
def unload(self) -> None
```

Unload the file from memory.

**Example:**
```python
fm.unload()  # Free memory
```

##### create_empty_file

```python
def create_empty_file(self) -> None
```

Create an empty file.

**Example:**
```python
fm.create_empty_file()  # Creates empty file
```

##### load_if_not_loaded

```python
def load_if_not_loaded(self) -> None
```

Load the file if it is not loaded.

**Example:**
```python
fm.load_if_not_loaded()  # Load only if not already loaded
```

### KeyOperationsMixin

Provides key-based data access with dot notation.

#### Methods

##### set_key

```python
def set_key(
    self,
    value: Any,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    overwrite: bool = True
) -> None
```

Set a value in the file using dot notation.

**Parameters:**
- `value` (Any): The value to set
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key
- `overwrite` (bool): Whether to overwrite the existing value. Default: True

**Example:**
```python
# Using dot notation
fm.set_key("localhost", dot_key="database.host")

# Using path and key name
fm.set_key(5432, path=["database"], key_name="port")

# Only set if key doesn't exist
fm.set_key("default", dot_key="database.host", overwrite=False)
```

##### get_key

```python
def get_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None,
    default: Any = None
) -> Any
```

Get a value from the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key
- `default` (Any): The default value if the key is not found

**Returns:**
- `Any`: The value at the specified path or default

**Example:**
```python
# Using dot notation
host = fm.get_key(dot_key="database.host", default="localhost")

# Using path and key name
port = fm.get_key(path=["database"], key_name="port", default=5432)
```

##### has_key

```python
def has_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None
) -> bool
```

Check if a key exists in the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key

**Returns:**
- `bool`: True if the key exists, False otherwise

**Example:**
```python
# Using dot notation
if fm.has_key(dot_key="database.host"):
    print("Database host exists")

# Using path and key name
if fm.has_key(path=["database"], key_name="port"):
    print("Database port exists")
```

##### delete_key

```python
def delete_key(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    key_name: Optional[str] = None
) -> bool
```

Delete a key from the file using dot notation.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key
- `path` (Optional[List[str]]): The path to the key
- `key_name` (Optional[str]): The name of the key

**Returns:**
- `bool`: True if the key was deleted, False if it didn't exist

**Example:**
```python
# Using dot notation
deleted = fm.delete_key(dot_key="database.host")

# Using path and key name
deleted = fm.delete_key(path=["database"], key_name="port")
```

### SectionOperationsMixin

Provides section-based data management.

#### Methods

##### set_section

```python
def set_section(
    self,
    section_data: Dict[str, Any],
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None,
    overwrite: bool = True
) -> None
```

Set an entire section in the file.

**Parameters:**
- `section_data` (Dict[str, Any]): The section data to set
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section
- `overwrite` (bool): Whether to overwrite the existing section. Default: True

**Example:**
```python
# Using dot notation
fm.set_section({
    "host": "localhost",
    "port": 5432,
    "ssl": True
}, dot_key="database")

# Using path and section name
fm.set_section({
    "version": "v1",
    "timeout": 30
}, path=["api"], section_name="config")
```

##### get_section

```python
def get_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None,
    default: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]
```

Get an entire section from the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section
- `default` (Optional[Dict[str, Any]]): The default value if the section is not found

**Returns:**
- `Optional[Dict[str, Any]]`: The section data or default

**Example:**
```python
# Using dot notation
db_config = fm.get_section(dot_key="database")

# Using path and section name
api_config = fm.get_section(path=["api"], section_name="config")
```

##### has_section

```python
def has_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None
) -> bool
```

Check if a section exists in the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section

**Returns:**
- `bool`: True if the section exists, False otherwise

**Example:**
```python
# Using dot notation
if fm.has_section(dot_key="database"):
    print("Database section exists")

# Using path and section name
if fm.has_section(path=["api"], section_name="config"):
    print("API config section exists")
```

##### delete_section

```python
def delete_section(
    self,
    dot_key: Optional[str] = None,
    *,
    path: Optional[List[str]] = None,
    section_name: Optional[str] = None
) -> bool
```

Delete an entire section from the file.

**Parameters:**
- `dot_key` (Optional[str]): The dot-separated key for the section
- `path` (Optional[List[str]]): The path to the section
- `section_name` (Optional[str]): The name of the section

**Returns:**
- `bool`: True if the section was deleted, False if it didn't exist

**Example:**
```python
# Using dot notation
deleted = fm.delete_section(dot_key="database")

# Using path and section name
deleted = fm.delete_section(path=["api"], section_name="config")
```

### ContextMixin

Provides context manager functionality.

#### Methods

##### __enter__

```python
def __enter__(self) -> Self
```

Enter the context manager and load the file.

**Returns:**
- `Self`: The file manager instance

**Example:**
```python
with YAPFileManager("config.json") as fm:
    # File is automatically loaded
    fm.set_key("value", dot_key="key")
```

##### __exit__

```python
def __exit__(self, exc_type, exc_val, exc_tb) -> None
```

Exit the context manager and save if dirty.

**Parameters:**
- `exc_type`: Exception type
- `exc_val`: Exception value
- `exc_tb`: Exception traceback

**Example:**
```python
with YAPFileManager("config.json") as fm:
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting context
```

##### lazy_save

```python
@contextmanager
def lazy_save(self, save_on_exit: bool = True) -> Iterator[Self]
```

Context manager for lazy saving.

**Parameters:**
- `save_on_exit` (bool): Whether to save when exiting the context. Default: True

**Returns:**
- `Iterator[Self]`: The file manager instance

**Example:**
```python
with fm.lazy_save():
    fm.set_key("value1", dot_key="key1")
    fm.set_key("value2", dot_key="key2")
    # Save happens here when exiting lazy_save context
```

##### auto_save

```python
@contextmanager
def auto_save(self, save_on_exit: bool = True) -> Iterator[Self]
```

Context manager for automatic saving.

**Parameters:**
- `save_on_exit` (bool): Whether to save when exiting the context. Default: True

**Returns:**
- `Iterator[Self]`: The file manager instance

**Example:**
```python
with fm.auto_save():
    fm.set_key("value", dot_key="key")
    # Save happens here when exiting auto_save context
```

## 📋 Registry

### FileStrategyRegistry

Registry for managing file strategies.

```python
from yapfm.registry import FileStrategyRegistry
```

#### Class Methods

##### register_strategy

```python
@classmethod
def register_strategy(
    cls,
    file_exts: Union[str, List[str]],
    strategy_cls: Type[BaseFileStrategy]
) -> None
```

Register one or multiple extensions for a strategy class.

**Parameters:**
- `file_exts` (Union[str, List[str]]): File extension(s) to register the strategy for
- `strategy_cls` (Type[BaseFileStrategy]): Strategy class to register

**Raises:**
- `TypeError`: If the strategy does not inherit from BaseFileStrategy

**Example:**
```python
from yapfm.strategies import JsonStrategy

# Register single extension
FileStrategyRegistry.register_strategy(".json", JsonStrategy)

# Register multiple extensions
FileStrategyRegistry.register_strategy([".json", ".jsonc"], JsonStrategy)
```

##### unregister_strategy

```python
@classmethod
def unregister_strategy(cls, file_ext: str) -> None
```

Unregister a strategy for a file extension.

**Parameters:**
- `file_ext` (str): File extension to unregister the strategy for

**Example:**
```python
FileStrategyRegistry.unregister_strategy(".json")
```

##### get_strategy

```python
@classmethod
def get_strategy(cls, file_ext_or_path: str) -> Optional[BaseFileStrategy]
```

Get a strategy for a file extension or path.

**Parameters:**
- `file_ext_or_path` (str): File extension or path to get the strategy for

**Returns:**
- `Optional[BaseFileStrategy]`: The strategy for the file extension or path

**Example:**
```python
# Get strategy by extension
strategy = FileStrategyRegistry.get_strategy(".json")

# Get strategy by path
strategy = FileStrategyRegistry.get_strategy("config.json")
```

##### list_strategies

```python
@classmethod
def list_strategies(cls) -> Dict[str, Type[BaseFileStrategy]]
```

List all registered strategies.

**Returns:**
- `Dict[str, Type[BaseFileStrategy]]`: Dictionary mapping extensions to strategy classes

**Example:**
```python
strategies = FileStrategyRegistry.list_strategies()
print(strategies)  # {'.json': <class 'JsonStrategy'>, '.toml': <class 'TomlStrategy'>}
```

##### get_counters

```python
@classmethod
def get_counters(cls) -> Dict[str, int]
```

Get the counters for all registered strategies.

**Returns:**
- `Dict[str, int]`: Dictionary mapping extensions to usage counts

**Example:**
```python
counters = FileStrategyRegistry.get_counters()
print(counters)  # {'.json': 5, '.toml': 3}
```

##### get_skipped

```python
@classmethod
def get_skipped(cls) -> Dict[str, List[str]]
```

Get the skipped files for all registered strategies.

**Returns:**
- `Dict[str, List[str]]`: Dictionary mapping extensions to lists of skipped files

**Example:**
```python
skipped = FileStrategyRegistry.get_skipped()
print(skipped)  # {'unknown': ['file.xyz']}
```

##### get_supported_formats

```python
@classmethod
def get_supported_formats(cls) -> List[str]
```

Get the supported formats for all registered strategies.

**Returns:**
- `List[str]`: List of supported file extensions

**Example:**
```python
formats = FileStrategyRegistry.get_supported_formats()
print(formats)  # ['.json', '.toml', '.yaml']
```

##### is_format_supported

```python
@classmethod
def is_format_supported(cls, file_ext: str) -> bool
```

Check if a format is supported.

**Parameters:**
- `file_ext` (str): File extension to check

**Returns:**
- `bool`: True if the format is supported, False otherwise

**Example:**
```python
if FileStrategyRegistry.is_format_supported(".json"):
    print("JSON format is supported")
```

##### get_registry_stats

```python
@classmethod
def get_registry_stats(cls) -> Dict[str, Any]
```

Get registry statistics.

**Returns:**
- `Dict[str, Any]`: Registry statistics including counters and skipped files

**Example:**
```python
stats = FileStrategyRegistry.get_registry_stats()
print(stats)  # {'counters': {...}, 'skipped': {...}, 'supported_formats': [...]}
```

##### display_summary

```python
@classmethod
def display_summary(cls) -> None
```

Print a styled summary of counters and skipped files.

**Example:**
```python
FileStrategyRegistry.display_summary()
# Output:
# 🎯 Registered Strategies & Usage Summary
# ----------------------------------------
# .json      -> JsonStrategy         | Used: 5
# .toml      -> TomlStrategy         | Used: 3
```

### register_file_strategy

Decorator to register a strategy for one or more formats.

```python
from yapfm.registry import register_file_strategy
```

#### Usage

```python
@register_file_strategy(".json")
class MyJsonStrategy:
    def load(self, file_path):
        # Implementation
        pass
    
    def save(self, file_path, data):
        # Implementation
        pass
    
    def navigate(self, document, path, create=False):
        # Implementation
        pass
```

**Parameters:**
- `file_exts` (Union[str, List[str]]): The extensions to register the strategy for
- `registry` (Type[FileStrategyRegistry]): The registry to register the strategy for

**Example:**
```python
@register_file_strategy([".json", ".jsonc"])
class MyJsonStrategy:
    # Implementation
    pass
```

## ⚠️ Exceptions

### FileManagerError

Base exception for all file manager errors.

```python
from yapfm.exceptions import FileManagerError
```

### LoadFileError

Raised when there's an error loading a file.

```python
from yapfm.exceptions import LoadFileError
```

**Example:**
```python
try:
    fm.load()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
```

### FileWriteError

Raised when there's an error writing to a file.

```python
from yapfm.exceptions import FileWriteError
```

**Example:**
```python
try:
    fm.save()
except FileWriteError as e:
    print(f"Failed to save file: {e}")
```

### StrategyError

Raised when there's an error with file strategies.

```python
from yapfm.exceptions import StrategyError
```

**Example:**
```python
try:
    fm = YAPFileManager("file.xyz")
except StrategyError as e:
    print(f"Strategy error: {e}")
```

## 🛠️ Helpers

### split_dot_key

Split a dot-separated key into path and key name.

```python
from yapfm.helpers import split_dot_key
```

**Parameters:**
- `dot_key` (str): The dot-separated key

**Returns:**
- `Tuple[List[str], str]`: The path and key name

**Example:**
```python
path, key = split_dot_key("database.host")
print(path)  # ['database']
print(key)   # 'host'
```

### navigate_dict_like

Navigate through a dictionary-like structure.

```python
from yapfm.helpers import navigate_dict_like
```

**Parameters:**
- `document` (Any): The document to navigate
- `path` (List[str]): The path to traverse
- `create` (bool): Whether to create missing intermediate structures

**Returns:**
- `Optional[Any]`: The value at the specified path

**Example:**
```python
document = {"database": {"host": "localhost"}}
value = navigate_dict_like(document, ["database", "host"])
print(value)  # "localhost"
```

### load_file

Load a file using a custom loader function.

```python
from yapfm.helpers import load_file
```

**Parameters:**
- `file_path` (Union[Path, str]): Path to the file
- `loader` (Callable): Function to load the file content

**Returns:**
- `Any`: The loaded file content

**Example:**
```python
import json
data = load_file("config.json", json.loads)
```

### save_file

Save data to a file using a custom serializer.

```python
from yapfm.helpers import save_file
```

**Parameters:**
- `file_path` (Union[Path, str]): Path to save the file
- `data` (Any): Data to save
- `serializer` (Callable): Function to serialize the data

**Example:**
```python
import json
save_file("config.json", data, lambda x: json.dumps(x, indent=2))
```

---

*This API reference covers all public methods and classes in YAPFM. For more examples and usage patterns, see the [Examples Guide](examples.md).*
