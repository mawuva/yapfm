# Configuration Problems

## Invalid Configuration Structure

**Problem**: Configuration file has invalid structure.

**Solutions**:
```python
# 1. Validate configuration
def validate_config(data):
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a dictionary")
    
    required_keys = ["app", "database"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    return True

# 2. Use configuration validator
class ConfigValidator:
    def __init__(self, fm):
        self.fm = fm
    
    def validate(self):
        with self.fm:
            return validate_config(self.fm.data)

# 3. Fix common issues
def fix_config_issues(fm):
    with fm:
        data = fm.data
        
        # Ensure top-level is dictionary
        if not isinstance(data, dict):
            fm.data = {"config": data}
        
        # Add missing required keys
        if "app" not in data:
            data["app"] = {"name": "My App", "version": "1.0.0"}
        
        if "database" not in data:
            data["database"] = {"host": "localhost", "port": 5432}
```

## Environment-Specific Issues

**Problem**: Configuration not working in different environments.

**Solutions**:
```python
import os

# 1. Use environment variables
def load_env_config():
    env = os.getenv("ENVIRONMENT", "development")
    config_file = f"config_{env}.json"
    
    fm = YAPFileManager(config_file, auto_create=True)
    with fm:
        # Set environment-specific defaults
        if env == "development":
            fm.set_key(True, dot_key="debug")
        elif env == "production":
            fm.set_key(False, dot_key="debug")
    
    return fm

# 2. Use configuration inheritance
def load_merged_config():
    base_fm = YAPFileManager("base_config.json")
    env_fm = YAPFileManager(f"config_{os.getenv('ENVIRONMENT', 'development')}.json")
    
    with base_fm:
        base_data = base_fm.data
    
    with env_fm:
        env_data = env_fm.data
    
    # Merge configurations
    merged_data = {**base_data, **env_data}
    
    return merged_data
```
