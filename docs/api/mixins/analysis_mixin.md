# AnalysisMixin

Provides analysis functionality for the file manager. The AnalysisMixin contains operations for analyzing data structure, types, and statistics.

## Methods

### get_all_keys

```python
def get_all_keys(self, flat: bool = True) -> List[str]
```

Get all keys in the file.

**Parameters:**
- `flat` (bool): If True, returns in dot notation (database.host). If False, returns hierarchical structure

**Returns:**
- `List[str]`: List of keys

**Example:**
```python
# Get keys in dot notation
keys = fm.get_all_keys()  # ['database.host', 'database.port', 'api.version']

# Get hierarchical keys
keys = fm.get_all_keys(flat=False)  # ['database', 'api']
```

### get_stats

```python
def get_stats(self) -> Dict[str, Any]
```

Get comprehensive statistics about the content.

**Returns:**
- `Dict[str, Any]`: Dictionary with detailed statistics

**Example:**
```python
stats = fm.get_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Max depth: {stats['max_depth']}")
print(f"File size: {stats['file_size']} bytes")
print(f"File format: {stats['file_format']}")
print(f"Cache enabled: {stats['cache_enabled']}")
```

### get_type_distribution

```python
def get_type_distribution(self) -> Dict[str, int]
```

Get distribution of data types in the file.

**Returns:**
- `Dict[str, int]`: Dictionary with type counts

**Example:**
```python
types = fm.get_type_distribution()
print(f"Strings: {types['str']}, Numbers: {types['int'] + types['float']}")
```

### get_size_info

```python
def get_size_info(self) -> Dict[str, Any]
```

Get size information about the file and data.

**Returns:**
- `Dict[str, Any]`: Dictionary with size information

**Example:**
```python
size_info = fm.get_size_info()
print(f"File size: {size_info['file_size_bytes']} bytes")
print(f"Memory usage: {size_info['memory_usage_bytes']} bytes")
print(f"Compression ratio: {size_info['compression_ratio']}")
```

### find_duplicates

```python
def find_duplicates(self) -> Dict[Any, List[str]]
```

Find duplicate values and their keys.

**Returns:**
- `Dict[Any, List[str]]`: Dictionary mapping values to lists of keys that contain them

**Example:**
```python
duplicates = fm.find_duplicates()
for value, keys in duplicates.items():
    if len(keys) > 1:
        print(f"Value '{value}' found in: {keys}")
```
