# Registry

## FileStrategyRegistry

Registry for managing file strategies.

```python
from yapfm.registry import FileStrategyRegistry
```

### Class Methods

#### register_strategy

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

#### unregister_strategy

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

#### get_strategy

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

#### list_strategies

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

#### get_counters

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

#### get_skipped

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

#### get_supported_formats

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

#### is_format_supported

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

#### get_registry_stats

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

#### display_summary

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

## register_file_strategy

Decorator to register a strategy for one or more formats.

```python
from yapfm.registry import register_file_strategy
```

### Usage

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
