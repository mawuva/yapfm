# Custom Strategies

Creating custom strategies allows you to support new file formats or customize existing ones.

## Basic Custom Strategy

```python
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy
from pathlib import Path
from typing import Any, List, Optional, Union
import csv

@register_file_strategy(".csv")
class CsvStrategy:
    """Custom strategy for CSV files."""
    
    def load(self, file_path: Union[Path, str]) -> List[Dict[str, Any]]:
        """Load CSV file as list of dictionaries."""
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    
    def save(self, file_path: Union[Path, str], data: List[Dict[str, Any]]) -> None:
        """Save list of dictionaries as CSV file."""
        if not data:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def navigate(self, document: List[Dict[str, Any]], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate CSV document structure."""
        if not path:
            return document
        
        # For CSV, we can navigate by row index and column name
        if len(path) == 1:
            # Get all values for a column
            column = path[0]
            return [row.get(column) for row in document if column in row]
        elif len(path) == 2:
            # Get specific cell value
            try:
                row_index = int(path[0])
                column = path[1]
                if 0 <= row_index < len(document):
                    return document[row_index].get(column)
            except (ValueError, IndexError):
                pass
        
        return None

# Usage
fm = YAPFileManager("data.csv")  # Automatically uses CsvStrategy
```

## Advanced Custom Strategy with Validation

```python
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy([".json", ".yaml", ".yml"])
class MultiFormatStrategy:
    """Strategy that can handle multiple formats based on file extension."""
    
    def load(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Load file based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if extension == '.json':
            return json.loads(content)
        elif extension in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def save(self, file_path: Union[Path, str], data: Dict[str, Any]) -> None:
        """Save file based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.json':
            content = json.dumps(data, indent=2, ensure_ascii=False)
        elif extension in ['.yaml', '.yml']:
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    
    def navigate(self, document: Dict[str, Any], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate document structure."""
        current = document
        
        for part in path:
            if isinstance(current, dict):
                if part not in current:
                    if create:
                        current[part] = {}
                    else:
                        return None
                current = current[part]
            else:
                return None
        
        return current

# Usage
json_fm = YAPFileManager("config.json")  # Uses MultiFormatStrategy
yaml_fm = YAPFileManager("config.yaml")  # Uses MultiFormatStrategy
```

## Strategy with Caching

```python
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time
from yapfm.strategies import BaseFileStrategy
from yapfm.registry import register_file_strategy

@register_file_strategy(".json")
class CachedJsonStrategy:
    """JSON strategy with caching capabilities."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # path -> (data, timestamp)
        self._cache_ttl = 300  # 5 minutes
    
    def load(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Load JSON file with caching."""
        file_path = str(file_path)
        current_time = time.time()
        
        # Check cache
        if file_path in self._cache:
            data, timestamp = self._cache[file_path]
            if current_time - timestamp < self._cache_ttl:
                return data
        
        # Load from file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Update cache
        self._cache[file_path] = (data, current_time)
        
        return data
    
    def save(self, file_path: Union[Path, str], data: Dict[str, Any]) -> None:
        """Save JSON file and update cache."""
        file_path = str(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        # Update cache
        self._cache[file_path] = (data, time.time())
    
    def navigate(self, document: Dict[str, Any], path: List[str], create: bool = False) -> Optional[Any]:
        """Navigate document structure."""
        current = document
        
        for part in path:
            if isinstance(current, dict):
                if part not in current:
                    if create:
                        current[part] = {}
                    else:
                        return None
                current = current[part]
            else:
                return None
        
        return current
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for data, timestamp in self._cache.values():
            if current_time - timestamp < self._cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self._cache_ttl
        }
```
