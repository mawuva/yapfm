# Getting Started

## Basic Setup

```python
from yapfm import YAPFileManager

# Create a file manager
fm = YAPFileManager("config.json")

# Load the file
fm.load()

# Your file is now ready to use!
```

## Using the open_file Helper

For a more convenient approach:

```python
from yapfm.helpers import open_file

# Open file with automatic format detection
fm = open_file("config.json")

# Force a specific format
fm = open_file("config.txt", format="toml")

# Auto-create if file doesn't exist
fm = open_file("new_config.json", auto_create=True)

# Use the file manager
with fm:
    fm.set_key("value", dot_key="key")
```

## With Context Manager (Recommended)

```python
from yapfm import YAPFileManager

# Automatic loading and saving
with YAPFileManager("config.json", auto_create=True) as fm:
    # Work with your configuration
    fm.set_key("value", dot_key="key")
    # File is automatically saved when exiting the context
```
