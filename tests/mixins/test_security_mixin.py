"""
Tests for SecurityMixin.

This module contains unit tests for the SecurityMixin class,
which provides security functionality like freezing and masking.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path

import pytest

from yapfm.manager import YAPFileManager
from yapfm.strategies.json_strategy import JsonStrategy


class TestSecurityMixin:
    """Test class for SecurityMixin functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.test_file = self.temp_path / "test_config.json"

        # Create test data
        self.test_data = {
            "database": {"host": "localhost", "port": 5432, "password": "secret123"},
            "api": {"key": "api_key_12345", "secret": "very_secret"},
            "user": {"email": "user@example.com", "password": "userpass"},
            "debug": True,
        }

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_freeze_basic(self) -> None:
        """
        Scenario: Freeze the file manager to prevent modifications

        Expected:
        - Should set frozen state to True
        - Should prevent write operations
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Should not be frozen initially
        assert not fm.is_frozen()

        # Freeze the manager
        fm.freeze()

        # Should be frozen now
        assert fm.is_frozen()

    def test_unfreeze_basic(self) -> None:
        """
        Scenario: Unfreeze the file manager to allow modifications

        Expected:
        - Should set frozen state to False
        - Should allow write operations again
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Freeze first
        fm.freeze()
        assert fm.is_frozen()

        # Unfreeze
        fm.unfreeze()
        assert not fm.is_frozen()

    def test_frozen_prevents_modifications(self) -> None:
        """
        Scenario: Frozen state prevents data modifications

        Expected:
        - Should raise PermissionError for write operations when frozen
        - Should allow read operations when frozen
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Freeze the manager
        fm.freeze()

        # Should raise PermissionError for modifications
        with pytest.raises(PermissionError, match="File is frozen"):
            fm.set("new.key", "value")

        # Note: Direct data assignment might not be protected
        # Test other modification methods
        with pytest.raises(PermissionError, match="File is frozen"):
            fm.delete("database.host")

    def test_frozen_allows_read_operations(self) -> None:
        """
        Scenario: Frozen state allows read operations

        Expected:
        - Should allow all read operations when frozen
        - Should not raise errors for read operations
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Freeze the manager
        fm.freeze()

        # Should allow read operations
        assert fm.get("database.host") == "localhost"
        assert fm.data == self.test_data
        assert fm.is_frozen()

    def test_mask_sensitive_basic(self) -> None:
        """
        Scenario: Mask sensitive data using default patterns

        Expected:
        - Should return masked data with sensitive fields hidden
        - Should preserve non-sensitive data
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Mask sensitive data
        masked_data = fm.mask_sensitive()

        # Should mask sensitive fields
        assert masked_data["database"]["password"] == "***"
        assert masked_data["api"]["key"] == "***"
        assert masked_data["api"]["secret"] == "***"
        assert masked_data["user"]["password"] == "***"

        # Should preserve non-sensitive data
        assert masked_data["database"]["host"] == "localhost"
        assert masked_data["database"]["port"] == 5432
        assert masked_data["user"]["email"] == "user@example.com"
        assert masked_data["debug"] is True

    def test_mask_sensitive_with_custom_patterns(self) -> None:
        """
        Scenario: Mask sensitive data using custom patterns

        Expected:
        - Should mask fields matching custom patterns
        - Should not mask fields not in custom patterns
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Custom sensitive patterns
        sensitive_patterns = ["host", "email"]

        masked_data = fm.mask_sensitive(keys_to_mask=sensitive_patterns)

        # Should mask custom patterns
        assert masked_data["database"]["host"] == "***"
        assert masked_data["user"]["email"] == "***"

        # Should preserve other data
        assert masked_data["database"]["password"] == "secret123"
        assert masked_data["api"]["key"] == "api_key_12345"

    def test_mask_sensitive_with_custom_mask(self) -> None:
        """
        Scenario: Mask sensitive data with custom mask string

        Expected:
        - Should use custom mask string for sensitive fields
        - Should preserve non-sensitive data
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        # Custom mask
        masked_data = fm.mask_sensitive(mask="[MASKED]")

        # Should use custom mask
        assert masked_data["database"]["password"] == "[MASKED]"
        assert masked_data["api"]["key"] == "[MASKED]"

    def test_mask_sensitive_preserves_structure(self) -> None:
        """
        Scenario: Mask sensitive data preserves data structure

        Expected:
        - Should preserve overall data structure
        - Should only change sensitive field values
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = self.test_data.copy()

        masked_data = fm.mask_sensitive()

        # Should preserve structure
        assert "database" in masked_data
        assert "api" in masked_data
        assert "user" in masked_data
        assert "debug" in masked_data

        # Should preserve nested structure
        assert "host" in masked_data["database"]
        assert "port" in masked_data["database"]
        assert "password" in masked_data["database"]

    def test_mask_sensitive_with_empty_data(self) -> None:
        """
        Scenario: Mask sensitive data with empty data

        Expected:
        - Should handle empty data gracefully
        - Should not raise errors
        """
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = {}

        masked_data = fm.mask_sensitive()
        assert masked_data == {}

    def test_mask_sensitive_with_nested_structures(self) -> None:
        """
        Scenario: Mask sensitive data in deeply nested structures

        Expected:
        - Should mask sensitive data at all levels
        - Should preserve nested structure
        """
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "password": "secret",
                        "api_key": "key123",
                        "normal": "value",
                    }
                }
            }
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = nested_data
        masked_data = fm.mask_sensitive()

        # Should mask sensitive data at all levels
        assert masked_data["level1"]["level2"]["level3"]["password"] == "***"
        assert masked_data["level1"]["level2"]["level3"]["api_key"] == "***"
        assert masked_data["level1"]["level2"]["level3"]["normal"] == "value"

    def test_mask_sensitive_with_lists(self) -> None:
        """
        Scenario: Mask sensitive data in lists

        Expected:
        - Should mask sensitive data in list elements
        - Should preserve list structure
        """
        list_data = {
            "users": [
                {"name": "John", "password": "pass1"},
                {"name": "Jane", "password": "pass2"},
            ],
            "api_keys": ["key1", "key2", "key3"],
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = list_data
        masked_data = fm.mask_sensitive()

        # Should mask sensitive data in lists
        assert masked_data["users"][0]["password"] == "***"
        assert masked_data["users"][1]["password"] == "***"
        assert masked_data["users"][0]["name"] == "John"
        assert masked_data["users"][1]["name"] == "Jane"
        assert masked_data["api_keys"] == "***"  # Lists are treated as single values

    def test_mask_sensitive_with_special_characters(self) -> None:
        """
        Scenario: Mask sensitive data with special characters

        Expected:
        - Should handle special characters correctly
        - Should mask sensitive data regardless of special characters
        """
        special_data = {
            "password": "p@ssw0rd!",
            "api_key": "key-123_456",
            "secret": "s3cr3t#",
            "normal": "value",
        }

        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = special_data
        masked_data = fm.mask_sensitive()

        # Should mask sensitive data with special characters
        assert masked_data["password"] == "***"
        assert masked_data["api_key"] == "***"
        assert masked_data["secret"] == "***"
        assert masked_data["normal"] == "value"

    def test_security_preserves_data_integrity(self) -> None:
        """
        Scenario: Security operations preserve data integrity

        Expected:
        - Should preserve non-sensitive data exactly
        - Should only change sensitive field values
        """
        original_data = self.test_data.copy()
        fm = YAPFileManager(self.test_file, strategy=JsonStrategy(), auto_create=True)
        fm.data = original_data

        # Perform security operations
        masked_data = fm.mask_sensitive()

        # Should preserve non-sensitive data exactly
        assert masked_data["database"]["host"] == original_data["database"]["host"]
        assert masked_data["database"]["port"] == original_data["database"]["port"]
        assert masked_data["user"]["email"] == original_data["user"]["email"]
        assert masked_data["debug"] == original_data["debug"]

        # Should only change sensitive data
        assert masked_data["database"]["password"] == "***"
        assert masked_data["api"]["key"] == "***"
        assert masked_data["api"]["secret"] == "***"
        assert masked_data["user"]["password"] == "***"
