# ExportMixin

Provides export functionality for the file manager. The ExportMixin contains operations for exporting data to different formats.

## Methods

### to_current_format

```python
def to_current_format(self) -> str
```

Export data to the current file's format using the manager's strategy.

**Returns:**
- `str`: String content in the current format

**Example:**
```python
fm = YAPFileManager("config.json")
json_str = fm.to_current_format()  # Uses JSON strategy
```

### to_json

```python
def to_json(self, pretty: bool = True) -> str
```

Export data to JSON format.

**Parameters:**
- `pretty` (bool): If True, formats with indentation

**Returns:**
- `str`: JSON string

**Example:**
```python
json_str = fm.to_json()
json_str = fm.to_json(pretty=False)  # Compact format
```

### to_yaml

```python
def to_yaml(self) -> str
```

Export data to YAML format.

**Returns:**
- `str`: YAML string

**Example:**
```python
yaml_str = fm.to_yaml()
```

### to_toml

```python
def to_toml(self) -> str
```

Export data to TOML format.

**Returns:**
- `str`: TOML string

**Example:**
```python
toml_str = fm.to_toml()
```

### export_section

```python
def export_section(
    self,
    section_path: str,
    format: str = "json",
    output_path: Optional[Union[str, Path]] = None,
) -> Union[str, Path]
```

Export a specific section to a file or return as string.

**Parameters:**
- `section_path` (str): Dot-separated path to the section
- `format` (str): Output format ("json", "yaml", "toml")
- `output_path` (Optional[Union[str, Path]]): Optional output file path. If None, returns string

**Returns:**
- `Union[str, Path]`: String content or output file path

**Example:**
```python
# Returns JSON string
json_str = fm.export_section("database", "json")

# Saves to file
fm.export_section("api", "yaml", "api_config.yaml")
```

### export_to_file

```python
def export_to_file(
    self, 
    output_path: Union[str, Path], 
    format: Optional[str] = None
) -> Path
```

Export the entire data to a file in the specified format.

**Parameters:**
- `output_path` (Union[str, Path]): Output file path
- `format` (Optional[str]): Output format. If None, inferred from file extension

**Returns:**
- `Path`: Output file path

**Example:**
```python
fm.export_to_file("backup.json")
fm.export_to_file("config.yaml", "yaml")
```
