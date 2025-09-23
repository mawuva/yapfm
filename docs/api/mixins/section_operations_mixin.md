# SectionOperationsMixin

Provides section-based data management.

## Methods

### set_section

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

### get_section

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

### has_section

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

### delete_section

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
