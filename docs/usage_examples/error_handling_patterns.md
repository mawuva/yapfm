# Error Handling Patterns

## Robust Configuration Loading

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
