# Exceptions

## FileManagerError

Base exception for all file manager errors.

```python
from yapfm.exceptions import FileManagerError
```

## LoadFileError

Raised when there's an error loading a file.

```python
from yapfm.exceptions import LoadFileError
```

**Example:**
```python
try:
    fm.load()
except LoadFileError as e:
    print(f"Failed to load file: {e}")
```

## FileWriteError

Raised when there's an error writing to a file.

```python
from yapfm.exceptions import FileWriteError
```

**Example:**
```python
try:
    fm.save()
except FileWriteError as e:
    print(f"Failed to save file: {e}")
```

## StrategyError

Raised when there's an error with file strategies.

```python
from yapfm.exceptions import StrategyError
```

**Example:**
```python
try:
    fm = YAPFileManager("file.xyz")
except StrategyError as e:
    print(f"Strategy error: {e}")
```
