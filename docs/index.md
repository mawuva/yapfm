# YAPFM Documentation

Welcome to the comprehensive documentation for YAPFM (Yet Another Python File Manager). This documentation covers all aspects of the library, from basic usage to advanced features.

## 📚 Documentation Structure

### Getting Started
- [**Installation Guide**](installation.md) - How to install and set up YAPFM
- [**Quick Start**](quick_start.md) - Get up and running in minutes
- [**User Guide**](user_guide/index.md) - Comprehensive step-by-step guide

### API Reference
- [**API Reference**](api/index.md) - Complete API documentation with examples
- [**Core Classes**](api/core_classes.md) - YAPFileManager, FileManagerProxy
- [**Strategies**](api/strategies.md) - File format handlers
- [**Mixins**](api/mixins.md) - Modular functionality components

### Examples and Patterns
- [**Examples**](usage_examples/index.md) - Code examples and common patterns
- [**Configuration Management**](usage_examples/configuration_management.md) - Real-world config examples
- [**Multi-Environment Setup**](usage_examples/multi_environment_setup.md) - Managing different environments
- [**Advanced Patterns**](usage_examples/advanced_patterns.md) - Complex usage scenarios

### Advanced Topics
- [**Performance Features**](PERFORMANCE_FEATURES.md) - Caching, lazy loading, and streaming capabilities
- [**Advanced Features**](advanced/index.md) - Proxy, mixins, and strategies
- [**Custom Strategies**](advanced/custom_strategies.md) - Creating your own file format handlers
- [**Performance Optimization**](advanced/performance_optimization.md) - Tips for better performance
- [**Thread Safety**](advanced/thread_safety.md) - Using YAPFM in multi-threaded environments

### Troubleshooting
- [**Troubleshooting**](troubleshooting/index.md) - Common issues and solutions
- [**FAQ**](troubleshooting/frequently_asked_questions.md) - Frequently asked questions
- [**Error Reference**](troubleshooting/error_reference.md) - Complete error reference

### Development & Future
- [**Roadmap**](roadmap/index.md) - Future enhancements and planned features
- [**Contributing**](roadmap/contributing_to_development.md) - How to contribute to YAPFM

## 🚀 Quick Navigation

### By Use Case
- **Configuration Files**: Start with [User Guide](user_guide/index.md) → [Configuration Management](usage_examples/configuration_management.md)
- **Performance & Caching**: [Performance Features](PERFORMANCE_FEATURES.md) → [Caching & Streaming Examples](usage_examples/caching_streaming_examples.md)
- **Multi-Format Support**: [API Reference](api/strategies.md) → [Custom Strategies](advanced/custom_strategies.md)
- **Logging & Monitoring**: [Advanced Features](advanced/proxy_pattern.md) → [Examples](usage_examples/logging_monitoring.md)
- **Performance Optimization**: [Performance Features](PERFORMANCE_FEATURES.md) → [Troubleshooting](troubleshooting/performance_issues.md)

### By Experience Level
- **Beginner**: [Installation](installation.md) → [Quick Start](quick_start.md) → [User Guide](user_guide/index.md)
- **Intermediate**: [Examples](usage_examples/index.md) → [API Reference](api/index.md) → [Advanced Features](advanced/index.md)
- **Advanced**: [Custom Strategies](advanced/custom_strategies.md) → [Performance](advanced/performance_optimization.md) → [Troubleshooting](troubleshooting/index.md)

## 💡 Key Concepts

### File Manager
The core class that combines all functionality through mixins. Handles file operations, data access, and persistence.

### Strategies
Format-specific handlers that know how to read and write different file types (JSON, TOML, YAML).

### Mixins
Modular components that provide specific functionality:
- **FileOperationsMixin**: Basic file operations (load, save, exists)
- **KeyOperationsMixin**: Key-based data access with dot notation
- **SectionOperationsMixin**: Section-based data management
- **ContextMixin**: Context manager support
- **CacheMixin**: Intelligent caching with TTL, LRU eviction, and statistics
- **LazySectionsMixin**: Lazy loading for memory-efficient section access
- **StreamingMixin**: Streaming functionality for large files

### Proxy Pattern
Wrapper that adds logging, metrics, and auditing to file operations without modifying the core functionality.

## 🔗 External Resources

- [GitHub Repository](https://github.com/mawuva/yapfm) - Source code and issue tracking
- [PyPI Package](https://pypi.org/project/yapfm/) - Package installation
- [Changelog](CHANGELOG.md) - Version history and changes

## 📝 Contributing to Documentation

Found an error or want to improve the documentation? Please:

1. Check the [Contributing Guide](CONTRIBUTING.md)
2. Open an issue or pull request
3. Follow the documentation style guide

---

*This documentation is automatically generated and updated with each release.*
