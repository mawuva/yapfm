# Logging and Monitoring

## Configuration with Proxy and Logging

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
