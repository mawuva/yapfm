# Helpers

## split_dot_key

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

## navigate_dict_like

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

## load_file

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

## save_file

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

## open_file

Open a configuration file with the appropriate strategy.

```python
from yapfm.helpers import open_file
```

**Parameters:**
- `path` (Union[str, Path]): Path to the file
- `format` (Optional[str]): Optional format override (e.g. "toml", "json", "yaml"). If provided, will select the strategy based on this format instead of the file extension
- `auto_create` (bool): Whether to create the file if it doesn't exist. Default: False

**Returns:**
- `YAPFileManager`: File manager instance configured for the specified file

**Example:**
```python
# Open file with automatic format detection
fm = open_file("config.json")

# Open file with format override
fm = open_file("config.txt", format="toml")

# Open file with auto-creation
fm = open_file("new_config.json", auto_create=True)

# Use the file manager
with fm:
    fm.set_key("value", dot_key="key")
```

## load_file_with_stream

Load a file using a custom loader function with stream support.

```python
from yapfm.helpers import load_file_with_stream
```

**Parameters:**
- `file_path` (Union[Path, str]): Path to the file
- `parser_func` (Callable[[Any], T]): Function to parse the file stream

**Returns:**
- `T`: Parsed file content

**Example:**
```python
import json

def parse_json_stream(stream):
    return json.load(stream)

data = load_file_with_stream("large_config.json", parse_json_stream)
```

## save_file_with_stream

Save data to a file using a custom writer function with stream support.

```python
from yapfm.helpers import save_file_with_stream
```

**Parameters:**
- `file_path` (Union[Path, str]): Path to save the file
- `data` (Any): Data to save
- `writer_func` (Callable[[Any, Any], None]): Function to write data to stream

**Example:**
```python
import json

def write_json_stream(data, stream):
    json.dump(data, stream, indent=2)

save_file_with_stream("output.json", data, write_json_stream)
```

## join_dot_key

Join a path and key name into a dot-separated key.

```python
from yapfm.helpers import join_dot_key
```

**Parameters:**
- `path` (List[str]): The path components
- `key_name` (str): The key name

**Returns:**
- `str`: The dot-separated key

**Example:**
```python
key = join_dot_key(["database", "connection"], "host")
print(key)  # "database.connection.host"
```

## resolve_file_extension

Resolve file extension from a file path or extension string.

```python
from yapfm.helpers import resolve_file_extension
```

**Parameters:**
- `file_ext_or_path` (str): File path or extension string

**Returns:**
- `str`: The resolved file extension

**Example:**
```python
ext = resolve_file_extension("config.json")  # ".json"
ext = resolve_file_extension(".toml")        # ".toml"
```

## deep_merge

Deep merge two dictionaries.

```python
from yapfm.helpers import deep_merge
```

**Parameters:**
- `dict1` (Dict[str, Any]): First dictionary
- `dict2` (Dict[str, Any]): Second dictionary

**Returns:**
- `Dict[str, Any]`: Merged dictionary

**Example:**
```python
base = {"database": {"host": "localhost"}}
override = {"database": {"port": 5432}}
merged = deep_merge(base, override)
# Result: {"database": {"host": "localhost", "port": 5432}}
```

## traverse_data_structure

Traverse a data structure and apply a function to each element.

```python
from yapfm.helpers import traverse_data_structure
```

**Parameters:**
- `data` (Any): The data structure to traverse
- `path` (str): The current path
- `visitor_func` (Callable[[Any, str], None]): Function to apply to each element
- `include_containers` (bool): Whether to include containers in traversal

**Example:**
```python
def print_paths(value, path):
    print(f"{path}: {value}")

traverse_data_structure(data, "", print_paths)
```

## transform_data_in_place

Transform data in place using a transformation function.

```python
from yapfm.helpers import transform_data_in_place
```

**Parameters:**
- `data` (Any): The data to transform
- `transformer_func` (Callable): Function to transform values
- `target` (str): What to transform ("key", "value", or "both")
- `deep` (bool): Whether to transform recursively

**Example:**
```python
def uppercase_strings(value):
    return value.upper() if isinstance(value, str) else value

transform_data_in_place(data, uppercase_strings, "value", deep=True)
```

## validate_strategy

Validate that a strategy implements the required interface.

```python
from yapfm.helpers import validate_strategy
```

**Parameters:**
- `strategy` (BaseFileStrategy): The strategy to validate

**Raises:**
- `ValueError`: If the strategy is invalid

**Example:**
```python
from yapfm.strategies import JsonStrategy

strategy = JsonStrategy()
validate_strategy(strategy)  # Validates the strategy
```