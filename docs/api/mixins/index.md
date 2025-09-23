# Mixins

YAPFM mixins provide modular functionality to extend file manager capabilities. Each mixin can be used independently or in combination with other mixins.

## Available Mixins

### Core Mixins
- [FileOperationsMixin](file_operations_mixin.md) - Basic file operations
- [KeyOperationsMixin](key_operations_mixin.md) - Key-based data access with dot notation
- [SectionOperationsMixin](section_operations_mixin.md) - Section-based data management
- [ContextMixin](context_mixin.md) - Context manager for automatic loading/saving
- [Batch Operations](batch_operations_mixin.md) - Efficient batch operations for multiple keys

### Performance Mixins
- [CacheMixin](cache_mixin.md) - Intelligent caching with TTL and LRU eviction
- [LazySectionsMixin](lazy_sections_mixin.md) - Lazy loading of sections
- [StreamingMixin](streaming_mixin.md) - Large file processing

### Analysis and Search Mixins
- [AnalysisMixin](analysis_mixin.md) - Data analysis and statistics
- [SearchMixin](search_mixin.md) - Search in keys and values

### Transformation Mixins
- [TransformMixin](transform_mixin.md) - Data transformation and restructuring
- [CleanupMixin](cleanup_mixin.md) - Data cleanup (removing nulls, empty sections)

### Advanced Management Mixins
- [MultiFileMixin](multi_file_mixin.md) - Multi-file management and merging
- [CloneMixin](clone_mixin.md) - Data cloning and copying
- [ExportMixin](export_mixin.md) - Export to different formats
- [SecurityMixin](security_mixin.md) - Security and sensitive data masking

## Usage

Mixins are automatically included in `YAPFileManager` and can be used directly:

```python
from yapfm import YAPFileManager

# All mixins are available
fm = YAPFileManager("config.json")

# Using mixin functionality
fm.set_key("value", dot_key="database.host")  # KeyOperationsMixin
fm.set_value("key", "value")  # CacheMixin
fm.get_stats()  # AnalysisMixin
fm.search_in_values("localhost")  # SearchMixin
```

## Architecture

Mixins follow the composition pattern and are designed to be:
- **Modular**: Each mixin has a specific responsibility
- **Composable**: Can be combined as needed
- **Thread-safe**: Safe for concurrent usage
- **Performant**: Optimized for frequent operations
