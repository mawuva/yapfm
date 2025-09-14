# Common Patterns

## 1. Configuration Management

```python
class AppConfig:
    def __init__(self, config_file="config.json"):
        self.fm = YAPFileManager(config_file, auto_create=True)
    
    def load(self):
        """Load configuration with defaults."""
        with self.fm:
            # Set defaults if not present
            defaults = {
                "app.name": "My App",
                "app.version": "1.0.0",
                "database.host": "localhost",
                "database.port": 5432,
                "debug": False
            }
            
            for key, value in defaults.items():
                if not self.fm.has_key(dot_key=key):
                    self.fm.set_key(value, dot_key=key)
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.fm.get_key(dot_key=key, default=default)
    
    def set(self, key, value):
        """Set configuration value."""
        self.fm.set_key(value, dot_key=key)
        self.fm.save()

# Use the configuration manager
config = AppConfig("my_app_config.json")
config.load()
app_name = config.get("app.name")
config.set("debug", True)
```

## 2. Environment-Specific Configuration

```python
import os
from yapfm import YAPFileManager

class EnvironmentConfig:
    def __init__(self, base_config="config.json"):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.config_file = f"config_{self.env}.json"
        self.fm = YAPFileManager(self.config_file, auto_create=True)
    
    def load(self):
        """Load environment-specific configuration."""
        with self.fm:
            # Set environment
            self.fm.set_key(self.env, dot_key="environment")
            
            # Set environment-specific defaults
            if self.env == "development":
                self.fm.set_key(True, dot_key="debug")
                self.fm.set_key("localhost", dot_key="database.host")
            elif self.env == "production":
                self.fm.set_key(False, dot_key="debug")
                self.fm.set_key("prod-db.example.com", dot_key="database.host")
    
    def get_database_url(self):
        """Get database URL for current environment."""
        host = self.fm.get_key(dot_key="database.host")
        port = self.fm.get_key(dot_key="database.port")
        name = self.fm.get_key(dot_key="database.name")
        return f"postgresql://{host}:{port}/{name}"

# Use environment-specific configuration
config = EnvironmentConfig()
config.load()
db_url = config.get_database_url()
```

## 3. Configuration Validation

```python
from yapfm import YAPFileManager

class ConfigValidator:
    def __init__(self, config_file):
        self.fm = YAPFileManager(config_file)
    
    def validate(self):
        """Validate configuration file."""
        errors = []
        
        # Required keys
        required_keys = [
            "app.name",
            "app.version",
            "database.host",
            "database.port"
        ]
        
        for key in required_keys:
            if not self.fm.has_key(dot_key=key):
                errors.append(f"Missing required key: {key}")
        
        # Validate specific values
        if self.fm.has_key(dot_key="database.port"):
            port = self.fm.get_key(dot_key="database.port")
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append("Invalid database port")
        
        if self.fm.has_key(dot_key="debug"):
            debug = self.fm.get_key(dot_key="debug")
            if not isinstance(debug, bool):
                errors.append("Debug flag must be boolean")
        
        return errors
    
    def is_valid(self):
        """Check if configuration is valid."""
        return len(self.validate()) == 0

# Use configuration validator
validator = ConfigValidator("config.json")
if validator.is_valid():
    print("Configuration is valid")
else:
    errors = validator.validate()
    print(f"Configuration errors: {errors}")
```

---

*Ready to explore more advanced features? Check out the [Advanced Features Guide](../advanced/index.md) for proxy patterns, custom strategies, and performance optimization.*
