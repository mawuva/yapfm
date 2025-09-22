# Caching & Performance

This document covers YAPFM's advanced caching and performance features, including intelligent caching, lazy loading, and streaming capabilities.

## 🚀 Overview

YAPFM provides powerful caching and performance features that significantly improve speed, memory efficiency, and usability:

- **Intelligent Caching System**: Smart caching with TTL, LRU eviction, and comprehensive statistics
- **Lazy Loading**: Memory-efficient loading of large sections
- **Streaming Support**: Process files larger than available RAM
- **Unified Architecture**: Centralized cache management and key generation

## 🧠 Intelligent Caching (CacheMixin)

### Features

The new caching system provides:

- **Automatic Caching**: Values are automatically cached on first access
- **TTL Support**: Time-to-live for cached entries
- **LRU Eviction**: Least Recently Used eviction when cache is full
- **Memory Management**: Size-based eviction to prevent memory issues
- **Statistics Tracking**: Hit/miss ratios and performance metrics
- **Pattern Invalidation**: Invalidate cache entries using wildcard patterns
- **Thread Safety**: Safe for use in multi-threaded environments

### Basic Usage

```python
from yapfm import YAPFileManager

# Enable caching
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=1000,      # Maximum number of cached entries
    cache_ttl=3600        # TTL in seconds (1 hour)
)

# First access loads from file and caches
host = fm.get_value("database.host")
print(f"Database host: {host}")

# Subsequent accesses return from cache (much faster)
host_cached = fm.get_value("database.host")  # Returns from cache
```

### Advanced Caching

```python
# Get cache statistics
stats = fm.get_cache_stats()
print(f"Cache hits: {stats['unified_cache']['hits']}")
print(f"Cache misses: {stats['unified_cache']['misses']}")
print(f"Hit rate: {stats['unified_cache']['hit_rate']:.2%}")

# Invalidate specific patterns
fm.invalidate_cache("key:database.*")  # Invalidate all database keys

# Clear all cache
fm.clear_cache()
```

### Performance Benefits

- **Speed**: Cached values are returned instantly
- **Memory Efficient**: LRU eviction prevents memory bloat
- **Configurable**: Adjust cache size and TTL based on your needs
- **Statistics**: Monitor cache performance and optimize usage

## 🎯 Lazy Loading (LazySectionsMixin)

### Features

Lazy loading provides:

- **Memory Efficiency**: Sections are loaded only when accessed
- **Performance**: Avoid loading large sections unnecessarily
- **Cache Integration**: Works seamlessly with the unified cache system
- **Automatic Invalidation**: Cache invalidation when sections are modified
- **Statistics**: Monitor lazy loading performance

### Basic Usage

```python
from yapfm import YAPFileManager

# Enable lazy loading
fm = YAPFileManager(
    "large_config.json",
    enable_lazy_loading=True
)

# Section is not loaded until accessed
db_section = fm.get_section("database")  # Loads only when accessed
print(f"Database host: {db_section['host']}")

# Subsequent accesses return from lazy cache
db_section_again = fm.get_section("database")  # Returns from cache
```

### Advanced Lazy Loading

```python
# Force immediate loading (bypass lazy loading)
db_section = fm.get_section("database", lazy=False)

# Update section with cache invalidation
fm.set_section({
    "host": "newhost",
    "port": 3306
}, dot_key="database", update_lazy_cache=True)

# Get lazy loading statistics
stats = fm.get_lazy_stats()
print(f"Total sections: {stats['total_sections']}")
print(f"Loaded sections: {stats['loaded_sections']}")

# Clear lazy cache
fm.clear_lazy_cache()
```

### Memory Benefits

- **Reduced Memory Usage**: Only load sections when needed
- **Faster Startup**: Don't load entire file at startup
- **Selective Loading**: Load only the sections you actually use
- **Automatic Management**: Cache invalidation when sections change

## 🌊 Streaming Support (StreamingMixin)

### Features

Streaming provides:

