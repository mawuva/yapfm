# SecurityMixin

Provides security functionality for the file manager. The SecurityMixin contains operations for freezing, unfreezing, and masking sensitive data.

## Methods

### freeze

```python
def freeze(self) -> None
```

Make the file read-only by preventing modifications.

**Example:**
```python
fm.freeze()
fm.set("new.key", "value")  # Raises PermissionError
```

### unfreeze

```python
def unfreeze(self) -> None
```

Re-enable write operations on the file.

**Example:**
```python
fm.unfreeze()
fm.set("new.key", "value")  # Now works
```

### is_frozen

```python
def is_frozen(self) -> bool
```

Check if the file is frozen (read-only).

**Returns:**
- `bool`: True if frozen, False otherwise

**Example:**
```python
if fm.is_frozen():
    print("File is read-only")
```

### mask_sensitive

```python
def mask_sensitive(
    self, 
    keys_to_mask: Optional[List[str]] = None, 
    mask: str = "***"
) -> Dict[str, Any]
```

Create a masked version of the data with sensitive information hidden.

**Parameters:**
- `keys_to_mask` (Optional[List[str]]): List of keys to mask. If None, uses default sensitive keys
- `mask` (str): String to use for masking

**Returns:**
- `Dict[str, Any]`: Dictionary with sensitive data masked

**Example:**
```python
# Mask with default sensitive keys
masked = fm.mask_sensitive()

# Mask with specific keys
masked = fm.mask_sensitive(["password", "secret"], "HIDDEN")
```

### get_public_config

```python
def get_public_config(
    self, 
    sensitive_keys: Optional[List[str]] = None
) -> Dict[str, Any]
```

Get a public version of the configuration with sensitive data removed.

**Parameters:**
- `sensitive_keys` (Optional[List[str]]): List of keys to remove. If None, uses default sensitive keys

**Returns:**
- `Dict[str, Any]`: Dictionary with sensitive data removed

**Example:**
```python
# Public config with default sensitive data removal
public = fm.get_public_config()

# Public config with specific keys
public = fm.get_public_config(["password", "secret"])
```

## Default Sensitive Keys

The SecurityMixin automatically recognizes the following key patterns as sensitive:
- password, passwd, pwd
- secret, key, token, auth, credential
- private, sensitive, confidential
- api_key, access_token, refresh_token
- session_id, cookie
