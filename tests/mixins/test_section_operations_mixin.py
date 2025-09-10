"""
Tests for SectionOperationsMixin.

This module contains unit tests for the SectionOperationsMixin class,
which provides section-level operations for the file manager.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, patch

from yapfm.mixins.section_operations_mixin import SectionOperationsMixin


class MockFileManager(SectionOperationsMixin):
    """Mock file manager for testing SectionOperationsMixin."""

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

    def resolve_and_navigate(
        self,
        dot_key: Optional[str],
        path: Optional[List[str]],
        key_name: Optional[str],
        create: bool = False,
    ) -> Optional[Tuple[Any, str]]:
        """Mock resolve_and_navigate method."""
        from yapfm.helpers import split_dot_key

        if dot_key is not None:
            path, key_name = split_dot_key(dot_key)
        elif path is not None and key_name is not None:
            pass
        else:
            raise ValueError("You must provide either dot_key or (path + key_name)")

        parent = self.strategy.navigate(self.document, path, create=create)
        if parent is None:
            return None
        return parent, key_name

    def has_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """Mock has_key method."""
        result = self.resolve_and_navigate(dot_key, path, key_name)
        return result is not None

    def delete_key(
        self,
        dot_key: Optional[str] = None,
        *,
        path: Optional[List[str]] = None,
        key_name: Optional[str] = None,
    ) -> bool:
        """Mock delete_key method."""
        result = self.resolve_and_navigate(dot_key, path, key_name)
        if result is None:
            return False

        parent, key_name = result
        if isinstance(parent, dict) and key_name in parent:
            del parent[key_name]
            self.mark_as_dirty()
            return True
        return False

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


class TestSectionOperationsMixin:
    """Test cases for SectionOperationsMixin."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_section_operations_mixin_set_section_dot_notation(self) -> None:
        """
        Scenario: Set section using dot notation

        Expected:
            - Should set section data at correct path
            - Should mark file as dirty
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {}

        # Mock strategy navigate method
        mock_parent = {}
        fm.strategy.navigate.return_value = mock_parent

        section_data = {"host": "localhost", "port": 5432, "name": "myapp"}
        fm.set_section(section_data, dot_key="database")

        # Verify strategy was called correctly (navigates to parent, then sets key)
        fm.strategy.navigate.assert_called_once_with(fm.document, [], create=True)
        # Verify parent was updated with section data
        assert mock_parent["database"] == section_data
        # Verify file is marked as dirty
        assert fm.is_dirty() is True

    def test_section_operations_mixin_set_section_explicit_path(self) -> None:
        """
        Scenario: Set section using explicit path

        Expected:
            - Should set section data at correct path
            - Should mark file as dirty
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {}

        # Mock strategy navigate method
        mock_parent = {}
        fm.strategy.navigate.return_value = mock_parent

        section_data = {"backend": "redis", "ttl": 3600, "max_connections": 100}
        fm.set_section(section_data, path=["cache"], key_name="config")

        # Verify strategy was called correctly
        fm.strategy.navigate.assert_called_once_with(
            fm.document, ["cache"], create=True
        )
        # Verify parent was updated with section data
        assert mock_parent["config"] == section_data
        # Verify file is marked as dirty
        assert fm.is_dirty() is True

    def test_section_operations_mixin_get_section_dot_notation(self) -> None:
        """
        Scenario: Get section using dot notation

        Expected:
            - Should return correct section data
            - Should load file if not loaded
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {"database": {"host": "localhost", "port": 5432}}
        fm._loaded = False

        # Mock resolve_and_navigate to return parent and key_name
        mock_parent = {"database": {"host": "localhost", "port": 5432}}
        with patch.object(fm, "resolve_and_navigate") as mock_resolve:
            mock_resolve.return_value = (mock_parent, "database")

            with patch.object(fm, "load") as mock_load:
                section = fm.get_section("database")

            assert section == {"host": "localhost", "port": 5432}
            mock_load.assert_called_once()

    def test_section_operations_mixin_get_section_with_default(self) -> None:
        """
        Scenario: Get section with default value when section doesn't exist

        Expected:
            - Should return default value
            - Should not raise exception
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {}

        # Mock strategy navigate method to return None
        fm.strategy.navigate.return_value = None

        default_section = {"key": "default_value"}
        section = fm.get_section("missing.section", default=default_section)
        assert section == default_section

    def test_section_operations_mixin_has_section_dot_notation(self) -> None:
        """
        Scenario: Check if section exists using dot notation

        Expected:
            - Should return True for existing section
            - Should return False for missing section
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {"database": {"host": "localhost"}}

        # Mock strategy navigate method
        fm.strategy.navigate.return_value = {"host": "localhost"}

        assert fm.has_section("database") is True

        # Test missing section
        fm.strategy.navigate.return_value = None
        assert fm.has_section("missing") is False

    def test_section_operations_mixin_delete_section_dot_notation(self) -> None:
        """
        Scenario: Delete section using dot notation

        Expected:
            - Should delete existing section
            - Should mark file as dirty
            - Should return True for successful deletion
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {"database": {"host": "localhost"}}

        # Mock strategy navigate method
        mock_parent = {"database": {"host": "localhost"}}
        fm.strategy.navigate.return_value = mock_parent

        result = fm.delete_section("database")

        assert result is True
        assert "database" not in mock_parent
        assert fm.is_dirty() is True

    def test_section_operations_mixin_integration_workflow(self) -> None:
        """
        Scenario: Complete workflow with section operations

        Expected:
            - Should handle complete CRUD workflow
            - Should maintain correct state throughout
        """
        fm = MockFileManager(self.temp_path / "test.toml")
        fm.document = {}

        # Mock strategy navigate method
        mock_parent = {}
        fm.strategy.navigate.return_value = mock_parent

        # Set initial sections
        database_config = {"host": "localhost", "port": 5432, "name": "myapp"}
        api_config = {"version": "v1", "timeout": 30, "retries": 3}

        fm.set_section(database_config, dot_key="database")
        fm.set_section(api_config, dot_key="api")

        # Verify sections were set
        assert mock_parent["database"] == database_config
        assert mock_parent["api"] == api_config

        # Check existence (mock resolve_and_navigate for each call)
        with patch.object(fm, "resolve_and_navigate") as mock_resolve:
            mock_resolve.return_value = (mock_parent, "database")
            assert fm.has_section("database") is True

            mock_resolve.return_value = (mock_parent, "api")
            assert fm.has_section("api") is True

            mock_resolve.return_value = None
            assert fm.has_section("missing") is False

            # Get sections
            mock_resolve.return_value = (mock_parent, "database")
            db_section = fm.get_section("database")

            mock_resolve.return_value = (mock_parent, "api")
            api_section = fm.get_section("api")

        assert db_section == database_config
        assert api_section == api_config

        # Delete sections
        with patch.object(fm, "resolve_and_navigate") as mock_resolve:
            mock_resolve.return_value = (mock_parent, "api")
            fm.delete_section("api")

            mock_resolve.return_value = None
            assert fm.has_section("api") is False

            mock_resolve.return_value = (mock_parent, "database")
            assert fm.has_section("database") is True

        # Verify file is dirty
        assert fm.is_dirty() is True
