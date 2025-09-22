# Performance Features

YAPFM provides powerful performance features designed to optimize speed, memory usage, and efficiency for various use cases.

## 🚀 Overview

YAPFM's performance features are built around three core concepts:

- **Intelligent Caching**: Smart caching system with TTL, LRU eviction, and comprehensive statistics
- **Lazy Loading**: Memory-efficient loading of large sections and data
- **Streaming**: Process files larger than available RAM with constant memory usage

## 🧠 Intelligent Caching

### What is Intelligent Caching?

Intelligent caching automatically caches frequently accessed values to dramatically improve performance. The system includes:

- **TTL Support**: Time-to-live for cached entries
- **LRU Eviction**: Least Recently Used eviction when cache is full
- **Memory Management**: Size-based eviction to prevent memory issues
- **Statistics Tracking**: Hit/miss ratios and performance metrics
- **Pattern Invalidation**: Invalidate cache entries using wildcard patterns

### When to Use Caching

- **Frequently Accessed Data**: Configuration values accessed multiple times
- **Expensive Operations**: Data that takes time to load or compute
- **Read-Heavy Workloads**: Applications that read more than they write
- **Performance Critical**: Applications where speed is important

### Example

```python
from yapfm import YAPFileManager

# Enable caching
fm = YAPFileManager(
    "config.json",
    enable_cache=True,
    cache_size=1000,      # Maximum 1000 cached entries
    cache_ttl=3600        # 1 hour TTL
)

# First access loads from file and caches
host = fm.get_value("database.host")

# Subsequent accesses return from cache (much faster)
host_cached = fm.get_value("database.host")  # Returns from cache
```

## 🎯 Lazy Loading

### What is Lazy Loading?

Lazy loading loads data only when it's actually needed, reducing memory usage and startup time. Features include:

- **Memory Efficiency**: Sections are loaded only when accessed
- **Cache Integration**: Works seamlessly with the unified cache system
- **Automatic Invalidation**: Cache invalidation when sections are modified
- **Statistics Tracking**: Monitor lazy loading performance

### When to Use Lazy Loading

- **Large Configuration Files**: Files with many sections, but only some are used
- **Memory Constrained**: Applications with limited memory
- **Selective Access**: When only specific parts of data are needed
- **Startup Performance**: When fast startup is important

### Example

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

## 🌊 Streaming

### What is Streaming?

Streaming allows processing files larger than available RAM by reading them in chunks. Features include:

- **Large File Support**: Process files larger than available RAM
- **Chunked Reading**: Process files in configurable chunks
- **Memory Efficient**: Constant memory usage regardless of file size
- **Progress Tracking**: Monitor processing progress
- **Search Capabilities**: Search within large files

### When to Use Streaming

- **Large Files**: Files larger than available RAM
- **Log Processing**: Analyzing large log files
- **Data Processing**: Processing large datasets
- **Memory Constrained**: When memory usage must be controlled

### Example

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
    if "ERROR" in line:
        print(f"Error found: {line}")
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

## 🔍 Troubleshooting

### Common Issues

#### Low Cache Hit Rate
- **Problem**: Cache hit rate below 80%
- **Solution**: Increase cache size or check access patterns

#### High Memory Usage
- **Problem**: Memory usage too high
- **Solution**: Reduce cache size or enable lazy loading

#### Slow Streaming
- **Problem**: Streaming operations are slow
- **Solution**: Adjust chunk size or check disk I/O performance

### Performance Tips

1. **Profile Your Application**: Use profiling tools to identify bottlenecks
2. **Monitor Statistics**: Regularly check cache and lazy loading statistics
3. **Test Different Configurations**: Find the optimal settings for your use case
4. **Consider Your Data**: Different data patterns require different optimizations

## 🔮 Future Enhancements

Planned enhancements include:

- **Distributed Caching**: Support for Redis and other distributed caches
- **Compression**: Automatic compression of cached data
- **Encryption**: Encrypted caching for sensitive data
- **Metrics**: More detailed performance metrics
- **Profiling**: Built-in profiling tools
- **Visualization**: Cache performance visualization tools

---

*For more detailed information, see the [Caching & Performance Guide](advanced/caching_performance.md) and [Examples](usage_examples/caching_streaming_examples.md).*
