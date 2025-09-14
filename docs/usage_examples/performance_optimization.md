# Performance Optimization

## Batch Operations

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
