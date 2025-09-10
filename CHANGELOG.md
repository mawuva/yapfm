## v0.2.0 (2025-09-10)

### Feat

- Introduce open_file helper function for simplified file management
- Enhance YAPFileManager with key and section operations mixins
- Introduce ContextMixin for enhanced context management in YAPFileManager
- Enhance YAPFM with mixins and file operations
- Implement FileManagerProxy for enhanced file management
- Add validation utilities for file strategies
- Introduce file management strategies and error handling
- Implement file management and strategy registry system - Introduce YAPFileManager class for managing file paths and strategies - Add FileStrategyRegistry for thread-safe strategy registration and usage tracking - Define BaseFileStrategy protocol for file handling strategies - Create initial structure for various file strategies

### Fix

- Correct JSON loading function in JsonStrategy

### Refactor

- Update import paths and enhance TOML merging logic
- Replace Lock with RLock for thread safety in FileStrategyRegistry
