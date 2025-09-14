# Strategies

## BaseFileStrategy

Abstract base protocol for all file handling strategies.

```python
from yapfm.strategies import BaseFileStrategy
```

### Methods

#### load

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

#### save

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

#### navigate

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

## JsonStrategy

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

## TomlStrategy

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

## YamlStrategy

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
