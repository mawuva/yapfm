# YAPFM - Yet Another Python File Manager

[![CI](https://github.com/mawuva/yapfm/actions/workflows/ci.yml/badge.svg)](https://github.com/mawuva/yapfm/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/yapfm.svg)](https://pypi.org/project/yapfm/)
[![Python Version](https://img.shields.io/pypi/pyversions/yapfm.svg)](https://pypi.org/project/yapfm/)
![GitHub License](https://img.shields.io/github/license/mawuva/yapfm)


A flexible and powerful Python file manager library for handling various file formats (JSON, TOML, YAML) with support for strategies, mixins, and advanced features like context management, proxy patterns, and automatic file operations.

## 🤔 Why Use YAPFM?

### The Problem
Managing configuration files in Python applications often involves:
- **Repetitive boilerplate code** for loading/saving different file formats
- **Manual error handling** for file operations and validation
- **Inconsistent APIs** across different file format libraries
- **No built-in features** for monitoring, auditing, or advanced operations
- **Complex nested data access** with verbose dictionary navigation

### The Solution
YAPFM provides a **unified, powerful interface** that solves these problems:

#### 🎯 **Unified API Across Formats**
```python
# Same API for JSON, TOML, and YAML files
json_fm = YAPFileManager("config.json")
toml_fm = YAPFileManager("config.toml") 
yaml_fm = YAPFileManager("config.yaml")

# All use the same methods
json_fm.set_key("value", dot_key="database.host")
toml_fm.set_key("value", dot_key="database.host")
yaml_fm.set_key("value", dot_key="database.host")
```

#### 🔧 **Powerful Dot Notation**
```python
# Instead of: data["section"]["subsection"]["key"]
fm.get_key(dot_key="section.subsection.key")

# Instead of: data["section"]["subsection"]["key"] = "value"
fm.set_key("value", dot_key="section.subsection.key")
```

#### 🛡️ **Built-in Safety & Context Management**
```python
# Automatic loading and saving with error handling
with YAPFileManager("config.json", auto_create=True) as fm:
    fm.set_key("localhost", dot_key="database.host")
    # File is automatically saved, even if exceptions occur
```

#### 📊 **Production-Ready Features**
```python
# Built-in logging, metrics, and auditing
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True
)
```

### When to Use YAPFM

**✅ Perfect for:**
- **Configuration Management**: Application settings, environment configs
- **Data Persistence**: User preferences, application state
- **Multi-Format Support**: Applications that need to support JSON, TOML, YAML
- **Production Applications**: Need monitoring, logging, and error handling
- **Complex Data Structures**: Nested configurations with easy access
- **Team Development**: Consistent API across different file formats
- **High-Performance Applications**: Need intelligent caching and lazy loading
- **Large File Processing**: Need streaming capabilities for big files
- **Memory-Constrained Environments**: Need efficient memory usage

**❌ Not ideal for:**
- **Large Binary Files**: Designed for text-based configuration files
- **Real-time Databases**: Use proper databases for high-frequency updates
- **Simple One-off Scripts**: May be overkill for basic file operations

## ✨ Features

### Core Features
- **Multi-format Support**: JSON, TOML, and YAML files with automatic format detection
- **Strategy Pattern**: Extensible architecture for adding new file format support
- **Context Management**: Safe file operations with automatic loading and saving
- **Proxy Pattern**: Logging, metrics, and auditing capabilities
- **Dot Notation**: Easy access to nested data using dot-separated keys
- **Mixins**: Modular functionality for file operations, key management, and sections
- **Type Safety**: Full type hints and protocol-based design
- **Thread Safety**: Thread-safe strategy registry and operations
- **Auto-creation**: Automatic file and directory creation when needed

### Performance Features
- **Intelligent Caching**: Smart caching with TTL, LRU eviction, and comprehensive statistics
- **Lazy Loading**: Memory-efficient loading of large sections and data
- **Streaming Support**: Process files larger than available RAM with constant memory usage
- **Unified Architecture**: Centralized cache management and key generation optimization

## 🚀 Quick Start

### Installation

```bash
pip install yapfm
```

or with Poetry:

```bash
poetry add yapfm
```

### Basic Usage

```python
from yapfm import YAPFileManager

# Create a file manager for a JSON file
fm = YAPFileManager("config.json")

# Load the file (creates empty document if file doesn't exist)
fm.load()

# Set values using dot notation
fm.set_key("localhost", dot_key="database.host")
fm.set_key(5432, dot_key="database.port")
fm.set_key("myapp", dot_key="database.name")

# Save changes
fm.save()

# Read values
host = fm.get_key(dot_key="database.host", default="localhost")
print(f"Database host: {host}")
```

### Using the open_file Helper

For a more convenient way to open files:

```python
from yapfm.helpers import open_file

# Open file with automatic format detection
fm = open_file("config.json")

# Force a specific format regardless of extension
fm = open_file("config.txt", format="toml")

# Auto-create file if it doesn't exist
fm = open_file("new_config.json", auto_create=True)

# Use the file manager
with fm:
    fm.set_key("localhost", dot_key="database.host")
    fm.set_key(5432, dot_key="database.port")
```

### Context Manager Usage

```python
from yapfm import YAPFileManager

# Automatic loading and saving with context manager
with YAPFileManager("config.toml", auto_create=True) as fm:
    # Set configuration values
    fm.set_key("production", dot_key="environment")
    fm.set_key(True, dot_key="debug")
    
    # Set entire sections
    fm.set_section({
        "host": "localhost",
        "port": 8000,
        "workers": 4
    }, dot_key="server")
    
# File is automatically saved when exiting the context
```

### Performance Features

#### Intelligent Caching
```python
from yapfm import YAPFileManager

# Enable caching for high-performance access
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

# Get cache statistics
stats = fm.get_cache_stats()
print(f"Cache hit rate: {stats['unified_cache']['hit_rate']:.2%}")
```

#### Lazy Loading
```python
# Enable lazy loading for memory efficiency
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

#### Streaming Large Files
```python
# Enable streaming for large files
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

# Search in large files
for match in fm.search_in_file("error", case_sensitive=False):
    print(f"Found: {match['match']}")
```

### Advanced Usage with Proxy

```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Create file manager
fm = YAPFileManager("app_config.json")

# Create proxy with logging and metrics
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True
)

# All operations are logged and measured
with proxy:
    proxy.set_key("v1.0.0", dot_key="app.version")
    proxy.set_key("production", dot_key="app.environment")
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [**Performance Features**](docs/PERFORMANCE_FEATURES.md) - Caching, lazy loading, and streaming capabilities
- [**User Guide**](docs/user_guide/index.md) - Step-by-step usage guide
- [**API Reference**](docs/api/index.md) - Complete API documentation
- [**Examples**](docs/usage_examples/index.md) - Code examples and patterns
- [**Advanced Features**](docs/advanced/index.md) - Proxy, mixins, and strategies
- [**Troubleshooting**](docs/troubleshooting/index.md) - Common issues and solutions
- [**Roadmap**](docs/roadmap/index.md) - Future enhancements and planned features

## 🎯 Supported File Formats

| Format | Extension | Strategy | Features |
|--------|-----------|----------|----------|
| JSON | `.json` | `JsonStrategy` | Standard JSON with pretty printing |
| TOML | `.toml` | `TomlStrategy` | Full TOML spec with comment preservation |
| YAML | `.yml`, `.yaml` | `YamlStrategy` | YAML 1.2 with safe loading |

## 🔧 Key Operations

### Dot Notation Access

```python
# Set nested values
fm.set_key("value", dot_key="section.subsection.key")

# Get nested values with defaults
value = fm.get_key(dot_key="section.subsection.key", default="default")

# Check if key exists
exists = fm.has_key(dot_key="section.subsection.key")

# Delete keys
deleted = fm.delete_key(dot_key="section.subsection.key")
```

### Section Operations

```python
# Set entire sections
fm.set_section({
    "host": "localhost",
    "port": 5432,
    "ssl": True
}, dot_key="database")

# Get entire sections
db_config = fm.get_section(dot_key="database")

# Check if section exists
has_section = fm.has_section(dot_key="database")
```

### File Operations

```python
# Check file status
print(f"File exists: {fm.exists()}")
print(f"File loaded: {fm.is_loaded()}")
print(f"File dirty: {fm.is_dirty()}")

# Manual operations
fm.load()      # Load from disk
fm.save()      # Save to disk
fm.reload()    # Reload from disk (discards changes)
fm.unload()    # Unload from memory
```

## 🏗️ Architecture

YAPFM uses a modular architecture with several key components:

- **YAPFileManager**: Main class combining all mixins
- **Strategies**: Format-specific handlers (JSON, TOML, YAML)
- **Mixins**: Modular functionality (FileOperations, KeyOperations, etc.)
- **Registry**: Strategy registration and management
- **Proxy**: Logging, metrics, and auditing wrapper

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python features and type hints
- Inspired by configuration management best practices
- Uses excellent libraries like [https://tomlkit.readthedocs.io/en/latest/](tomlkit) and [https://pyyaml.org/](PyYAML)

