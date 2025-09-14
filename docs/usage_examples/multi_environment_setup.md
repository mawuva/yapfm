# Multi-Environment Setup

## Environment-Specific Configuration

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

## Configuration Inheritance

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
