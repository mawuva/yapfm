# Examples and Usage Patterns

This guide provides comprehensive examples and real-world usage patterns for YAPFM, covering everything from basic operations to advanced scenarios.

## 📚 Table of Contents

1. [Basic Examples](#basic-examples)
2. [Configuration Management](#configuration-management)
3. [Multi-Environment Setup](#multi-environment-setup)
4. [Advanced Patterns](#advanced-patterns)
5. [Logging and Monitoring](#logging-and-monitoring)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Integration Examples](#integration-examples)

## 🚀 Basic Examples

### Simple Configuration File

```python
from yapfm import YAPFileManager

# Create a basic configuration file
def create_app_config():
    with YAPFileManager("app_config.json", auto_create=True) as fm:
        # Application settings
        fm.set_key("My Application", dot_key="app.name")
        fm.set_key("1.0.0", dot_key="app.version")
        fm.set_key("production", dot_key="app.environment")
        
        # Database configuration
        fm.set_key("localhost", dot_key="database.host")
        fm.set_key(5432, dot_key="database.port")
        fm.set_key("myapp", dot_key="database.name")
        fm.set_key(True, dot_key="database.ssl")
        
        # API settings
        fm.set_key("v1", dot_key="api.version")
        fm.set_key(30, dot_key="api.timeout")
        fm.set_key(3, dot_key="api.retries")
        
        print("Configuration created successfully!")

# Read configuration
def read_app_config():
    with YAPFileManager("app_config.json") as fm:
        app_name = fm.get_key(dot_key="app.name")
        db_host = fm.get_key(dot_key="database.host")
        api_timeout = fm.get_key(dot_key="api.timeout")
        
        print(f"App: {app_name}")
        print(f"Database: {db_host}")
        print(f"API Timeout: {api_timeout}s")

# Run the examples
create_app_config()
read_app_config()
```

### Working with Different File Formats

#### Using YAPFileManager Directly

```python
from yapfm import YAPFileManager

# JSON configuration
def json_example():
    with YAPFileManager("config.json", auto_create=True) as fm:
        fm.set_key("JSON Config", dot_key="format")
        fm.set_key({"key1": "value1", "key2": "value2"}, dot_key="data")
        print("JSON configuration created")

# TOML configuration
def toml_example():
    with YAPFileManager("config.toml", auto_create=True) as fm:
        fm.set_key("TOML Config", dot_key="format")
        fm.set_key("localhost", dot_key="server.host")
        fm.set_key(8000, dot_key="server.port")
        print("TOML configuration created")

# YAML configuration
def yaml_example():
    with YAPFileManager("config.yaml", auto_create=True) as fm:
        fm.set_key("YAML Config", dot_key="format")
        fm.set_key(["item1", "item2", "item3"], dot_key="items")
        print("YAML configuration created")

# Run all examples
json_example()
toml_example()
yaml_example()
```

#### Using the open_file Helper

```python
from yapfm.helpers import open_file

# Open files with automatic format detection
def open_file_examples():
    # JSON file
    json_fm = open_file("config.json", auto_create=True)
    with json_fm:
        json_fm.set_key("JSON Config", dot_key="format")
        json_fm.set_key({"key1": "value1", "key2": "value2"}, dot_key="data")
    
    # TOML file
    toml_fm = open_file("config.toml", auto_create=True)
    with toml_fm:
        toml_fm.set_key("TOML Config", dot_key="format")
        toml_fm.set_key("localhost", dot_key="server.host")
        toml_fm.set_key(8000, dot_key="server.port")
    
    # YAML file
    yaml_fm = open_file("config.yaml", auto_create=True)
    with yaml_fm:
        yaml_fm.set_key("YAML Config", dot_key="format")
        yaml_fm.set_key(["item1", "item2", "item3"], dot_key="items")
    
    print("All configurations created using open_file helper")

# Format override examples
def format_override_examples():
    # Force JSON format regardless of file extension
    json_fm = open_file("config.txt", format="json", auto_create=True)
    with json_fm:
        json_fm.set_key("Forced JSON", dot_key="format")
    
    # Force TOML format
    toml_fm = open_file("settings.dat", format="toml", auto_create=True)
    with toml_fm:
        toml_fm.set_key("Forced TOML", dot_key="format")
    
    # Force YAML format
    yaml_fm = open_file("data.log", format="yaml", auto_create=True)
    with yaml_fm:
        yaml_fm.set_key("Forced YAML", dot_key="format")
    
    print("Format override examples completed")

# Run examples
open_file_examples()
format_override_examples()
```

## ⚙️ Configuration Management

### Application Configuration Manager

```python
from yapfm import YAPFileManager
from typing import Dict, Any, Optional
import os

class AppConfig:
    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = config_file
        self.fm = YAPFileManager(config_file, auto_create=True)
    
    def load(self) -> None:
        """Load configuration with defaults."""
        with self.fm:
            # Set application defaults
            defaults = {
                "app.name": "My Application",
                "app.version": "1.0.0",
                "app.environment": "development",
                "app.debug": False,
                "database.host": "localhost",
                "database.port": 5432,
                "database.name": "myapp",
                "database.ssl": False,
                "api.version": "v1",
                "api.timeout": 30,
                "api.retries": 3,
                "logging.level": "INFO",
                "logging.file": "app.log"
            }
            
            # Set defaults for missing keys
            for key, value in defaults.items():
                if not self.fm.has_key(dot_key=key):
                    self.fm.set_key(value, dot_key=key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.fm.get_key(dot_key=key, default=default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.fm.set_key(value, dot_key=key)
        self.fm.save()
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get an entire configuration section."""
        return self.fm.get_section(dot_key=section)
    
    def set_section(self, section: str, data: Dict[str, Any]) -> None:
        """Set an entire configuration section."""
        self.fm.set_section(data, dot_key=section)
        self.fm.save()
    
    def validate(self) -> bool:
        """Validate required configuration keys."""
        required_keys = [
            "app.name",
            "app.version",
            "database.host",
            "database.port"
        ]
        
        for key in required_keys:
            if not self.fm.has_key(dot_key=key):
                print(f"Missing required configuration key: {key}")
                return False
        
        return True

# Usage example
def main():
    config = AppConfig("my_app_config.json")
    config.load()
    
    if config.validate():
        print("Configuration is valid")
        print(f"App: {config.get('app.name')}")
        print(f"Database: {config.get('database.host')}:{config.get('database.port')}")
    else:
        print("Configuration validation failed")

if __name__ == "__main__":
    main()
```

### Dynamic Configuration Updates

```python
from yapfm import YAPFileManager
import time
from typing import Dict, Any

class DynamicConfig:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.fm = YAPFileManager(config_file, auto_create=True)
        self.last_modified = 0
    
    def load(self) -> Dict[str, Any]:
        """Load configuration and track modifications."""
        with self.fm:
            self.last_modified = time.time()
            return self.fm.data
    
    def update_feature_flag(self, feature: str, enabled: bool) -> None:
        """Update a feature flag."""
        with self.fm:
            self.fm.set_key(enabled, dot_key=f"features.{feature}")
            self.fm.set_key(time.time(), dot_key="last_updated")
    
    def update_limits(self, limits: Dict[str, int]) -> None:
        """Update application limits."""
        with self.fm:
            for key, value in limits.items():
                self.fm.set_key(value, dot_key=f"limits.{key}")
            self.fm.set_key(time.time(), dot_key="last_updated")
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags."""
        return self.fm.get_section(dot_key="features") or {}
    
    def get_limits(self) -> Dict[str, int]:
        """Get all limits."""
        return self.fm.get_section(dot_key="limits") or {}

# Usage example
def main():
    config = DynamicConfig("dynamic_config.json")
    
    # Load initial configuration
    config.load()
    
    # Update feature flags
    config.update_feature_flag("new_ui", True)
    config.update_feature_flag("beta_features", False)
    
    # Update limits
    config.update_limits({
        "max_users": 1000,
        "max_requests_per_hour": 10000,
        "max_file_size_mb": 10
    })
    
    # Check current settings
    features = config.get_feature_flags()
    limits = config.get_limits()
    
    print("Feature Flags:", features)
    print("Limits:", limits)

if __name__ == "__main__":
    main()
```

## 🌍 Multi-Environment Setup

### Environment-Specific Configuration

```python
from yapfm import YAPFileManager
import os
from typing import Dict, Any

class EnvironmentConfig:
    def __init__(self, base_config: str = "config.json"):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.config_file = f"config_{self.environment}.json"
        self.fm = YAPFileManager(self.config_file, auto_create=True)
    
    def load(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        with self.fm:
            # Set environment
            self.fm.set_key(self.environment, dot_key="environment")
            
            # Set environment-specific defaults
            if self.environment == "development":
                self._set_development_defaults()
            elif self.environment == "staging":
                self._set_staging_defaults()
            elif self.environment == "production":
                self._set_production_defaults()
            
            return self.fm.data
    
    def _set_development_defaults(self) -> None:
        """Set development environment defaults."""
        defaults = {
            "debug": True,
            "database.host": "localhost",
            "database.port": 5432,
            "database.ssl": False,
            "api.timeout": 60,
            "api.debug": True,
            "logging.level": "DEBUG",
            "logging.console": True,
            "cors.origins": ["http://localhost:3000", "http://localhost:8080"]
        }
        
        for key, value in defaults.items():
            if not self.fm.has_key(dot_key=key):
                self.fm.set_key(value, dot_key=key)
    
    def _set_staging_defaults(self) -> None:
        """Set staging environment defaults."""
        defaults = {
            "debug": False,
            "database.host": "staging-db.example.com",
            "database.port": 5432,
            "database.ssl": True,
            "api.timeout": 30,
            "api.debug": False,
            "logging.level": "INFO",
            "logging.console": False,
            "cors.origins": ["https://staging.demo.example.com"]
        }
        
        for key, value in defaults.items():
            if not self.fm.has_key(dot_key=key):
                self.fm.set_key(value, dot_key=key)
    
    def _set_production_defaults(self) -> None:
        """Set production environment defaults."""
        defaults = {
            "debug": False,
            "database.host": "prod-db.example.com",
            "database.port": 3306,
            "database.ssl": True,
            "api.timeout": 15,
            "api.debug": False,
            "logging.level": "WARNING",
            "logging.console": False,
            "cors.origins": ["https://demo.example.com"]
        }
        
        for key, value in defaults.items():
            if not self.fm.has_key(dot_key=key):
                self.fm.set_key(value, dot_key=key)
    
    def get_database_url(self) -> str:
        """Get database URL for current environment."""
        host = self.fm.get_key(dot_key="database.host")
        port = self.fm.get_key(dot_key="database.port")
        name = self.fm.get_key(dot_key="database.name", default="myapp")
        ssl = self.fm.get_key(dot_key="database.ssl", default=False)
        
        protocol = "postgresql+ssl" if ssl else "postgresql"
        return f"{protocol}://{host}:{port}/{name}"
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration for current environment."""
        return {
            "version": self.fm.get_key(dot_key="api.version", default="v1"),
            "timeout": self.fm.get_key(dot_key="api.timeout", default=30),
            "debug": self.fm.get_key(dot_key="api.debug", default=False),
            "cors": {
                "origins": self.fm.get_key(dot_key="cors.origins", default=[])
            }
        }

# Usage example
def main():
    # Set environment (usually done via environment variable)
    os.environ["ENVIRONMENT"] = "development"
    
    config = EnvironmentConfig()
    config.load()
    
    print(f"Environment: {config.environment}")
    print(f"Database URL: {config.get_database_url()}")
    print(f"API Config: {config.get_api_config()}")

if __name__ == "__main__":
    main()
```

### Configuration Inheritance

```python
from yapfm import YAPFileManager
from typing import Dict, Any, Optional

class ConfigInheritance:
    def __init__(self, base_config: str = "base_config.json"):
        self.base_config = base_config
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.env_config = f"config_{self.environment}.json"
    
    def load_merged_config(self) -> Dict[str, Any]:
        """Load and merge base and environment-specific configuration."""
        # Load base configuration
        base_fm = YAPFileManager(self.base_config, auto_create=True)
        with base_fm:
            base_data = base_fm.data.copy()
        
        # Load environment-specific configuration
        env_fm = YAPFileManager(self.env_config, auto_create=True)
        with env_fm:
            env_data = env_fm.data
        
        # Merge configurations (environment overrides base)
        merged_config = self._deep_merge(base_data, env_data)
        
        # Save merged configuration
        merged_fm = YAPFileManager("merged_config.json", auto_create=True)
        with merged_fm:
            merged_fm.data = merged_config
        
        return merged_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

# Usage example
def main():
    config_manager = ConfigInheritance()
    merged_config = config_manager.load_merged_config()
    
    print("Merged Configuration:")
    print(f"Environment: {merged_config.get('environment')}")
    print(f"Database: {merged_config.get('database', {}).get('host')}")
    print(f"API: {merged_config.get('api', {}).get('timeout')}")

if __name__ == "__main__":
    main()
```

## 🎨 Advanced Patterns

### Configuration Validation and Schema

```python
from yapfm import YAPFileManager
from typing import Dict, Any, List, Optional, Union
import re

class ConfigValidator:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.fm = YAPFileManager(config_file, auto_create=True)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """Validate configuration against schema."""
        self.errors.clear()
        self.warnings.clear()
        
        with self.fm:
            # Validate required keys
            self._validate_required_keys()
            
            # Validate data types
            self._validate_data_types()
            
            # Validate value ranges
            self._validate_value_ranges()
            
            # Validate string formats
            self._validate_string_formats()
        
        return len(self.errors) == 0
    
    def _validate_required_keys(self) -> None:
        """Validate that all required keys are present."""
        required_keys = [
            "app.name",
            "app.version",
            "database.host",
            "database.port",
            "api.timeout"
        ]
        
        for key in required_keys:
            if not self.fm.has_key(dot_key=key):
                self.errors.append(f"Missing required key: {key}")
    
    def _validate_data_types(self) -> None:
        """Validate data types of configuration values."""
        type_validations = {
            "app.name": str,
            "app.version": str,
            "database.port": int,
            "api.timeout": int,
            "api.retries": int,
            "debug": bool
        }
        
        for key, expected_type in type_validations.items():
            if self.fm.has_key(dot_key=key):
                value = self.fm.get_key(dot_key=key)
                if not isinstance(value, expected_type):
                    self.errors.append(f"Key '{key}' should be {expected_type.__name__}, got {type(value).__name__}")
    
    def _validate_value_ranges(self) -> None:
        """Validate value ranges for numeric configuration."""
        range_validations = {
            "database.port": (1, 65535),
            "api.timeout": (1, 300),
            "api.retries": (0, 10)
        }
        
        for key, (min_val, max_val) in range_validations.items():
            if self.fm.has_key(dot_key=key):
                value = self.fm.get_key(dot_key=key)
                if isinstance(value, (int, float)):
                    if not (min_val <= value <= max_val):
                        self.errors.append(f"Key '{key}' value {value} is out of range [{min_val}, {max_val}]")
    
    def _validate_string_formats(self) -> None:
        """Validate string formats for configuration values."""
        format_validations = {
            "app.version": r"^\d+\.\d+\.\d+$",  # Semantic versioning
            "database.host": r"^[a-zA-Z0-9.-]+$",  # Hostname format
            "api.version": r"^v\d+$"  # API version format
        }
        
        for key, pattern in format_validations.items():
            if self.fm.has_key(dot_key=key):
                value = self.fm.get_key(dot_key=key)
                if isinstance(value, str):
                    if not re.match(pattern, value):
                        self.errors.append(f"Key '{key}' value '{value}' does not match expected format")
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings
    
    def fix_common_issues(self) -> bool:
        """Attempt to fix common configuration issues."""
        fixed = False
        
        with self.fm:
            # Fix missing required keys with defaults
            defaults = {
                "app.name": "My Application",
                "app.version": "1.0.0",
                "database.host": "localhost",
                "database.port": 5432,
                "api.timeout": 30
            }
            
            for key, default_value in defaults.items():
                if not self.fm.has_key(dot_key=key):
                    self.fm.set_key(default_value, dot_key=key)
                    fixed = True
        
        return fixed

# Usage example
def main():
    validator = ConfigValidator("app_config.json")
    
    # Try to fix common issues
    if validator.fix_common_issues():
        print("Fixed some common configuration issues")
    
    # Validate configuration
    if validator.validate():
        print("Configuration is valid!")
    else:
        print("Configuration validation failed:")
        for error in validator.get_errors():
            print(f"  - {error}")

if __name__ == "__main__":
    main()
```

### Configuration Caching and Hot Reloading

```python
from yapfm import YAPFileManager
import time
import threading
from typing import Dict, Any, Callable, Optional

class ConfigCache:
    def __init__(self, config_file: str, reload_interval: int = 30):
        self.config_file = config_file
        self.reload_interval = reload_interval
        self.fm = YAPFileManager(config_file, auto_create=True)
        self.cache: Dict[str, Any] = {}
        self.last_reload = 0
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._stop_reload = False
        self._reload_thread: Optional[threading.Thread] = None
    
    def start_auto_reload(self) -> None:
        """Start automatic configuration reloading."""
        if self._reload_thread is None or not self._reload_thread.is_alive():
            self._stop_reload = False
            self._reload_thread = threading.Thread(target=self._auto_reload_loop)
            self._reload_thread.daemon = True
            self._reload_thread.start()
    
    def stop_auto_reload(self) -> None:
        """Stop automatic configuration reloading."""
        self._stop_reload = True
        if self._reload_thread and self._reload_thread.is_alive():
            self._reload_thread.join()
    
    def _auto_reload_loop(self) -> None:
        """Background thread for automatic reloading."""
        while not self._stop_reload:
            time.sleep(self.reload_interval)
            if self._should_reload():
                self.reload()
    
    def _should_reload(self) -> bool:
        """Check if configuration should be reloaded."""
        if not self.fm.exists():
            return False
        
        try:
            stat = self.fm.path.stat()
            return stat.st_mtime > self.last_reload
        except OSError:
            return False
    
    def load(self) -> Dict[str, Any]:
        """Load configuration into cache."""
        with self.fm:
            self.cache = self.fm.data.copy()
            self.last_reload = time.time()
            return self.cache
    
    def reload(self) -> Dict[str, Any]:
        """Reload configuration from file."""
        old_cache = self.cache.copy()
        new_cache = self.load()
        
        # Notify callbacks if configuration changed
        if old_cache != new_cache:
            for callback in self.callbacks:
                try:
                    callback(new_cache)
                except Exception as e:
                    print(f"Error in configuration callback: {e}")
        
        return new_cache
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from cache."""
        if not self.cache:
            self.load()
        
        # Navigate through nested keys
        keys = key.split('.')
        value = self.cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback for configuration changes."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Remove a configuration change callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

# Usage example
def config_change_handler(new_config: Dict[str, Any]) -> None:
    """Handle configuration changes."""
    print("Configuration updated!")
    print(f"New app name: {new_config.get('app', {}).get('name')}")

def main():
    cache = ConfigCache("app_config.json", reload_interval=10)
    
    # Add change handler
    cache.add_callback(config_change_handler)
    
    # Load initial configuration
    cache.load()
    
    # Start auto-reload
    cache.start_auto_reload()
    
    try:
        # Use configuration
        for i in range(5):
            app_name = cache.get("app.name", "Unknown")
            print(f"App name: {app_name}")
            time.sleep(5)
    finally:
        # Stop auto-reload
        cache.stop_auto_reload()

if __name__ == "__main__":
    main()
```

## 📊 Logging and Monitoring

### Configuration with Proxy and Logging

```python
from yapfm import YAPFileManager, FileManagerProxy
import logging
import time
from typing import Dict, Any

class MonitoredConfig:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.fm = YAPFileManager(config_file, auto_create=True)
        
        # Set up logging
        self.logger = logging.getLogger("config_monitor")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler("config_operations.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Create proxy with monitoring
        self.proxy = FileManagerProxy(
            self.fm,
            enable_logging=True,
            enable_metrics=True,
            enable_audit=True,
            logger=self.logger,
            audit_hook=self._audit_hook
        )
        
        # Metrics storage
        self.metrics: Dict[str, Any] = {
            "operations": 0,
            "loads": 0,
            "saves": 0,
            "errors": 0
        }
    
    def _audit_hook(self, method: str, args: tuple, kwargs: dict, result: Any) -> None:
        """Custom audit hook for tracking operations."""
        self.metrics["operations"] += 1
        
        if method == "load":
            self.metrics["loads"] += 1
        elif method == "save":
            self.metrics["saves"] += 1
        
        # Log significant operations
        if method in ["set_key", "set_section", "delete_key"]:
            self.logger.info(f"Configuration modified: {method} with args {args}")
    
    def load(self) -> Dict[str, Any]:
        """Load configuration with monitoring."""
        try:
            with self.proxy:
                return self.proxy.data
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def set_key(self, key: str, value: Any) -> None:
        """Set configuration key with monitoring."""
        try:
            with self.proxy:
                self.proxy.set_key(value, dot_key=key)
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Failed to set key {key}: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get operation metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset operation metrics."""
        self.metrics = {
            "operations": 0,
            "loads": 0,
            "saves": 0,
            "errors": 0
        }

# Usage example
def main():
    config = MonitoredConfig("monitored_config.json")
    
    # Load configuration
    config.load()
    
    # Make some changes
    config.set_key("app.name", "Monitored App")
    config.set_key("app.version", "2.0.0")
    config.set_key("database.host", "monitored-db.example.com")
    
    # Check metrics
    metrics = config.get_metrics()
    print("Configuration Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
```

## ⚠️ Error Handling Patterns

### Robust Configuration Loading

```python
from yapfm import YAPFileManager
from yapfm.exceptions import LoadFileError, FileWriteError, StrategyError
import logging
from typing import Dict, Any, Optional

class RobustConfig:
    def __init__(self, config_file: str, fallback_config: Optional[Dict[str, Any]] = None):
        self.config_file = config_file
        self.fallback_config = fallback_config or {}
        self.logger = logging.getLogger("robust_config")
        
    def load_with_fallback(self) -> Dict[str, Any]:
        """Load configuration with fallback to defaults."""
        try:
            # Try to load from file
            fm = YAPFileManager(self.config_file)
            with fm:
                return fm.data
        except LoadFileError as e:
            self.logger.warning(f"Failed to load config file: {e}")
            return self._create_fallback_config()
        except StrategyError as e:
            self.logger.error(f"Unsupported file format: {e}")
            return self._create_fallback_config()
        except Exception as e:
            self.logger.error(f"Unexpected error loading config: {e}")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> Dict[str, Any]:
        """Create fallback configuration."""
        self.logger.info("Creating fallback configuration")
        
        fallback = {
            "app": {
                "name": "Fallback App",
                "version": "1.0.0",
                "environment": "fallback"
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "fallback_db"
            },
            "api": {
                "timeout": 30,
                "retries": 3
            }
        }
        
        # Merge with provided fallback
        fallback.update(self.fallback_config)
        
        # Save fallback config
        try:
            fm = YAPFileManager(self.config_file, auto_create=True)
            with fm:
                fm.data = fallback
        except Exception as e:
            self.logger.error(f"Failed to save fallback config: {e}")
        
        return fallback
    
    def safe_save(self, data: Dict[str, Any]) -> bool:
        """Safely save configuration with backup."""
        try:
            # Create backup
            backup_file = f"{self.config_file}.backup"
            if self.fm.exists():
                import shutil
                shutil.copy2(self.config_file, backup_file)
            
            # Save new configuration
            fm = YAPFileManager(self.config_file)
            with fm:
                fm.data = data
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except FileWriteError as e:
            self.logger.error(f"Failed to save configuration: {e}")
            
            # Try to restore from backup
            try:
                if backup_file and os.path.exists(backup_file):
                    import shutil
                    shutil.copy2(backup_file, self.config_file)
                    self.logger.info("Restored configuration from backup")
            except Exception as restore_error:
                self.logger.error(f"Failed to restore from backup: {restore_error}")
            
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error saving configuration: {e}")
            return False

# Usage example
def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create robust config with fallback
    fallback_config = {
        "app": {"name": "My App", "version": "1.0.0"},
        "database": {"host": "localhost", "port": 5432}
    }
    
    config = RobustConfig("app_config.json", fallback_config)
    
    # Load configuration (will use fallback if file doesn't exist)
    data = config.load_with_fallback()
    print("Loaded configuration:", data)
    
    # Safely save configuration
    data["app"]["version"] = "1.1.0"
    if config.safe_save(data):
        print("Configuration saved successfully")
    else:
        print("Failed to save configuration")

if __name__ == "__main__":
    main()
```

## ⚡ Performance Optimization

### Batch Operations

```python
from yapfm import YAPFileManager
from typing import Dict, Any, List
import time

class BatchConfig:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.fm = YAPFileManager(config_file, auto_create=True)
        self.pending_changes: Dict[str, Any] = {}
    
    def batch_set(self, changes: Dict[str, Any]) -> None:
        """Set multiple configuration values in a single operation."""
        with self.fm:
            with self.fm.lazy_save():
                for key, value in changes.items():
                    self.fm.set_key(value, dot_key=key)
    
    def batch_set_sections(self, sections: Dict[str, Dict[str, Any]]) -> None:
        """Set multiple sections in a single operation."""
        with self.fm:
            with self.fm.lazy_save():
                for section_key, section_data in sections.items():
                    self.fm.set_section(section_data, dot_key=section_key)
    
    def batch_update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values efficiently."""
        with self.fm:
            # Get current data
            current_data = self.fm.data.copy()
            
            # Apply updates
            for key, value in updates.items():
                keys = key.split('.')
                target = current_data
                
                # Navigate to the target location
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                
                # Set the value
                target[keys[-1]] = value
            
            # Save updated data
            self.fm.data = current_data

# Performance comparison example
def performance_comparison():
    config_file = "performance_test.json"
    
    # Individual operations
    start_time = time.time()
    fm = YAPFileManager(config_file, auto_create=True)
    
    with fm:
        for i in range(100):
            fm.set_key(f"value_{i}", dot_key=f"key_{i}")
    
    individual_time = time.time() - start_time
    print(f"Individual operations: {individual_time:.4f} seconds")
    
    # Batch operations
    start_time = time.time()
    batch_config = BatchConfig("performance_test_batch.json")
    
    changes = {f"key_{i}": f"value_{i}" for i in range(100)}
    batch_config.batch_set(changes)
    
    batch_time = time.time() - start_time
    print(f"Batch operations: {batch_time:.4f} seconds")
    
    print(f"Speedup: {individual_time / batch_time:.2f}x")

if __name__ == "__main__":
    performance_comparison()
```

## 🔗 Integration Examples

### Flask Application Integration

```python
from flask import Flask, request, jsonify
from yapfm import YAPFileManager, FileManagerProxy
import logging

app = Flask(__name__)

# Set up configuration
config_fm = YAPFileManager("flask_config.json", auto_create=True)
config_proxy = FileManagerProxy(
    config_fm,
    enable_logging=True,
    enable_metrics=True,
    logger=logging.getLogger("flask_config")
)

@app.route('/config', methods=['GET'])
def get_config():
    """Get application configuration."""
    try:
        with config_proxy:
            return jsonify(config_proxy.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/<path:key>', methods=['GET'])
def get_config_key(key):
    """Get a specific configuration key."""
    try:
        with config_proxy:
            value = config_proxy.get_key(dot_key=key)
            if value is None:
                return jsonify({"error": "Key not found"}), 404
            return jsonify({"key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/<path:key>', methods=['POST'])
def set_config_key(key):
    """Set a specific configuration key."""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Value required"}), 400
        
        with config_proxy:
            config_proxy.set_key(data['value'], dot_key=key)
            return jsonify({"key": key, "value": data['value']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Settings Integration

```python
# settings.py
from yapfm import YAPFileManager
import os

# Load configuration from file
config_fm = YAPFileManager("django_config.json", auto_create=True)

with config_fm:
    # Database configuration
    DATABASES = {
        'default': {
            'ENGINE': config_fm.get_key(dot_key="database.engine", default="django.db.backends.postgresql"),
            'NAME': config_fm.get_key(dot_key="database.name", default="myapp"),
            'USER': config_fm.get_key(dot_key="database.user", default="postgres"),
            'PASSWORD': config_fm.get_key(dot_key="database.password", default=""),
            'HOST': config_fm.get_key(dot_key="database.host", default="localhost"),
            'PORT': config_fm.get_key(dot_key="database.port", default="5432"),
        }
    }
    
    # Debug setting
    DEBUG = config_fm.get_key(dot_key="debug", default=False)
    
    # Secret key
    SECRET_KEY = config_fm.get_key(dot_key="secret_key", default="your-secret-key-here")
    
    # Allowed hosts
    ALLOWED_HOSTS = config_fm.get_key(dot_key="allowed_hosts", default=["localhost"])
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': config_fm.get_key(dot_key="logging.level", default="INFO"),
                'class': 'logging.FileHandler',
                'filename': config_fm.get_key(dot_key="logging.file", default="django.log"),
            },
        },
        'root': {
            'handlers': ['file'],
        },
    }
```

---

*These examples demonstrate the flexibility and power of YAPFM in real-world scenarios. For more advanced features, see the [Advanced Features Guide](advanced_features.md).*
