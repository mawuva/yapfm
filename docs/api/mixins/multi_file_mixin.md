# MultiFileMixin

Provides functionality to load and merge multiple files into a single dictionary. It uses the Strategy pattern for different merge approaches and integrates with the existing cache system.

## Key Features

- **Multiple merge strategies** (deep, namespace, priority, conditional, append, replace)
- **File pattern support** (glob patterns)
- **Integration with existing cache system**
- **Conditional merging** based on environment or context
- **Namespace prefixing** for organized data structure
- **Performance optimization** with lazy loading

## Methods

### load_multiple_files

```python
def load_multiple_files(
    self,
    file_paths: Union[List[Union[str, Path]], str],
    strategy: Union[str, MergeStrategy, BaseMergeStrategy] = MergeStrategy.DEEP,
    file_patterns: Optional[List[str]] = None,
    conditional_filter: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]
```

Load and merge multiple files into a single dictionary.

**Parameters:**
- `file_paths` (Union[List[Union[str, Path]], str]): List of file paths or single path/pattern string
- `strategy` (Union[str, MergeStrategy, BaseMergeStrategy]): Strategy to use for merging files
- `file_patterns` (Optional[List[str]]): Optional list of glob patterns to expand
- `conditional_filter` (Optional[Callable[[str, Dict[str, Any]], bool]]): Optional function to filter files based on content
- `use_cache` (bool): Whether to use caching for loaded files
- `**kwargs` (Any): Additional arguments passed to the strategy

**Returns:**
- `Dict[str, Any]`: Dictionary containing merged data from all files

**Example:**
```python
# Deep merge multiple files
data = fm.load_multiple_files([
    "config.json",
    "secrets.json"
], strategy="deep")

# Namespace merge with prefix
data = fm.load_multiple_files([
    "database.json",
    "cache.toml"
], strategy="namespace", namespace_prefix="app")

# Use file patterns
data = fm.load_multiple_files(
    "config/*.json",
    strategy="deep"
)
```

### get_available_merge_strategies

```python
def get_available_merge_strategies(self) -> List[str]
```

Get list of available merge strategies.

**Returns:**
- `List[str]`: List of strategy names

**Example:**
```python
strategies = fm.get_available_merge_strategies()
print(f"Available strategies: {strategies}")
```

### invalidate_multi_file_cache

```python
def invalidate_multi_file_cache(self, file_path: Union[str, Path]) -> None
```

Invalidate cache for a specific file in multi-file operations.

**Parameters:**
- `file_path` (Union[str, Path]): Path to the file to invalidate

**Example:**
```python
fm.invalidate_multi_file_cache("config.json")
```

### load_file_group

```python
def load_file_group(
    self, 
    group_name: str, 
    config: Dict[str, Any], 
    **kwargs: Any
) -> Dict[str, Any]
```

Load a predefined group of files based on configuration.

**Parameters:**
- `group_name` (str): Name of the file group
- `config` (Dict[str, Any]): Configuration dictionary defining the group
- `**kwargs` (Any): Additional arguments for file loading

**Returns:**
- `Dict[str, Any]`: Merged dictionary from the file group

**Example:**
```python
config = {
    "app_config": {
        "files": ["config.json", "secrets.json"],
        "strategy": "deep",
        "namespace_prefix": "app"
    }
}
data = fm.load_file_group("app_config", config)
```
