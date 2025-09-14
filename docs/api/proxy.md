# Proxy

The `FileManagerProxy` provides powerful capabilities for monitoring, logging, and auditing file operations without modifying the core functionality.

## FileManagerProxy

Proxy wrapper that adds logging, metrics, and auditing capabilities.

```python
from yapfm import FileManagerProxy
```

### Constructor

```python
FileManagerProxy(
    manager: Any,
    *,
    enable_logging: bool = False,
    enable_metrics: bool = False,
    enable_audit: bool = False,
    logger: Optional[logging.Logger] = None,
    audit_hook: Optional[Callable[[str, tuple, dict, Any], None]] = None
) -> None
```

**Parameters:**
- `manager` (Any): The underlying FileManager instance to proxy
- `enable_logging` (bool): Enable debug logging of method calls and results. Default: False
- `enable_metrics` (bool): Enable execution time measurement. Default: False
- `enable_audit` (bool): Enable audit hook execution. Default: False
- `logger` (Optional[logging.Logger]): Custom logger. Defaults to `logging.getLogger(__name__)`
- `audit_hook` (Optional[Callable]): Custom hook called as `audit_hook(method: str, args: tuple, kwargs: dict, result: Any)`

**Example:**
```python
from yapfm import YAPFileManager, FileManagerProxy
import logging

# Create file manager
fm = YAPFileManager("config.json")

# Create proxy with logging and metrics
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True,
    enable_audit=True
)

# Use proxy like the original manager
with proxy:
    proxy.set_key("value", dot_key="key")
```

### Features

The proxy automatically wraps all method calls to the underlying file manager and provides:

- **Logging**: Debug logging of method calls and results
- **Metrics**: Execution time measurement for performance monitoring
- **Audit**: Custom hook execution for tracking operations
- **Transparency**: All methods are proxied transparently

### Usage Patterns

#### Basic Monitoring

```python
# Create proxy with basic monitoring
proxy = FileManagerProxy(
    fm,
    enable_logging=True,
    enable_metrics=True
)

# All operations are logged and measured
with proxy:
    proxy.set_key("value", dot_key="key")
    data = proxy.get_key(dot_key="key")
```

#### Custom Audit Hooks

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

#### Production Monitoring

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
