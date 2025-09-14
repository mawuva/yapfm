# Common Issues

## File Not Found Errors

**Problem**: `FileNotFoundError` when trying to load a file.

**Solutions**:
```python
# 1. Use auto_create=True
fm = YAPFileManager("config.json", auto_create=True)

# 2. Check if file exists first
if fm.exists():
    fm.load()
else:
    print("File does not exist")

# 3. Create the file manually
fm.create_empty_file()
```

## Permission Denied Errors

**Problem**: `PermissionError` when trying to save a file.

**Solutions**:
```python
# 1. Check file permissions
import os
print(f"File permissions: {oct(os.stat('config.json').st_mode)[-3:]}")

# 2. Check directory permissions
print(f"Directory permissions: {oct(os.stat('.').st_mode)[-3:]}")

# 3. Run with appropriate permissions
# On Unix/Linux: chmod 644 config.json
# On Windows: Check file properties
```

## Strategy Not Found Errors

**Problem**: `StrategyError` when trying to use an unsupported file format.

**Solutions**:
```python
# 1. Check supported formats
from yapfm.registry import FileStrategyRegistry
print(f"Supported formats: {FileStrategyRegistry.get_supported_formats()}")

# 2. Register a custom strategy
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy(".xml")
class XmlStrategy:
    def load(self, file_path):
        # Implementation
        pass
    
    def save(self, file_path, data):
        # Implementation
        pass
    
    def navigate(self, document, path, create=False):
        # Implementation
        pass

# 3. Use a supported format
fm = YAPFileManager("config.json")  # Use .json instead of .xml
```

## Data Type Errors

**Problem**: `TypeError` when setting data that's not a dictionary.

**Solutions**:
```python
# 1. Ensure data is a dictionary
data = {"key": "value"}  # Correct
fm.data = data

# 2. Convert other types to dictionary
import json
json_string = '{"key": "value"}'
data = json.loads(json_string)
fm.data = data

# 3. Use proper data structure
# For lists, wrap in a dictionary
fm.data = {"items": [1, 2, 3]}  # Correct
# fm.data = [1, 2, 3]  # Incorrect
```
