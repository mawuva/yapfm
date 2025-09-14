# Proxy Pattern

The `FileManagerProxy` provides powerful capabilities for monitoring, logging, and auditing file operations without modifying the core functionality.

## Basic Proxy Usage

```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_proxy")

# Create file manager
fm = YAPFileManager("config.json", auto_create=True)

# Create proxy with monitoring
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True,
    logger=logger
)

# Use proxy like the original manager
with proxy:
    proxy.set_key("value", dot_key="key")
    # All operations are logged and measured
```

## Custom Audit Hooks

```python
def custom_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    """Custom audit hook for tracking configuration changes."""
    print(f"🔍 AUDIT: {method} called with {args}, {kwargs} => {result}")
    
    # Track specific operations
    if method == "set_key":
        key = args[1] if len(args) > 1 else kwargs.get('dot_key', 'unknown')
        value = args[0] if len(args) > 0 else 'unknown'
        print(f"Configuration changed: {key} = {value}")
    
    elif method == "delete_key":
        key = args[0] if len(args) > 0 else kwargs.get('dot_key', 'unknown')
        print(f"Configuration deleted: {key}")

# Use custom audit hook
proxy = FileManagerProxy(
    fm,
    enable_audit=True,
    audit_hook=custom_audit_hook
)
```

## Metrics Collection

```python
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.operation_times = defaultdict(list)
        self.operation_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    def collect_metrics(self, method: str, args: tuple, kwargs: dict, result: Any, execution_time: float) -> None:
        """Collect metrics for operations."""
        self.operation_times[method].append(execution_time)
        self.operation_counts[method] += 1
        
        if isinstance(result, Exception):
            self.error_counts[method] += 1
    
    def get_stats(self) -> dict:
        """Get collected statistics."""
        stats = {}
        for method, times in self.operation_times.items():
            stats[method] = {
                "count": self.operation_counts[method],
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "errors": self.error_counts[method]
            }
        return stats

# Use metrics collector
metrics = MetricsCollector()

def metrics_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    # This would be called by the proxy with execution time
    pass

proxy = FileManagerProxy(
    fm,
    enable_metrics=True,
    enable_audit=True,
    audit_hook=metrics_audit_hook
)
```

## Production Monitoring

```python
import json
from datetime import datetime
from typing import Dict, Any

class ProductionMonitor:
    def __init__(self, log_file: str = "config_operations.log"):
        self.log_file = log_file
        self.operations = []
    
    def log_operation(self, method: str, args: tuple, kwargs: dict, result: Any, execution_time: float) -> None:
        """Log operation for production monitoring."""
        operation = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "args": str(args),
            "kwargs": str(kwargs),
            "result_type": type(result).__name__,
            "execution_time_ms": execution_time * 1000,
            "success": not isinstance(result, Exception)
        }
        
        self.operations.append(operation)
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(operation) + "\n")
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of operations."""
        if not self.operations:
            return {}
        
        total_operations = len(self.operations)
        successful_operations = sum(1 for op in self.operations if op["success"])
        avg_execution_time = sum(op["execution_time_ms"] for op in self.operations) / total_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations,
            "average_execution_time_ms": avg_execution_time
        }

# Use production monitor
monitor = ProductionMonitor()

def monitor_audit_hook(method: str, args: tuple, kwargs: dict, result: Any) -> None:
    # This would be called by the proxy with execution time
    pass

proxy = FileManagerProxy(
    fm,
    enable_metrics=True,
    enable_audit=True,
    audit_hook=monitor_audit_hook
)
```
