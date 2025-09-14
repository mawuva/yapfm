# Plugin Architecture

## Plugin System

```python
from yapfm import YAPFileManager
from typing import Any, Dict, List, Optional, Protocol
import importlib
import os

class Plugin(Protocol):
    """Plugin protocol for extending file manager functionality."""
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        """Initialize the plugin with the file manager."""
        ...
    
    def before_load(self, file_manager: YAPFileManager) -> None:
        """Called before loading the file."""
        ...
    
    def after_load(self, file_manager: YAPFileManager) -> None:
        """Called after loading the file."""
        ...
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        """Called before saving the file."""
        ...
    
    def after_save(self, file_manager: YAPFileManager) -> None:
        """Called after saving the file."""
        ...

class PluginManager:
    """Manager for file manager plugins."""
    
    def __init__(self, file_manager: YAPFileManager):
        self.file_manager = file_manager
        self.plugins: List[Plugin] = []
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        plugin.initialize(self.file_manager)
        self.plugins.append(plugin)
    
    def load_plugins_from_directory(self, directory: str) -> None:
        """Load plugins from a directory."""
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                module = importlib.import_module(f"{directory}.{module_name}")
                
                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, 'initialize') and
                        hasattr(attr, 'before_load')):
                        plugin = attr()
                        self.register_plugin(plugin)
    
    def before_load(self) -> None:
        """Call before_load on all plugins."""
        for plugin in self.plugins:
            plugin.before_load(self.file_manager)
    
    def after_load(self) -> None:
        """Call after_load on all plugins."""
        for plugin in self.plugins:
            plugin.after_load(self.file_manager)
    
    def before_save(self) -> None:
        """Call before_save on all plugins."""
        for plugin in self.plugins:
            plugin.before_save(self.file_manager)
    
    def after_save(self) -> None:
        """Call after_save on all plugins."""
        for plugin in self.plugins:
            plugin.after_save(self.file_manager)

class LoggingPlugin:
    """Plugin for logging file operations."""
    
    def __init__(self):
        self.logger = None
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        import logging
        self.logger = logging.getLogger("file_manager_plugin")
    
    def before_load(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"Loading file: {file_manager.path}")
    
    def after_load(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"File loaded: {file_manager.path}")
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"Saving file: {file_manager.path}")
    
    def after_save(self, file_manager: YAPFileManager) -> None:
        self.logger.info(f"File saved: {file_manager.path}")

class ValidationPlugin:
    """Plugin for validating configuration."""
    
    def __init__(self):
        self.validation_rules = {}
    
    def initialize(self, file_manager: YAPFileManager) -> None:
        pass
    
    def before_save(self, file_manager: YAPFileManager) -> None:
        # Validate configuration before saving
        if not self._validate_config(file_manager.data):
            raise ValueError("Configuration validation failed")
    
    def _validate_config(self, data: Dict[str, Any]) -> bool:
        # Add your validation logic here
        return True

# Usage
fm = YAPFileManager("plugin_config.json", auto_create=True)
plugin_manager = PluginManager(fm)

# Register plugins
plugin_manager.register_plugin(LoggingPlugin())
plugin_manager.register_plugin(ValidationPlugin())

# Use file manager with plugins
with fm:
    plugin_manager.before_load()
    fm.load()
    plugin_manager.after_load()
    
    fm.set_key("value", dot_key="key")
    
    plugin_manager.before_save()
    fm.save()
    plugin_manager.after_save()
```
