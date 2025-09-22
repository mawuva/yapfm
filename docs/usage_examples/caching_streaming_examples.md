# Caching & Streaming Examples

This document provides practical examples of using YAPFM's caching and performance features: intelligent caching, lazy loading, and streaming capabilities.

## 🚀 Quick Start with Caching & Performance Features

### Basic Setup

```python
from yapfm import YAPFileManager
from yapfm.strategies import JSONFileStrategy

# Create a file manager with all caching and performance features enabled
fm = YAPFileManager(
    "config.json",
    strategy=JSONFileStrategy(),
    auto_create=True,
    enable_cache=True,           # Enable intelligent caching
    cache_size=1000,            # Maximum 1000 cached entries
    cache_ttl=3600,             # 1 hour TTL
    enable_lazy_loading=True,   # Enable lazy loading for sections
    enable_streaming=True       # Enable streaming for large files
)
```

## 🧠 Intelligent Caching Examples

### Basic Caching

```python
# First access loads from file and caches
host = fm.get_value("database.host")
print(f"Database host: {host}")

# Subsequent accesses return from cache (much faster)
host_cached = fm.get_value("database.host")  # Returns from cache
print(f"Cached host: {host_cached}")

# Access with default value
port = fm.get_value("database.port", default=5432)
print(f"Database port: {port}")
```

### Cache Management

```python
# Get cache statistics
stats = fm.get_cache_stats()
print(f"Cache hits: {stats['unified_cache']['hits']}")
print(f"Cache misses: {stats['unified_cache']['misses']}")
print(f"Hit rate: {stats['unified_cache']['hit_rate']:.2%}")
print(f"Cache size: {stats['unified_cache']['size']}")

# Invalidate specific patterns
fm.invalidate_cache("key:database.*")  # Invalidate all database keys
fm.invalidate_cache("key:api.*")       # Invalidate all API keys

# Clear all cache
fm.clear_cache()
```

### Performance Monitoring

```python
import time

# Measure cache performance
start_time = time.time()
for i in range(1000):
    value = fm.get_value("database.host")
cached_time = time.time() - start_time

# Clear cache and measure without caching
fm.clear_cache()
start_time = time.time()
for i in range(1000):
    value = fm.get_value("database.host")
uncached_time = time.time() - start_time

print(f"Cached access time: {cached_time:.4f}s")
print(f"Uncached access time: {uncached_time:.4f}s")
print(f"Speed improvement: {uncached_time/cached_time:.2f}x")
```

## 🎯 Lazy Loading Examples

### Basic Lazy Loading

```python
# Section is not loaded until accessed
db_section = fm.get_section("database")
print(f"Database host: {db_section['host']}")
print(f"Database port: {db_section['port']}")

# Subsequent accesses return from lazy cache
db_section_again = fm.get_section("database")  # Returns from cache
print(f"Database name: {db_section_again['name']}")
```

### Lazy Loading with Statistics

```python
# Get lazy loading statistics
stats = fm.get_lazy_stats()
print(f"Total sections: {stats['total_sections']}")
print(f"Loaded sections: {stats['loaded_sections']}")
print(f"Loading efficiency: {stats['loaded_sections']/stats['total_sections']:.2%}")

# Force immediate loading (bypass lazy loading)
db_section = fm.get_section("database", lazy=False)
```

### Lazy Loading with Cache Invalidation

```python
# Update section with cache invalidation
fm.set_section({
    "host": "newhost.example.com",
    "port": 3306,
    "name": "new_database"
}, dot_key="database", update_lazy_cache=True)

# The lazy cache is automatically invalidated
db_section = fm.get_section("database")  # Loads fresh data
print(f"New database host: {db_section['host']}")
```

## 🌊 Streaming Examples

### Basic File Streaming

```python
# Stream file in chunks
for chunk in fm.stream_file(chunk_size=1024*1024):  # 1MB chunks
    print(f"Processing chunk of {len(chunk)} bytes")
    process_chunk(chunk)
```

### Line-by-Line Processing

```python
# Stream file line by line
error_count = 0
for line in fm.stream_lines():
    if "ERROR" in line:
        error_count += 1
        print(f"Error found: {line.strip()}")

print(f"Total errors found: {error_count}")
```

### Section Extraction

```python
# Extract sections from large configuration files
for section in fm.stream_sections("[", "]"):
    print(f"Section: {section['name']}")
    print(f"Content: {section['content']}")
    print("---")
```

### Custom Processing with Progress

```python
def count_words(chunk):
    return len(chunk.split())

def progress_callback(progress):
    print(f"Processing progress: {progress:.1%}")

# Process large file with custom function
results = list(fm.process_large_file(count_words, progress_callback))
total_words = sum(results)
print(f"Total words in file: {total_words}")
```

### Search in Large Files

```python
# Search for patterns in large files
for match in fm.search_in_file("error", case_sensitive=False, context_lines=3):
    print(f"Found at line {match['line_number']}: {match['match']}")
    print(f"Context: {match['context']}")
    print("---")
```

