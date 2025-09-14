# Frequently Asked Questions

## Q: How do I handle large configuration files?

**A**: Use streaming and chunked processing:

```python
# For very large files, process in chunks
def process_large_config(fm):
    with fm:
        data = fm.data
        
        # Process in chunks
        chunk_size = 1000
        items = list(data.items())
        
        for i in range(0, len(items), chunk_size):
            chunk = dict(items[i:i + chunk_size])
            process_chunk(chunk)
```

## Q: Can I use YAPFM with multiple file formats in the same application?

**A**: Yes, you can use different file managers for different formats:

```python
# Different file managers for different formats
json_fm = YAPFileManager("config.json")
toml_fm = YAPFileManager("config.toml")
yaml_fm = YAPFileManager("config.yaml")

# Or use a single manager with different files
configs = {
    "json": YAPFileManager("config.json"),
    "toml": YAPFileManager("config.toml"),
    "yaml": YAPFileManager("config.yaml")
}
```

## Q: How do I handle configuration validation?

**A**: Use a validation mixin or custom validation:

```python
class ConfigValidator:
    def __init__(self, fm):
        self.fm = fm
        self.rules = {}
    
    def add_rule(self, key, rule, message):
        self.rules[key] = {"rule": rule, "message": message}
    
    def validate(self):
        errors = []
        with self.fm:
            data = self.fm.data
            
            for key, rule_info in self.rules.items():
                if not rule_info["rule"](data.get(key)):
                    errors.append(rule_info["message"])
        
        return errors
```

## Q: Can I use YAPFM in a multi-threaded environment?

**A**: Yes, but you need to handle thread safety:

```python
import threading

# Use locks for thread safety
lock = threading.Lock()

def thread_safe_operation(fm):
    with lock:
        fm.set_key("value", dot_key="key")

# Or use a thread-safe wrapper
class ThreadSafeFileManager:
    def __init__(self, path):
        self.fm = YAPFileManager(path)
        self.lock = threading.RLock()
    
    def __getattr__(self, name):
        attr = getattr(self.fm, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                with self.lock:
                    return attr(*args, **kwargs)
            return wrapper
        return attr
```

## Q: How do I handle configuration updates in production?

**A**: Use safe update patterns:

```python
def safe_config_update(fm, updates):
    # Create backup
    backup_file = f"{fm.path}.backup"
    if fm.exists():
        import shutil
        shutil.copy2(fm.path, backup_file)
    
    try:
        # Apply updates
        with fm:
            for key, value in updates.items():
                fm.set_key(value, dot_key=key)
        
        # Validate configuration
        if validate_config(fm.data):
            fm.save()
        else:
            raise ValueError("Configuration validation failed")
    
    except Exception as e:
        # Restore from backup
        if os.path.exists(backup_file):
            import shutil
            shutil.copy2(backup_file, fm.path)
        raise e
```

## Q: How do I monitor configuration changes?

**A**: Use the proxy pattern with audit hooks:

```python
def audit_hook(method, args, kwargs, result):
    print(f"Configuration changed: {method} with {args}")
    
    # Log to file
    with open("config_changes.log", "a") as f:
        f.write(f"{datetime.now()}: {method} - {args}\n")

proxy = FileManagerProxy(
    fm,
    enable_audit=True,
    audit_hook=audit_hook
)
```

## Q: How do I handle configuration encryption?

**A**: Use a custom mixin or wrapper:

```python
from cryptography.fernet import Fernet

class EncryptedFileManager:
    def __init__(self, path, key):
        self.fm = YAPFileManager(path)
        self.cipher = Fernet(key)
    
    def set_encrypted_key(self, value, dot_key):
        encrypted = self.cipher.encrypt(value.encode())
        self.fm.set_key(encrypted.decode(), dot_key=dot_key)
    
    def get_encrypted_key(self, dot_key, default=None):
        encrypted = self.fm.get_key(dot_key=dot_key, default=default)
        if encrypted:
            return self.cipher.decrypt(encrypted.encode()).decode()
        return default
```

---

*If you're still experiencing issues, please check the [GitHub Issues](https://github.com/mawuva/yapfm/issues) or create a new issue with detailed information about your problem.*