- **Large File Support**: Process files larger than available RAM
- **Chunked Reading**: Process files in configurable chunks
- **Memory Efficient**: Constant memory usage regardless of file size
- **Multiple Formats**: Support for different file encodings
- **Progress Tracking**: Monitor processing progress
- **Search Capabilities**: Search within large files
- **Section Extraction**: Extract specific sections from large files

### Basic Usage

```python
from yapfm import YAPFileManager

# Enable streaming
fm = YAPFileManager(
    "large_file.txt",
    enable_streaming=True
)

# Stream file in chunks
for chunk in fm.stream_file(chunk_size=1024*1024):  # 1MB chunks
    process_chunk(chunk)

# Stream line by line
for line in fm.stream_lines():
    if "error" in line.lower():
        print(f"Error found: {line}")
```

### Advanced Streaming

```python
# Stream sections with markers
for section in fm.stream_sections("[", "]"):
    print(f"Section: {section['name']}")
    print(f"Content: {section['content']}")

# Process with custom function
def count_lines(chunk):
    return chunk.count('\n')

def progress_callback(progress):
    print(f"Progress: {progress:.1%}")

results = list(fm.process_large_file(count_lines, progress_callback))
total_lines = sum(results)

# Search in large file
for match in fm.search_in_file("error", case_sensitive=False):
    print(f"Found: {match['match']}")
    print(f"Context: {match['context']}")

# Get file information
size = fm.get_file_size()
progress = fm.get_file_progress()
estimated_time = fm.estimate_processing_time(count_lines)
```

### Performance Benefits

- **Memory Efficient**: Process files of any size
- **Configurable**: Adjust chunk size based on available memory
- **Progress Tracking**: Monitor long-running operations
- **Search Capabilities**: Find patterns in large files efficiently

## 🏗️ Unified Architecture

### Centralized Cache Management

The new architecture provides:

- **Unified Cache**: Single cache instance for all operations
- **Key Generation**: Centralized key generation with caching
- **Statistics**: Comprehensive statistics across all caching mechanisms
- **Memory Management**: Centralized memory management and cleanup

### Key Generation Optimization

```python
# Key generation is now cached for performance
key1 = fm._generate_cache_key("database.host", None, None, "key")
key2 = fm._generate_cache_key("database.host", None, None, "key")  # Returns cached key

# Clear key generation cache
fm.clear_key_cache()
```

### Comprehensive Statistics

```python
# Get unified statistics
stats = fm.get_cache_stats()
print("Unified Cache Stats:")
print(f"  Hits: {stats['unified_cache']['hits']}")
print(f"  Misses: {stats['unified_cache']['misses']}")
print(f"  Hit Rate: {stats['unified_cache']['hit_rate']:.2%}")

print("Lazy Sections Stats:")
print(f"  Total Sections: {stats['lazy_sections']['total_sections']}")
print(f"  Loaded Sections: {stats['lazy_sections']['loaded_sections']}")

print("Key Cache Stats:")
print(f"  Size: {stats['key_cache']['size']}")
```

## 🔧 Configuration Examples

### High-Performance Configuration

```python
# For high-performance applications
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=10000,     # Large cache
    cache_ttl=7200,       # 2 hours TTL
    enable_lazy_loading=True,
    enable_streaming=True
)
```

### Memory-Conscious Configuration

```python
# For memory-constrained environments
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=100,       # Small cache
    cache_ttl=300,        # 5 minutes TTL
    enable_lazy_loading=True,
    enable_streaming=True
)
```

### Development Configuration

```python
# For development with frequent changes
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=1000,
    cache_ttl=60,         # Short TTL for development
    enable_lazy_loading=False,  # Disable for easier debugging
    enable_streaming=True
)
```

## 📊 Performance Monitoring

### Cache Performance

