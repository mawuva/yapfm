# Error Handling

## Common Exceptions

```python
from yapfm.exceptions import LoadFileError, FileWriteError, StrategyError

try:
    with YAPFileManager("config.json") as fm:
        fm.set_key("value", dot_key="key")
        fm.save()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
except FileWriteError as e:
    print(f"Failed to save file: {e}")
except StrategyError as e:
    print(f"Strategy error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Graceful Error Handling

```python
def safe_config_operation(config_file, key, value):
    """Safely set a configuration value with error handling."""
    try:
        with YAPFileManager(config_file, auto_create=True) as fm:
            fm.set_key(value, dot_key=key)
            return True
    except LoadFileError:
        print(f"Could not load configuration file: {config_file}")
        return False
    except FileWriteError:
        print(f"Could not save configuration file: {config_file}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Use the safe function
success = safe_config_operation("config.json", "database.host", "localhost")
if success:
    print("Configuration updated successfully")
```

## Validation and Error Prevention

```python
def validate_config_file(config_file):
    """Validate that a configuration file is usable."""
    try:
        fm = YAPFileManager(config_file)
        
        # Check if file exists
        if not fm.exists():
            print(f"Configuration file does not exist: {config_file}")
            return False
        
        # Try to load the file
        fm.load()
        
        # Check if file is valid
        if not isinstance(fm.data, dict):
            print(f"Configuration file is not a valid dictionary: {config_file}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Configuration file validation failed: {e}")
        return False

# Use validation
if validate_config_file("config.json"):
    print("Configuration file is valid")
else:
    print("Configuration file has issues")
```
