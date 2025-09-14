# Installation Guide

This guide covers how to install YAPFM and its dependencies on different platforms.

## 📋 Requirements

### Python Version
- **Python 3.10+** (tested up to Python 3.13)
- **pip** or **Poetry** for package management

### Dependencies
- `tomlkit` (>=0.13.3,<0.14.0) - TOML file handling
- `pyyaml` (>=6.0.2,<7.0.0) - YAML file handling

*Note: JSON support uses Python's built-in `json` module, so no additional dependencies are required.*

## 🚀 Installation Methods

### Method 1: pip (Recommended)

```bash
# Install the latest version
pip install yapfm

# Install a specific version
pip install yapfm==1.0.0

# Install with development dependencies
pip install yapfm[dev]
```

### Method 2: Poetry

```bash
# Add to your project
poetry add yapfm

# Add development dependencies
poetry add --group dev yapfm
```

### Method 3: From Source

```bash
# Clone the repository
git clone https://github.com/mawuva/yapfm.git
cd yapfm

# Install in development mode
pip install -e .

# Or with Poetry
poetry install
```

## 🔧 Platform-Specific Instructions

### Windows

```powershell
# Using PowerShell
pip install yapfm

# Verify installation
python -c "import yapfm; print(yapfm.__version__)"
```

### macOS

```bash
# Using Homebrew Python
brew install python
pip3 install yapfm

# Or using system Python
python3 -m pip install yapfm
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip if not already installed
sudo apt install python3 python3-pip

# Install YAPFM
pip3 install yapfm
```

### Linux (CentOS/RHEL)

```bash
# Install Python and pip
sudo yum install python3 python3-pip

# Install YAPFM
pip3 install yapfm
```

## 🐳 Docker Installation

### Using Dockerfile

```dockerfile
FROM python:3.11-slim

# Install YAPFM
RUN pip install yapfm

# Your application code here
COPY . /app
WORKDIR /app
```

### Using Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./config:/app/config
```

## 🔍 Verification

After installation, verify that YAPFM is working correctly:

```python
# test_installation.py
from yapfm import YAPFileManager, FileManagerProxy, FileStrategyRegistry

# Test basic functionality
fm = YAPFileManager("test.json")
print("✅ YAPFileManager imported successfully")

# Test proxy
proxy = FileManagerProxy(fm)
print("✅ FileManagerProxy imported successfully")

# Test registry
strategies = FileStrategyRegistry.get_supported_formats()
print(f"✅ Supported formats: {strategies}")

print("🎉 YAPFM installation verified!")
```

Run the test:

```bash
python test_installation.py
```

## 🛠️ Development Setup

If you're contributing to YAPFM or want to run the tests:

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/mawuva/yapfm.git
cd yapfm

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Or with Poetry
poetry install --with dev
```

### Development Dependencies

The development dependencies include:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `ruff` - Linting and formatting
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking
- `pre-commit` - Git hooks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yapfm

# Run specific test file
pytest tests/test_manager.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## 🚨 Troubleshooting

### Common Installation Issues

#### 1. Permission Denied

```bash
# Use --user flag
pip install --user yapfm

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install yapfm
```

#### 2. TOML Dependencies Issues

```bash
# Update pip first
pip install --upgrade pip

# Install with specific TOML version
pip install tomlkit==0.13.3
pip install yapfm
```

#### 3. YAML Dependencies Issues

```bash
# Install PyYAML separately
pip install pyyaml>=6.0.2
pip install yapfm
```

#### 4. Python Version Issues

```bash
# Check Python version
python --version

# Use specific Python version
python3.10 -m pip install yapfm
```

### Platform-Specific Issues

#### Windows: Microsoft Visual C++ 14.0 Required

If you encounter this error, install Visual Studio Build Tools:

1. Download from [Microsoft's website](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install "C++ build tools"
3. Restart your terminal
4. Try installing again

#### macOS: Xcode Command Line Tools

```bash
# Install Xcode command line tools
xcode-select --install

# Then install YAPFM
pip install yapfm
```

#### Linux: Missing Development Headers

```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc
```

## 📦 Virtual Environments

### Using venv

```bash
# Create virtual environment
python -m venv yapfm-env

# Activate (Linux/macOS)
source yapfm-env/bin/activate

# Activate (Windows)
yapfm-env\Scripts\activate

# Install YAPFM
pip install yapfm

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n yapfm-env python=3.11

# Activate environment
conda activate yapfm-env

# Install YAPFM
pip install yapfm
```

## 🔄 Upgrading

### Upgrade to Latest Version

```bash
# Using pip
pip install --upgrade yapfm

# Using Poetry
poetry update yapfm
```

### Check Current Version

```python
import yapfm
print(yapfm.__version__)
```

## 📝 Next Steps

After successful installation:

1. Read the [Quick Start Guide](quick_start.md)
2. Follow the [User Guide](user_guide/index.md)
3. Explore [Examples](usage_examples/index.md)
4. Check the [API Reference](api/index.md)

---

*Having trouble with installation? Check our [Troubleshooting Guide](troubleshooting/index.md) or open an issue on GitHub.*
