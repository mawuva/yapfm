# TransformMixin

Provides transformation functionality for the file manager. The TransformMixin contains operations for flattening, unflattening, and transforming data.

## Methods

### flatten

```python
def flatten(self, separator: str = ".") -> Dict[str, Any]
```

Flatten the structure into a single-level dictionary.

**Parameters:**
- `separator` (str): Separator to use for nested keys

**Returns:**
- `Dict[str, Any]`: Flattened dictionary

**Example:**
```python
flat = fm.flatten()
print(flat)  # {'database.host': 'localhost', 'database.port': 5432}

# With custom separator
flat = fm.flatten(separator="_")
print(flat)  # {'database_host': 'localhost', 'database_port': 5432}
```

### unflatten

```python
def unflatten(self, separator: str = ".") -> Dict[str, Any]
```

Reconstruct nested structure from flattened data.

**Parameters:**
- `separator` (str): Separator used in flattened keys

**Returns:**
- `Dict[str, Any]`: Nested dictionary

**Example:**
```python
# Flatten then unflatten
flat_data = fm.flatten()
nested = fm.unflatten()

# With custom separator
flat_data = fm.flatten(separator="_")
nested = fm.unflatten(separator="_")
```

### transform_values

```python
def transform_values(
    self, 
    transformer_func: Callable[[Any], Any], 
    deep: bool = True
) -> None
```

Transform all values using a function.

**Parameters:**
- `transformer_func` (Callable[[Any], Any]): Function to transform values
- `deep` (bool): If True, transforms recursively in nested structures

**Example:**
```python
# Convert all strings to uppercase
fm.transform_values(lambda x: x.upper() if isinstance(x, str) else x)

# Multiply all integers by 2
fm.transform_values(lambda x: x * 2 if isinstance(x, int) else x)

# Type conversion
fm.transform_values(lambda x: str(x) if isinstance(x, (int, float)) else x)
```

### transform_keys

```python
def transform_keys(
    self, 
    transformer_func: Callable[[str], str], 
    deep: bool = True
) -> None
```

Transform all keys using a function.

**Parameters:**
- `transformer_func` (Callable[[str], str]): Function to transform keys
- `deep` (bool): If True, transforms recursively in nested structures

**Example:**
```python
# Convert all keys to uppercase
fm.transform_keys(str.upper)

# Replace underscores with dashes
fm.transform_keys(lambda k: k.replace('_', '-'))

# Add prefix
fm.transform_keys(lambda k: f"app_{k}")

# Convert snake_case to camelCase
def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

fm.transform_keys(snake_to_camel)
```
