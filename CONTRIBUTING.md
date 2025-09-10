# Contributing to YAPFM

Thank you for your interest in contributing to YAPFM! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Types of Contributions](#types-of-contributions)

## 🤝 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful, inclusive, and constructive in all interactions.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/yapfm.git
   cd yapfm
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/mawuva/yapfm.git
   ```

## 🛠️ Development Setup

### 1. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 2. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install
```

### 3. Verify Installation

```bash
# Run tests to ensure everything is working
poetry run pytest

# Run linting
poetry run ruff check .

# Run type checking
poetry run mypy src/
```

## 📝 Contributing Process

### 1. Create a Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/yapfm

# Run specific test files
poetry run pytest tests/strategies/test_json_strategy.py
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```bash
# Examples of good commit messages:
git commit -m "feat: add support for XML file format"
git commit -m "fix: resolve memory leak in proxy pattern"
git commit -m "docs: update API reference for new methods"
git commit -m "test: add unit tests for context manager"
git commit -m "refactor: simplify strategy registration logic"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

## 🎨 Code Style and Standards

### Python Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting and additional formatting
- **MyPy**: Type checking

### Running Code Quality Tools

```bash
# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Fix auto-fixable issues
poetry run ruff check --fix src/ tests/

# Type checking
poetry run mypy src/
```

### Code Style Guidelines

1. **Type Hints**: All functions and methods should have type hints
2. **Docstrings**: Use Google-style docstrings for all public functions/classes
3. **Line Length**: Maximum 88 characters (Black default)
4. **Imports**: Use absolute imports, sort with isort
5. **Naming**: Follow PEP 8 conventions

### Example Code Style

```python
from typing import Any, Dict, Optional

from yapfm.exceptions import FileManagerError


class ExampleClass:
    """Example class demonstrating code style.
    
    This class shows the expected code style for YAPFM contributions.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the example class.
        
        Args:
            name: The name of the instance
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
    
    def process_data(self, data: Dict[str, Any]) -> bool:
        """Process the given data.
        
        Args:
            data: The data to process
            
        Returns:
            True if processing was successful
            
        Raises:
            FileManagerError: If processing fails
        """
        if not data:
            raise FileManagerError("Data cannot be empty")
        
        # Process the data
        return True
```

## 🧪 Testing

### Test Structure

Tests are organized in the `tests/` directory mirroring the source structure:

```
tests/
├── helpers/
│   ├── test_dict_utils.py
│   ├── test_io.py
│   └── test_validation.py
├── mixins/
│   ├── test_context_mixin.py
│   ├── test_file_operations_mixin.py
│   └── test_key_operations_mixin.py
├── strategies/
│   ├── test_base.py
│   ├── test_json_strategy.py
│   └── test_toml_strategy.py
└── test_proxy.py
```

### Writing Tests

1. **Test Coverage**: Aim for high test coverage (90%+)
2. **Test Naming**: Use descriptive test names that explain what is being tested
3. **Test Structure**: Follow Arrange-Act-Assert pattern
4. **Fixtures**: Use pytest fixtures for common setup

### Example Test

```python
import pytest
from yapfm import YAPFileManager
from yapfm.exceptions import FileManagerError


class TestYAPFileManager:
    """Test cases for YAPFileManager class."""
    
    def test_set_key_creates_nested_structure(self) -> None:
        """Test that set_key creates nested dictionary structure."""
        # Arrange
        fm = YAPFileManager("test.json")
        fm.load()
        
        # Act
        fm.set_key("localhost", dot_key="database.host")
        
        # Assert
        assert fm.get_key(dot_key="database.host") == "localhost"
        assert fm.get_key(dot_key="database") == {"host": "localhost"}
    
    def test_set_key_raises_error_for_invalid_key(self) -> None:
        """Test that set_key raises error for invalid key format."""
        # Arrange
        fm = YAPFileManager("test.json")
        fm.load()
        
        # Act & Assert
        with pytest.raises(FileManagerError, match="Invalid key format"):
            fm.set_key("value", dot_key="")
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/yapfm --cov-report=html

# Run specific test file
poetry run pytest tests/strategies/test_json_strategy.py

# Run tests with verbose output
poetry run pytest -v

# Run tests matching a pattern
poetry run pytest -k "test_set_key"
```

## 📚 Documentation

### Documentation Structure

Documentation is located in the `docs/` directory:

- `README.md` - Project overview and quick start
- `installation.md` - Installation instructions
- `quick_start.md` - Getting started guide
- `user_guide.md` - Comprehensive usage guide
- `api_reference.md` - Complete API documentation
- `examples.md` - Code examples and patterns
- `advanced_features.md` - Advanced features and patterns
- `troubleshooting.md` - Common issues and solutions
- `roadmap.md` - Future plans and features

### Writing Documentation

1. **Markdown**: Use standard Markdown with GitHub-flavored extensions
2. **Code Examples**: Include working code examples
3. **Cross-references**: Link between related documentation sections
4. **Updates**: Update documentation when adding new features

### Building Documentation

```bash
# Build documentation locally
poetry run mkdocs serve

# Build static documentation
poetry run mkdocs build
```

## 🚀 Release Process

### Version Management

We use [Commitizen](https://commitizen-tools.github.io/commitizen/) for version management:

```bash
# Bump version (patch, minor, or major)
poetry run cz bump

# Check current version
poetry run cz version
```

### Release Checklist

1. ✅ All tests pass
2. ✅ Documentation is updated
3. ✅ CHANGELOG.md is updated
4. ✅ Version is bumped
5. ✅ Pull request is approved and merged
6. ✅ GitHub release is created
7. ✅ Package is published to PyPI

## 🎯 Types of Contributions

### 🐛 Bug Fixes

- Fix existing functionality that's not working correctly
- Include tests that reproduce the bug
- Ensure the fix doesn't break existing functionality

### ✨ New Features

- Add new functionality to the library
- Follow the existing architecture patterns
- Include comprehensive tests
- Update documentation

### 📚 Documentation

- Improve existing documentation
- Add missing documentation
- Fix typos or unclear explanations
- Add examples and tutorials

### 🧪 Tests

- Add missing test coverage
- Improve existing tests
- Add integration tests
- Add performance tests

### 🔧 Refactoring

- Improve code structure without changing functionality
- Optimize performance
- Improve type hints
- Simplify complex code

### 🎨 Code Quality

- Fix linting issues
- Improve code style
- Add type hints
- Optimize imports

## 📞 Getting Help

If you need help or have questions:

1. **Check the documentation** in the `docs/` directory
2. **Search existing issues** on GitHub
3. **Create a new issue** if your question isn't answered
4. **Join discussions** in GitHub Discussions

## 🙏 Recognition

Contributors will be recognized in:
- The project's README.md
- Release notes
- GitHub contributors list

Thank you for contributing to YAPFM! 🎉