```python
# Monitor cache performance
stats = fm.get_cache_stats()
hit_rate = stats['unified_cache']['hit_rate']

if hit_rate < 0.8:  # Less than 80% hit rate
    print("Warning: Low cache hit rate, consider increasing cache size")
    fm.clear_cache()  # Clear cache and start fresh
```

### Memory Usage

```python
# Monitor memory usage
stats = fm.get_cache_stats()
memory_usage = stats['unified_cache']['memory_usage_mb']

if memory_usage > 50:  # More than 50MB
    print("Warning: High memory usage, consider reducing cache size")
    fm.clear_cache()
```

### Lazy Loading Efficiency

```python
# Monitor lazy loading efficiency
stats = fm.get_lazy_stats()
loaded_ratio = stats['loaded_sections'] / stats['total_sections']

if loaded_ratio > 0.5:  # More than 50% of sections loaded
    print("Warning: High lazy loading ratio, consider disabling lazy loading")
```

## 🚨 Best Practices

### Caching Best Practices

1. **Choose Appropriate Cache Size**: Balance memory usage with performance
2. **Set Reasonable TTL**: Don't cache data that changes frequently
3. **Monitor Hit Rates**: Aim for 80%+ hit rate
4. **Use Pattern Invalidation**: Invalidate related cache entries together
5. **Clear Cache When Needed**: Clear cache when data changes significantly

### Lazy Loading Best Practices

1. **Use for Large Sections**: Only use lazy loading for sections that are large
2. **Monitor Memory Usage**: Keep track of loaded sections
3. **Invalidate When Needed**: Update lazy cache when sections change
4. **Consider Access Patterns**: Disable lazy loading if sections are accessed frequently

### Streaming Best Practices

1. **Choose Appropriate Chunk Size**: Balance memory usage with I/O efficiency
2. **Use Progress Callbacks**: Monitor long-running operations
3. **Handle Errors Gracefully**: Streaming operations can fail on large files
4. **Consider File Size**: Use streaming for files larger than available RAM
5. **Test with Different Chunk Sizes**: Find the optimal chunk size for your use case

## 🔄 Migration Guide

### From Basic to Cached

```python
# Old way
host = fm.get_key("database.host")

# New way with caching
host = fm.get_value("database.host")  # Automatically cached
```

### From Immediate to Lazy Loading

```python
# Old way
section = fm.get_section("database")

# New way with lazy loading
section = fm.get_section("database", lazy=True)  # Lazy loaded
```

### Adding Streaming Support

```python
# For large files
fm = YAPFileManager("large_file.txt", enable_streaming=True)

# Process in chunks
for chunk in fm.stream_file():
    process_chunk(chunk)
```

## 🎯 Use Cases

### Configuration Management

```python
# High-performance configuration management
fm = YAPFileManager(
    "app_config.json",
    enable_cache=True,
    cache_size=1000,
    cache_ttl=3600,
    enable_lazy_loading=True
)

# Fast access to frequently used values
db_host = fm.get_value("database.host")
api_key = fm.get_value("api.key")
```

### Large File Processing

```python
# Process large log files
fm = YAPFileManager("access.log", enable_streaming=True)

# Search for errors
for match in fm.search_in_file("ERROR", case_sensitive=False):
    print(f"Error at line {match['line_number']}: {match['match']}")
```

### Memory-Efficient Data Access

```python
# Process large configuration files
fm = YAPFileManager(
    "large_config.json",
    enable_lazy_loading=True,
    enable_cache=True
)

# Only load sections when needed
if user_needs_database_config:
    db_config = fm.get_section("database")
    process_database_config(db_config)
```

## 🔮 Future Enhancements

Planned enhancements include:

- **Distributed Caching**: Support for Redis and other distributed caches
- **Compression**: Automatic compression of cached data
- **Encryption**: Encrypted caching for sensitive data
- **Metrics**: More detailed performance metrics
- **Profiling**: Built-in profiling tools
- **Visualization**: Cache performance visualization tools

---

*For more information about these features, see the [API Reference](api/mixins.md) and [Examples](usage_examples/index.md).*
