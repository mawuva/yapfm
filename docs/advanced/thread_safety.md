# Thread Safety

## Thread-Safe File Manager

```python
from yapfm import YAPFileManager
import threading
from typing import Any, Dict, Optional
import time

class ThreadSafeFileManager:
    """Thread-safe wrapper for file manager."""
    
    def __init__(self, path: str, **kwargs):
        self._fm = YAPFileManager(path, **kwargs)
        self._lock = threading.RLock()
        self._readers = 0
        self._writers = 0
        self._read_ready = threading.Condition(self._lock)
        self._write_ready = threading.Condition(self._lock)
    
    def read_operation(self, operation: callable) -> Any:
        """Perform a read operation with reader-writer lock."""
        with self._lock:
            while self._writers > 0:
                self._read_ready.wait()
            self._readers += 1
        
        try:
            return operation(self._fm)
        finally:
            with self._lock:
                self._readers -= 1
                if self._readers == 0:
                    self._write_ready.notify_all()
    
    def write_operation(self, operation: callable) -> Any:
        """Perform a write operation with reader-writer lock."""
        with self._lock:
            while self._readers > 0 or self._writers > 0:
                self._write_ready.wait()
            self._writers += 1
        
        try:
            return operation(self._fm)
        finally:
            with self._lock:
                self._writers -= 1
                self._read_ready.notify_all()
                self._write_ready.notify_all()
    
    def get_key(self, dot_key: str, default: Any = None) -> Any:
        """Thread-safe get key operation."""
        return self.read_operation(lambda fm: fm.get_key(dot_key=dot_key, default=default))
    
    def set_key(self, value: Any, dot_key: str) -> None:
        """Thread-safe set key operation."""
        self.write_operation(lambda fm: fm.set_key(value, dot_key=dot_key))
    
    def load(self) -> None:
        """Thread-safe load operation."""
        self.write_operation(lambda fm: fm.load())
    
    def save(self) -> None:
        """Thread-safe save operation."""
        self.write_operation(lambda fm: fm.save())

# Usage
thread_safe_fm = ThreadSafeFileManager("thread_safe_config.json")

# Multiple threads can safely access the file manager
def reader_thread():
    for i in range(10):
        value = thread_safe_fm.get_key("counter", default=0)
        print(f"Reader: {value}")
        time.sleep(0.1)

def writer_thread():
    for i in range(10):
        thread_safe_fm.set_key(i, "counter")
        print(f"Writer: {i}")
        time.sleep(0.1)

# Start threads
threading.Thread(target=reader_thread).start()
threading.Thread(target=writer_thread).start()
```
