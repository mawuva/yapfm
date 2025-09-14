# Core Concepts

## File Manager

The `YAPFileManager` is the main class that combines all functionality through mixins:

- **FileOperationsMixin**: Basic file operations (load, save, exists)
- **KeyOperationsMixin**: Key-based data access with dot notation
- **SectionOperationsMixin**: Section-based data management
- **ContextMixin**: Context manager support

## Strategies

YAPFM uses the Strategy pattern to handle different file formats:

- **JsonStrategy**: Handles JSON files
- **TomlStrategy**: Handles TOML files with comment preservation
- **YamlStrategy**: Handles YAML files with safe loading

## Dot Notation

YAPFM uses dot notation to access nested data:

```python
# Instead of: data["section"]["subsection"]["key"]
fm.get_key(dot_key="section.subsection.key")

# Instead of: data["section"]["subsection"]["key"] = "value"
fm.set_key("value", dot_key="section.subsection.key")
```
