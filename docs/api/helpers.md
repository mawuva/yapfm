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