## 🔧 Real-World Examples

### Configuration Management System

```python
class ConfigManager:
    def __init__(self, config_file):
        self.fm = YAPFileManager(
            config_file,
            enable_cache=True,
            cache_size=5000,
            cache_ttl=1800,  # 30 minutes
            enable_lazy_loading=True
        )
    
    def get_database_config(self):
        """Get database configuration with caching."""
        return self.fm.get_section("database")
    
    def get_api_config(self):
        """Get API configuration with caching."""
        return self.fm.get_section("api")
    
    def update_database_config(self, new_config):
        """Update database configuration with cache invalidation."""
        self.fm.set_section(new_config, dot_key="database", update_lazy_cache=True)
    
    def get_cache_stats(self):
        """Get comprehensive cache statistics."""
        return self.fm.get_cache_stats()

# Usage
config = ConfigManager("app_config.json")
db_config = config.get_database_config()
api_config = config.get_api_config()

# Monitor performance
stats = config.get_cache_stats()
print(f"Cache hit rate: {stats['unified_cache']['hit_rate']:.2%}")
```

### Large Log File Analyzer

```python
class LogAnalyzer:
    def __init__(self, log_file):
        self.fm = YAPFileManager(log_file, enable_streaming=True)
    
    def analyze_errors(self):
        """Analyze error patterns in log file."""
        error_patterns = {}
        
        for match in self.fm.search_in_file("ERROR", case_sensitive=False):
            error_type = self.extract_error_type(match['match'])
            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
        
        return error_patterns
    
    def extract_error_type(self, error_line):
        """Extract error type from error line."""
        # Simple error type extraction
        if "connection" in error_line.lower():
            return "connection_error"
        elif "timeout" in error_line.lower():
            return "timeout_error"
        else:
            return "unknown_error"
    
    def get_file_stats(self):
        """Get file statistics."""
        return {
            "size": self.fm.get_file_size(),
            "progress": self.fm.get_file_progress()
        }

# Usage
analyzer = LogAnalyzer("application.log")
error_patterns = analyzer.analyzer_errors()
print("Error patterns found:")
for error_type, count in error_patterns.items():
    print(f"  {error_type}: {count}")

file_stats = analyzer.get_file_stats()
print(f"File size: {file_stats['size']} bytes")
```

### Memory-Efficient Data Processor

```python
class DataProcessor:
    def __init__(self, data_file):
        self.fm = YAPFileManager(
            data_file,
            enable_lazy_loading=True,
            enable_cache=True,
            cache_size=1000
        )
    
    def process_user_data(self, user_id):
        """Process user data with lazy loading."""
        user_section = self.fm.get_section(f"users.{user_id}")
        if user_section:
            return self.process_user_section(user_section)
        return None
    
    def process_user_section(self, user_data):
        """Process individual user data."""
        # Process user data without loading entire file
        return {
            "id": user_data.get("id"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "processed_at": time.time()
        }
    
    def get_processing_stats(self):
        """Get processing statistics."""
        cache_stats = self.fm.get_cache_stats()
        lazy_stats = self.fm.get_lazy_stats()
        
        return {
            "cache_hit_rate": cache_stats['unified_cache']['hit_rate'],
            "loaded_sections": lazy_stats['loaded_sections'],
            "total_sections": lazy_stats['total_sections']
        }

# Usage
processor = DataProcessor("users.json")

# Process individual users (only loads their sections)
user_1 = processor.process_user_data("user_1")
user_2 = processor.process_user_data("user_2")

# Get processing statistics
stats = processor.get_processing_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
print(f"Loaded sections: {stats['loaded_sections']}/{stats['total_sections']}")
```

## 🎯 Performance Optimization Examples

### Cache Size Optimization

```python
import time
import psutil

def optimize_cache_size(fm, test_keys, max_memory_mb=100):
    """Find optimal cache size based on memory usage."""
    best_size = 100
    best_hit_rate = 0
    
    for cache_size in [100, 500, 1000, 2000, 5000]:
        fm.clear_cache()
        fm.unified_cache.max_size = cache_size
        
        # Test with sample keys
        start_time = time.time()
        for key in test_keys:
            fm.get_value(key)
        test_time = time.time() - start_time
        
        # Get statistics
        stats = fm.get_cache_stats()
        hit_rate = stats['unified_cache']['hit_rate']
        memory_usage = stats['unified_cache']['memory_usage_mb']
        
        print(f"Cache size: {cache_size}, Hit rate: {hit_rate:.2%}, Memory: {memory_usage:.2f}MB")
        
        if hit_rate > best_hit_rate and memory_usage < max_memory_mb:
            best_size = cache_size
            best_hit_rate = hit_rate
    
    return best_size

# Usage
test_keys = ["database.host", "database.port", "api.key", "api.url", "app.name"]
optimal_size = optimize_cache_size(fm, test_keys)
print(f"Optimal cache size: {optimal_size}")
```

