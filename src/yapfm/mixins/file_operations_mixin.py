"""
Mixin for file operations.
"""

# mypy: ignore-errors

from yapfm.exceptions import FileWriteError, LoadFileError


class FileOperationsMixin:
    def __init__(self, **kwargs) -> None:
        self._loaded = False
        self._dirty = False
        super().__init__(**kwargs)

    def exists(self) -> bool:
        """Check if the file exists."""
        return self.path.exists()

    def is_dirty(self) -> bool:
        """Check if the file is dirty."""
        return self._dirty

    def is_loaded(self) -> bool:
        """Check if the file is loaded."""
        return self._loaded

    def load(self) -> None:
        """
        Load data from the file.

        This method reads the file from disk and loads its contents into memory.
        If the file doesn't exist, it creates an empty document. The method
        automatically detects the file format and uses the appropriate strategy
        for parsing.

        Raises:
            FileNotFoundError: If the file doesn't exist and auto_create is False.
            ValueError: If the file format is invalid or corrupted.
            LoadFileError: If there's an error during the loading process.

        Example:
            >>> fm = FileManager("config.toml")
            >>> fm.load()  # Loads the file content into memory
            >>>
            >>> # Check if loaded successfully
            >>> if fm.is_loaded():
            ...     print("File loaded successfully")
            ...     data = fm.get_data()
            ...     print(f"Loaded {len(data)} top-level keys")
        """
        if not self.exists():
            # Create empty document if file doesn't exist
            self.document = {}
            self.mark_as_loaded()
            return

        try:
            self.document = self.strategy.load(self.path)
            self.mark_as_loaded()
        except Exception as e:
            raise LoadFileError(f"Failed to load file {self.path}: {e}")

    def save(self) -> None:
        """
        Save data to the file.

        This method writes the current in-memory data to the file on disk.
        It uses the appropriate strategy for the file format to ensure proper
        serialization. The method will create the file if it doesn't exist
        and will overwrite existing content.

        Raises:
            PermissionError: If the file cannot be written due to permissions.
            ValueError: If the data format is invalid for the file type.
            FileWriteError: If there's an error during the writing process.

        Example:
            >>> fm = FileManager("config.toml")
            >>> fm.load()
            >>>
            >>> # Make changes
            >>> fm.set_key("database.host", "localhost")
            >>> fm.set_key("database.port", 5432)
            >>>
            >>> # Save changes
            >>> fm.save()
            >>> print("File saved successfully")
            >>>
            >>> # Check if file is dirty
            >>> if fm.is_dirty():
            ...     print("File has unsaved changes")
            ...     fm.save()
        """
        if not self.is_loaded():
            raise FileWriteError("No data to save. Load or set data first.", self.path)

        try:
            self.strategy.save(self.path, self.document)
            self.mark_as_clean()
        except Exception as e:
            raise FileWriteError(f"Failed to save file: {e}", self.path)

    def save_if_dirty(self) -> None:
        """
        Save the file only if it has been modified.
        """
        if self.is_dirty():
            self.save()

    def reload(self) -> None:
        """Reload data from the file, discarding any unsaved changes."""
        self.mark_as_clean()
        self.load()

    def mark_as_dirty(self) -> None:
        """Mark the file as dirty."""
        self._dirty = True

    def mark_as_clean(self) -> None:
        """Mark the file as clean."""
        self._dirty = False

    def mark_as_loaded(self) -> None:
        """Mark the file as loaded."""
        self._loaded = True

    def unload(self) -> None:
        """Unload the file."""
        self._loaded = False
        self._dirty = False
        self.document = {}

    def create_empty_file(self) -> None:
        """Create an empty file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        self.mark_as_loaded()
        self.save()

    def load_if_not_loaded(self) -> None:
        """Load the file if it is not loaded."""
        if not self.is_loaded():
            self.load()
