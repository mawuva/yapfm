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

### Methods

All methods from the mixins are available. See [Mixins](mixins.md) section for detailed documentation.

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
