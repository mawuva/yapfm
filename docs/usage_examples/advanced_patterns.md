# Advanced Patterns

## Configuration Validation and Schema

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

## Configuration Caching and Hot Reloading

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
