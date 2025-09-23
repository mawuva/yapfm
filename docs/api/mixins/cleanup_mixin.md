# CleanupMixin

Provides cleanup functionality for the file manager. The CleanupMixin contains operations for cleaning empty sections, removing nulls, and compacting data.

## Methods

### clean_empty_sections

```python
def clean_empty_sections(self) -> int
```

Remove empty sections from the data.

**Returns:**
- `int`: Number of empty sections removed

**Example:**
```python
removed = fm.clean_empty_sections()
print(f"Removed {removed} empty sections")
```

### remove_nulls

```python
def remove_nulls(self) -> int
```

Remove null/None values from the data.

**Returns:**
- `int`: Number of null values removed

**Example:**
```python
removed = fm.remove_nulls()
print(f"Removed {removed} null values")
```

### compact

```python
def compact(self) -> Dict[str, int]
```

Optimize the data structure by removing empty sections and nulls.

**Returns:**
- `Dict[str, int]`: Dictionary with counts of operations performed

**Example:**
```python
result = fm.compact()
print(f"Removed {result['empty_sections']} empty sections and {result['nulls']} nulls")
print(f"Total operations: {result['total_operations']}")
```
