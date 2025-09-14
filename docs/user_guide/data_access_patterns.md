# Data Access Patterns

## Key Operations

### Setting Values

```python
# Set single values
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key(True, dot_key="database.ssl")

# Set with path and key name
fm.set_key("localhost", path=["database"], key_name="host")

# Set with overwrite control
fm.set_key("new_value", dot_key="key", overwrite=True)   # Default
fm.set_key("new_value", dot_key="key", overwrite=False)  # Only if key doesn't exist
```

### Getting Values

```python
# Get values with defaults
host = fm.get_key(dot_key="database.host", default="localhost")
port = fm.get_key(dot_key="database.port", default=5432)

# Get with path and key name
host = fm.get_key(path=["database"], key_name="host", default="localhost")

# Get without default (returns None if not found)
host = fm.get_key(dot_key="database.host")
```

### Checking Existence

```python
# Check if key exists
if fm.has_key(dot_key="database.host"):
    print("Database host is configured")

# Check with path and key name
if fm.has_key(path=["database"], key_name="host"):
    print("Database host is configured")
```

### Deleting Keys

```python
# Delete single keys
deleted = fm.delete_key(dot_key="database.host")
if deleted:
    print("Database host removed")

# Delete with path and key name
deleted = fm.delete_key(path=["database"], key_name="host")
```

## Section Operations

### Setting Sections

```python
# Set entire sections
database_config = {
    "host": "localhost",
    "port": 5432,
    "name": "myapp",
    "ssl": True
}
fm.set_section(database_config, dot_key="database")

# Set nested sections
api_config = {
    "version": "v1",
    "timeout": 30,
    "cors": {
        "enabled": True,
        "origins": ["http://localhost:3000"]
    }
}
fm.set_section(api_config, dot_key="api")
```

### Getting Sections

```python
# Get entire sections
database_config = fm.get_section(dot_key="database")
if database_config:
    print(f"Database: {database_config['host']}:{database_config['port']}")

# Get nested sections
cors_config = fm.get_section(dot_key="api.cors")
if cors_config:
    print(f"CORS origins: {cors_config['origins']}")
```

### Checking Section Existence

```python
# Check if section exists
if fm.has_section(dot_key="database"):
    print("Database configuration exists")

# Check nested sections
if fm.has_section(dot_key="api.cors"):
    print("CORS configuration exists")
```

## Direct Data Access

```python
# Access data directly (auto-loads if not loaded)
data = fm.data
print(f"All data: {data}")

# Set data directly
fm.data = {
    "app": {"name": "My App", "version": "1.0.0"},
    "database": {"host": "localhost", "port": 5432}
}

# Modify data directly
fm.data["app"]["version"] = "1.1.0"
fm.mark_as_dirty()  # Remember to mark as dirty
```
