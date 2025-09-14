# Mixins Deep Dive

## Creating Custom Mixins

```python
from yapfm.mixins import FileOperationsMixin
from typing import Any, Dict, List, Optional
import hashlib

class ValidationMixin:
    """Mixin for configuration validation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validation_rules: Dict[str, Any] = {}
        self._validation_errors: List[str] = []
    
    def add_validation_rule(self, key: str, rule: callable, message: str = None) -> None:
        """Add a validation rule for a configuration key."""
        self._validation_rules[key] = {
            "rule": rule,
            "message": message or f"Validation failed for key: {key}"
        }
    
    def validate_key(self, key: str, value: Any) -> bool:
        """Validate a single key."""
        if key not in self._validation_rules:
            return True
        
        rule = self._validation_rules[key]["rule"]
        try:
            result = rule(value)
            if not result:
                self._validation_errors.append(self._validation_rules[key]["message"])
            return result
        except Exception as e:
            self._validation_errors.append(f"Validation error for {key}: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Validate all configuration keys."""
        self._validation_errors.clear()
        
        if not self.is_loaded():
            self.load()
        
        # Validate all keys in the document
        self._validate_dict(self.data, "")
        
        return len(self._validation_errors) == 0
    
    def _validate_dict(self, data: Dict[str, Any], prefix: str) -> None:
        """Recursively validate dictionary data."""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._validate_dict(value, full_key)
            else:
                self.validate_key(full_key, value)
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        return self._validation_errors.copy()
    
    def set_key_with_validation(self, value: Any, dot_key: str) -> bool:
        """Set a key with validation."""
        if self.validate_key(dot_key, value):
            self.set_key(value, dot_key=dot_key)
            return True
        return False

class EncryptionMixin:
    """Mixin for configuration encryption."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._encryption_key: Optional[bytes] = None
    
    def set_encryption_key(self, key: str) -> None:
        """Set encryption key."""
        self._encryption_key = key.encode('utf-8')
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a string value."""
        if not self._encryption_key:
            return value
        
        from cryptography.fernet import Fernet
        f = Fernet(self._encryption_key)
        return f.encrypt(value.encode('utf-8')).decode('utf-8')
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value."""
        if not self._encryption_key:
            return encrypted_value
        
        from cryptography.fernet import Fernet
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    
    def set_encrypted_key(self, value: str, dot_key: str) -> None:
        """Set an encrypted configuration key."""
        encrypted_value = self.encrypt_value(value)
        self.set_key(encrypted_value, dot_key=dot_key)
    
    def get_encrypted_key(self, dot_key: str, default: str = None) -> str:
        """Get and decrypt a configuration key."""
        encrypted_value = self.get_key(dot_key=dot_key, default=default)
        if encrypted_value is None:
            return default
        
        return self.decrypt_value(encrypted_value)

# Create a custom file manager with mixins
class AdvancedFileManager(
    FileOperationsMixin,
    ValidationMixin,
    EncryptionMixin
):
    def __init__(self, path, **kwargs):
        self.path = path
        super().__init__(**kwargs)
```

## Using Custom Mixins

```python
# Create advanced file manager
fm = AdvancedFileManager("secure_config.json", auto_create=True)

# Set up validation rules
fm.add_validation_rule("database.port", lambda x: isinstance(x, int) and 1 <= x <= 65535)
fm.add_validation_rule("app.version", lambda x: isinstance(x, str) and len(x) > 0)

# Set up encryption
fm.set_encryption_key("my-secret-key")

# Use validation
fm.set_key_with_validation(5432, dot_key="database.port")  # Valid
fm.set_key_with_validation("invalid", dot_key="database.port")  # Invalid

# Use encryption
fm.set_encrypted_key("secret-password", dot_key="database.password")
password = fm.get_encrypted_key(dot_key="database.password")
```
