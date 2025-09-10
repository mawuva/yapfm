"""
Tests for KeyOperationsMixin.

This module contains unit tests for the KeyOperationsMixin class,
which provides key-level operations for the file manager.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from yapfm.mixins.key_operations_mixin import KeyOperationsMixin


class MockFileManager(KeyOperationsMixin):
    """Mock file manager for testing KeyOperationsMixin."""

    def __init__(
        self,
        path: Path,
        auto_create: bool = False,
        document: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.path = path
        self.auto_create = auto_create
        self.document = document or {}
        self._loaded = True
        self._dirty = False
        self.strategy = MagicMock()
        super().__init__()

    def exists(self) -> bool:
        """Check if file exists."""
        return self.path.exists()

    def is_loaded(self) -> bool:
        """Check if file is loaded."""
        return self._loaded

    def load(self) -> None:
        """Load file."""
        self._loaded = True

    def save(self) -> None:
        """Save file."""
        self._dirty = False

    def mark_as_dirty(self) -> None:
        """Mark file as dirty."""
        self._dirty = True

    def mark_as_clean(self) -> None:
        """Mark file as clean."""
        self._dirty = False

    def is_dirty(self) -> bool:
        """Check if file is dirty."""
        return self._dirty


class TestKeyOperationsMixin:
    """Test cases for KeyOperationsMixin."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_key_operations_mixin_resolve_dot_key(self) -> None:
        """
        Scenario: Resolve dot key to path and key name

        Expected:
            - Should return correct path and key name
            - Should handle nested keys correctly
        """
        fm = MockFileManager(self.temp_path / "test.json")

        # Test simple key
        path, key_name = fm.resolve("simple_key", None, None)
        assert path == []
        assert key_name == "simple_key"

        # Test nested key
        path, key_name = fm.resolve("database.host", None, None)
        assert path == ["database"]
        assert key_name == "host"

        # Test deeply nested key
        path, key_name = fm.resolve("services.database.connection.host", None, None)
        assert path == ["services", "database", "connection"]
        assert key_name == "host"

    def test_key_operations_mixin_resolve_explicit_path(self) -> None:
        """
        Scenario: Resolve explicit path and key name

        Expected:
            - Should return the provided path and key name
            - Should handle empty path correctly
        """
        fm = MockFileManager(self.temp_path / "test.json")

        # Test with explicit path
        path, key_name = fm.resolve(None, ["database"], "host")
        assert path == ["database"]
        assert key_name == "host"

        # Test with empty path
        path, key_name = fm.resolve(None, [], "root_key")
        assert path == []
        assert key_name == "root_key"

    def test_key_operations_mixin_resolve_invalid_input(self) -> None:
        """
        Scenario: Resolve with invalid input

        Expected:
            - Should raise ValueError when neither dot_key nor path+key_name provided
        """
        fm = MockFileManager(self.temp_path / "test.json")

        with pytest.raises(
            ValueError,
            match="You must provide either dot_key or \\(path \\+ key_name\\)",
        ):
            fm.resolve(None, None, None)

    def test_key_operations_mixin_set_key_dot_notation(self) -> None:
        """
        Scenario: Set key using dot notation

        Expected:
            - Should set value at correct path
            - Should mark file as dirty
        """
        fm = MockFileManager(self.temp_path / "test.json")
        fm.document = {}

        # Mock strategy navigate method
        mock_parent = {}
        fm.strategy.navigate.return_value = mock_parent

        fm.set_key("localhost", dot_key="database.host")

        # Verify strategy was called correctly
        fm.strategy.navigate.assert_called_once_with(
            fm.document, ["database"], create=True
        )
        # Verify parent was updated
        assert mock_parent["host"] == "localhost"
        # Verify file is marked as dirty
        assert fm.is_dirty() is True

    def test_key_operations_mixin_get_key_dot_notation(self) -> None:
        """
        Scenario: Get key using dot notation

        Expected:
            - Should return correct value
            - Should load file if not loaded
        """
        fm = MockFileManager(self.temp_path / "test.json")
        fm.document = {"database": {"host": "localhost"}}
        fm._loaded = False

        # Mock strategy navigate method
        fm.strategy.navigate.return_value = {"host": "localhost"}

        with patch.object(fm, "load") as mock_load:
            value = fm.get_key("database.host")

        assert value == "localhost"
        mock_load.assert_called_once()

    def test_key_operations_mixin_has_key_dot_notation(self) -> None:
        """
        Scenario: Check if key exists using dot notation

        Expected:
            - Should return True for existing key
            - Should return False for missing key
        """
        fm = MockFileManager(self.temp_path / "test.json")
        fm.document = {"database": {"host": "localhost"}}

        # Mock strategy navigate method
        fm.strategy.navigate.return_value = {"host": "localhost"}

        assert fm.has_key("database.host") is True

        # Test missing key
        fm.strategy.navigate.return_value = None
        assert fm.has_key("database.missing") is False

    def test_key_operations_mixin_delete_key_dot_notation(self) -> None:
        """
        Scenario: Delete key using dot notation

        Expected:
            - Should delete existing key
            - Should mark file as dirty
            - Should return True for successful deletion
        """
        fm = MockFileManager(self.temp_path / "test.json")
        fm.document = {"database": {"host": "localhost"}}

        # Mock strategy navigate method
        mock_parent = {"host": "localhost"}
        fm.strategy.navigate.return_value = mock_parent

        result = fm.delete_key("database.host")

        assert result is True
        assert "host" not in mock_parent
        assert fm.is_dirty() is True

    def test_key_operations_mixin_integration_workflow(self) -> None:
        """
        Scenario: Complete workflow with key operations

        Expected:
            - Should handle complete CRUD workflow
            - Should maintain correct state throughout
        """
        fm = MockFileManager(self.temp_path / "test.json")
        fm.document = {}

        # Mock strategy navigate method
        mock_parent = {}
        fm.strategy.navigate.return_value = mock_parent

        # Set initial values
        fm.set_key("localhost", dot_key="database.host")
        fm.set_key("5432", dot_key="database.port")
        fm.set_key("v1", dot_key="api.version")

        # Verify values were set
        assert mock_parent["host"] == "localhost"
        assert mock_parent["port"] == "5432"
        assert mock_parent["version"] == "v1"

        # Check existence
        assert fm.has_key("database.host") is True
        assert fm.has_key("database.port") is True
        assert fm.has_key("api.version") is True
        assert fm.has_key("missing.key") is False

        # Get values
        host = fm.get_key("database.host")
        port = fm.get_key("database.port")
        version = fm.get_key("api.version")

        assert host == "localhost"
        assert port == "5432"
        assert version == "v1"

        # Delete values
        fm.delete_key("database.port")
        fm.delete_key("api.version")

        assert "port" not in mock_parent
        assert "version" not in mock_parent
        assert fm.has_key("database.port") is False
        assert fm.has_key("api.version") is False

        # Verify file is dirty
        assert fm.is_dirty() is True
