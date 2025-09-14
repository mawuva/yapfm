# Basic Examples

## Simple Configuration File

```python
from yapfm import YAPFileManager

# Create a basic configuration file
def create_app_config():
    with YAPFileManager("app_config.json", auto_create=True) as fm:
        # Application settings
        fm.set_key("My Application", dot_key="app.name")
        fm.set_key("1.0.0", dot_key="app.version")
        fm.set_key("production", dot_key="app.environment")
        
        # Database configuration
        fm.set_key("localhost", dot_key="database.host")
        fm.set_key(5432, dot_key="database.port")
        fm.set_key("myapp", dot_key="database.name")
        fm.set_key(True, dot_key="database.ssl")
        
        # API settings
        fm.set_key("v1", dot_key="api.version")
        fm.set_key(30, dot_key="api.timeout")
        fm.set_key(3, dot_key="api.retries")
        
        print("Configuration created successfully!")

# Read configuration
def read_app_config():
    with YAPFileManager("app_config.json") as fm:
        app_name = fm.get_key(dot_key="app.name")
        db_host = fm.get_key(dot_key="database.host")
        api_timeout = fm.get_key(dot_key="api.timeout")
        
        print(f"App: {app_name}")
        print(f"Database: {db_host}")
        print(f"API Timeout: {api_timeout}s")

# Run the examples
create_app_config()
read_app_config()
```

## Working with Different File Formats

### Using YAPFileManager Directly

```python
from yapfm import YAPFileManager

# JSON configuration
def json_example():
    with YAPFileManager("config.json", auto_create=True) as fm:
        fm.set_key("JSON Config", dot_key="format")
        fm.set_key({"key1": "value1", "key2": "value2"}, dot_key="data")
        print("JSON configuration created")

# TOML configuration
def toml_example():
    with YAPFileManager("config.toml", auto_create=True) as fm:
        fm.set_key("TOML Config", dot_key="format")
        fm.set_key("localhost", dot_key="server.host")
        fm.set_key(8000, dot_key="server.port")
        print("TOML configuration created")

# YAML configuration
def yaml_example():
    with YAPFileManager("config.yaml", auto_create=True) as fm:
        fm.set_key("YAML Config", dot_key="format")
        fm.set_key(["item1", "item2", "item3"], dot_key="items")
        print("YAML configuration created")

# Run all examples
json_example()
toml_example()
yaml_example()
```

### Using the open_file Helper

```python
from yapfm.helpers import open_file

# Open files with automatic format detection
def open_file_examples():
    # JSON file
    json_fm = open_file("config.json", auto_create=True)
    with json_fm:
        json_fm.set_key("JSON Config", dot_key="format")
        json_fm.set_key({"key1": "value1", "key2": "value2"}, dot_key="data")
    
    # TOML file
    toml_fm = open_file("config.toml", auto_create=True)
    with toml_fm:
        toml_fm.set_key("TOML Config", dot_key="format")
        toml_fm.set_key("localhost", dot_key="server.host")
        toml_fm.set_key(8000, dot_key="server.port")
    
    # YAML file
    yaml_fm = open_file("config.yaml", auto_create=True)
    with yaml_fm:
        yaml_fm.set_key("YAML Config", dot_key="format")
        yaml_fm.set_key(["item1", "item2", "item3"], dot_key="items")
    
    print("All configurations created using open_file helper")

# Format override examples
def format_override_examples():
    # Force JSON format regardless of file extension
    json_fm = open_file("config.txt", format="json", auto_create=True)
    with json_fm:
        json_fm.set_key("Forced JSON", dot_key="format")
    
    # Force TOML format
    toml_fm = open_file("settings.dat", format="toml", auto_create=True)
    with toml_fm:
        toml_fm.set_key("Forced TOML", dot_key="format")
    
    # Force YAML format
    yaml_fm = open_file("data.log", format="yaml", auto_create=True)
    with yaml_fm:
        yaml_fm.set_key("Forced YAML", dot_key="format")
    
    print("Format override examples completed")

# Run examples
open_file_examples()
format_override_examples()
```