### Lazy Loading Efficiency

```python
def analyze_lazy_loading_efficiency(fm):
    """Analyze lazy loading efficiency."""
    stats = fm.get_lazy_stats()
    
    total_sections = stats['total_sections']
    loaded_sections = stats['loaded_sections']
    efficiency = loaded_sections / total_sections if total_sections > 0 else 0
    
    print(f"Lazy Loading Analysis:")
    print(f"  Total sections: {total_sections}")
    print(f"  Loaded sections: {loaded_sections}")
    print(f"  Efficiency: {efficiency:.2%}")
    
    if efficiency > 0.5:
        print("  Warning: High lazy loading ratio, consider disabling lazy loading")
    elif efficiency < 0.1:
        print("  Good: Low lazy loading ratio, lazy loading is working well")
    else:
        print("  Good: Moderate lazy loading ratio")

# Usage
analyze_lazy_loading_efficiency(fm)
```

### Streaming Performance

```python
def benchmark_streaming(fm, chunk_sizes=[1024, 10240, 102400, 1024000]):
    """Benchmark streaming performance with different chunk sizes."""
    results = {}
    
    for chunk_size in chunk_sizes:
        start_time = time.time()
        
        # Stream file with specific chunk size
        chunks = list(fm.stream_file(chunk_size=chunk_size))
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        results[chunk_size] = {
            "time": processing_time,
            "chunks": len(chunks),
            "avg_chunk_size": sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0
        }
        
        print(f"Chunk size: {chunk_size}, Time: {processing_time:.4f}s, Chunks: {len(chunks)}")
    
    # Find optimal chunk size
    best_chunk_size = min(results.keys(), key=lambda k: results[k]["time"])
    print(f"Optimal chunk size: {best_chunk_size}")
    
    return results

# Usage
streaming_results = benchmark_streaming(fm)
```

## 🔍 Debugging and Monitoring

### Cache Debugging

```python
def debug_cache_behavior(fm):
    """Debug cache behavior and performance."""
    print("Cache Debug Information:")
    print("=" * 50)
    
    # Get cache statistics
    stats = fm.get_cache_stats()
    cache_stats = stats['unified_cache']
    
    print(f"Cache size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"Memory usage: {cache_stats['memory_usage_mb']:.2f}MB")
    print(f"Hit rate: {cache_stats['hit_rate']:.2%}")
    print(f"Hits: {cache_stats['hits']}")
    print(f"Misses: {cache_stats['misses']}")
    print(f"Evictions: {cache_stats['evictions']}")
    
    # Check for performance issues
    if cache_stats['hit_rate'] < 0.5:
        print("⚠️  Warning: Low hit rate, consider increasing cache size")
    
    if cache_stats['memory_usage_mb'] > 50:
        print("⚠️  Warning: High memory usage, consider reducing cache size")
    
    if cache_stats['evictions'] > cache_stats['hits']:
        print("⚠️  Warning: High eviction rate, cache size may be too small")

# Usage
debug_cache_behavior(fm)
```

### Lazy Loading Monitoring

```python
def monitor_lazy_loading(fm):
    """Monitor lazy loading performance."""
    print("Lazy Loading Monitor:")
    print("=" * 50)
    
    stats = fm.get_lazy_stats()
    
    print(f"Total sections: {stats['total_sections']}")
    print(f"Loaded sections: {stats['loaded_sections']}")
    print(f"Loading efficiency: {stats['loaded_sections']/stats['total_sections']:.2%}")
    
    # Monitor memory usage
    import psutil
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Process memory usage: {memory_usage:.2f}MB")
    
    if memory_usage > 100:  # More than 100MB
        print("⚠️  Warning: High memory usage, consider clearing lazy cache")
        fm.clear_lazy_cache()

# Usage
monitor_lazy_loading(fm)
```

## 🎯 Best Practices Summary

### Caching Best Practices

1. **Start with reasonable defaults**: 1000 cache size, 1 hour TTL
2. **Monitor hit rates**: Aim for 80%+ hit rate
3. **Use pattern invalidation**: Invalidate related entries together
4. **Clear cache when needed**: Clear cache when data changes significantly
5. **Balance memory and performance**: Adjust cache size based on available memory

### Lazy Loading Best Practices

1. **Use for large sections**: Only use lazy loading for sections that are large
2. **Monitor memory usage**: Keep track of loaded sections
3. **Invalidate when needed**: Update lazy cache when sections change
4. **Consider access patterns**: Disable lazy loading if sections are accessed frequently

### Streaming Best Practices

1. **Choose appropriate chunk size**: Balance memory usage with I/O efficiency
2. **Use progress callbacks**: Monitor long-running operations
3. **Handle errors gracefully**: Streaming operations can fail on large files
4. **Test with different chunk sizes**: Find the optimal chunk size for your use case

---

*For more examples and advanced usage patterns, see the [API Reference](api/mixins.md) and [New Features Guide](advanced/new_features.md).*
