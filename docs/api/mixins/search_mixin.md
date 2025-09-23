# SearchMixin

Provides search functionality for the file manager. The SearchMixin contains operations for finding keys, values, and searching content.

## Methods

### find_key

```python
def find_key(self, pattern: str, use_wildcards: bool = True) -> List[str]
```

Find all keys matching a pattern.

**Parameters:**
- `pattern` (str): Search pattern (supports wildcards like *, ?, [])
- `use_wildcards` (bool): If True, uses fnmatch wildcards, otherwise simple substring search

**Returns:**
- `List[str]`: List of matching keys

**Example:**
```python
# Search with wildcards
keys = fm.find_key("database.*")  # Find database.host, database.port
keys = fm.find_key("api.v[0-9]*")  # Find api.v1, api.v2, etc.

# Simple substring search
keys = fm.find_key("host", use_wildcards=False)
```

### find_value

```python
def find_value(self, value: Any, deep: bool = True) -> List[str]
```

Find all keys containing a specific value.

**Parameters:**
- `value` (Any): Value to search for
- `deep` (bool): If True, searches recursively in nested structures

**Returns:**
- `List[str]`: List of keys containing the value

**Example:**
```python
# Value search
keys = fm.find_value("localhost")  # Find all keys with "localhost"
keys = fm.find_value(5432)  # Find all keys with port 5432
```

### search_in_values

```python
def search_in_values(self, query: str, case_sensitive: bool = True) -> List[tuple]
```

Search for text in string values.

**Parameters:**
- `query` (str): Text to search for
- `case_sensitive` (bool): Whether search should be case sensitive

**Returns:**
- `List[tuple]`: List of tuples (key, value) containing the query

**Example:**
```python
# Search in values
results = fm.search_in_values("localhost")  # Find all string values containing "localhost"
results = fm.search_in_values("API", case_sensitive=False)  # Case insensitive search

for key, value in results:
    print(f"Key: {key}, Value: {value}")
```
