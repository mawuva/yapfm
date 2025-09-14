# Configuration Management

## Application Configuration Manager

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

## Dynamic Configuration Updates

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
