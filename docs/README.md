# YAPFM Documentation

Welcome to the comprehensive documentation for YAPFM (Yet Another Python File Manager). This documentation covers all aspects of the library, from basic usage to advanced features.

## 📚 Documentation Structure

### Getting Started
- [**Installation Guide**](installation.md) - How to install and set up YAPFM
- [**Quick Start**](quick_start.md) - Get up and running in minutes
- [**User Guide**](user_guide.md) - Comprehensive step-by-step guide

### API Reference
- [**API Reference**](api_reference.md) - Complete API documentation with examples
- [**Core Classes**](api_reference.md#core-classes) - YAPFileManager, FileManagerProxy
- [**Strategies**](api_reference.md#strategies) - File format handlers
- [**Mixins**](api_reference.md#mixins) - Modular functionality components

### Examples and Patterns
- [**Examples**](examples.md) - Code examples and common patterns
- [**Configuration Management**](examples.md#configuration-management) - Real-world config examples
- [**Multi-Environment Setup**](examples.md#multi-environment-setup) - Managing different environments
- [**Advanced Patterns**](examples.md#advanced-patterns) - Complex usage scenarios

### Advanced Topics
- [**Advanced Features**](advanced_features.md) - Proxy, mixins, and strategies
- [**Custom Strategies**](advanced_features.md#custom-strategies) - Creating your own file format handlers
- [**Performance Optimization**](advanced_features.md#performance-optimization) - Tips for better performance
- [**Thread Safety**](advanced_features.md#thread-safety) - Using YAPFM in multi-threaded environments

### Troubleshooting
- [**Troubleshooting**](troubleshooting.md) - Common issues and solutions
- [**FAQ**](troubleshooting.md#frequently-asked-questions) - Frequently asked questions
- [**Error Reference**](troubleshooting.md#error-reference) - Complete error reference

### Development & Future
- [**Roadmap**](roadmap.md) - Future enhancements and planned features
- [**Contributing**](roadmap.md#contributing-to-development) - How to contribute to YAPFM

## 🚀 Quick Navigation

### By Use Case
- **Configuration Files**: Start with [User Guide](user_guide.md) → [Configuration Management](examples.md#configuration-management)
- **Multi-Format Support**: [API Reference](api_reference.md#strategies) → [Custom Strategies](advanced_features.md#custom-strategies)
- **Logging & Monitoring**: [Advanced Features](advanced_features.md#proxy-pattern) → [Examples](examples.md#logging-and-monitoring)
- **Performance**: [Advanced Features](advanced_features.md#performance-optimization) → [Troubleshooting](troubleshooting.md#performance-issues)

### By Experience Level
- **Beginner**: [Installation](installation.md) → [Quick Start](quick_start.md) → [User Guide](user_guide.md)
- **Intermediate**: [Examples](examples.md) → [API Reference](api_reference.md) → [Advanced Features](advanced_features.md)
- **Advanced**: [Custom Strategies](advanced_features.md#custom-strategies) → [Performance](advanced_features.md#performance-optimization) → [Troubleshooting](troubleshooting.md)

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

### Proxy Pattern
Wrapper that adds logging, metrics, and auditing to file operations without modifying the core functionality.

## 🔗 External Resources

- [GitHub Repository](https://github.com/mawuva/yapfm) - Source code and issue tracking
- [PyPI Package](https://pypi.org/project/yapfm/) - Package installation
- [Changelog](CHANGELOG.md) - Version history and changes

## 📝 Contributing to Documentation

Found an error or want to improve the documentation? Please:

1. Check the [Contributing Guide](../CONTRIBUTING.md)
2. Open an issue or pull request
3. Follow the documentation style guide

---

*This documentation is automatically generated and updated with each release.*
