"""
Tests for the open_file helper function.
"""

# mypy: ignore-errors

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from yapfm.helpers import open_file
from yapfm.manager import YAPFileManager


class TestOpenFile:
    """Test cases for the open_file helper function."""

    def test_open_file_with_string_path(self):
        """Test opening a file with string path."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with string path
            fm = open_file(tmp_path)
            assert isinstance(fm, YAPFileManager)
            assert fm.path == Path(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_path_object(self):
        """Test opening a file with Path object."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Test with Path object
            fm = open_file(tmp_path)
            assert isinstance(fm, YAPFileManager)
            assert fm.path == tmp_path
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_open_file_with_format_override(self):
        """Test opening a file with format override."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with format override
            fm = open_file(tmp_path, format="json")
            assert isinstance(fm, YAPFileManager)
            # Should have .json extension due to format override
            assert fm.path.suffix == ".json"
            assert fm.path.stem == Path(tmp_path).stem
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_format_override_dot_prefix(self):
        """Test opening a file with format override that has dot prefix."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with format override (with dot prefix)
            fm = open_file(tmp_path, format=".toml")
            assert isinstance(fm, YAPFileManager)
            # Should have .toml extension
            assert fm.path.suffix == ".toml"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_auto_create(self):
        """Test opening a file with auto_create enabled."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_existent_file = Path(tmp_dir) / "test_config.json"

            # Test with auto_create=True
            fm = open_file(non_existent_file, auto_create=True)
            assert isinstance(fm, YAPFileManager)
            assert fm.auto_create is True

    def test_open_file_without_auto_create(self):
        """Test opening a file without auto_create (default)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_existent_file = Path(tmp_dir) / "test_config.json"

            # Test with auto_create=False (default)
            fm = open_file(non_existent_file, auto_create=False)
            assert isinstance(fm, YAPFileManager)
            assert fm.auto_create is False

    def test_open_file_different_formats(self):
        """Test opening files with different format overrides."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test JSON format
            fm_json = open_file(tmp_path, format="json")
            assert fm_json.path.suffix == ".json"

            # Test TOML format
            fm_toml = open_file(tmp_path, format="toml")
            assert fm_toml.path.suffix == ".toml"

            # Test YAML format
            fm_yaml = open_file(tmp_path, format="yaml")
            assert fm_yaml.path.suffix == ".yaml"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_format_case_insensitive(self):
        """Test that format parameter is case insensitive."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test uppercase format
            fm_upper = open_file(tmp_path, format="JSON")
            assert fm_upper.path.suffix == ".json"

            # Test mixed case format
            fm_mixed = open_file(tmp_path, format="ToMl")
            assert fm_mixed.path.suffix == ".toml"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_preserves_original_path_stem(self):
        """Test that format override preserves the original file stem."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            original_stem = tmp_path.stem

        try:
            # Test that stem is preserved
            fm = open_file(tmp_path, format="json")
            assert fm.path.stem == original_stem
            assert fm.path.suffix == ".json"

        finally:
            tmp_path.unlink(missing_ok=True)

    def test_open_file_with_none_format(self):
        """Test opening a file with None format (should use file extension)."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with None format
            fm = open_file(tmp_path, format=None)
            assert isinstance(fm, YAPFileManager)
            assert fm.path == Path(tmp_path)
            assert fm.path.suffix == ".json"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_returns_yapfilemanager_instance(self):
        """Test that open_file returns a YAPFileManager instance."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            fm = open_file(tmp_path)
            assert isinstance(fm, YAPFileManager)
            assert hasattr(fm, "load")
            assert hasattr(fm, "save")
            assert hasattr(fm, "set_key")
            assert hasattr(fm, "get_key")

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_complex_path(self):
        """Test opening a file with complex path structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            complex_path = Path(tmp_dir) / "subdir" / "config" / "app.json"
            complex_path.parent.mkdir(parents=True, exist_ok=True)
            complex_path.touch()

            # Test with complex path
            fm = open_file(complex_path)
            assert isinstance(fm, YAPFileManager)
            assert fm.path == complex_path

    def test_open_file_with_relative_path(self):
        """Test opening a file with relative path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            test_file = tmp_dir_path / "test_config.json"
            test_file.touch()

            # Change to the temp directory to create a relative path
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(tmp_dir_path)

                # Test with relative path
                fm = open_file("test_config.json")
                assert isinstance(fm, YAPFileManager)
                assert fm.path.resolve() == test_file.resolve()

            finally:
                os.chdir(original_cwd)

    def test_open_file_integration_with_existing_file(self):
        """Test integration with existing file operations."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Create some test data
            test_data = {"app": {"name": "Test App", "version": "1.0.0"}}

            # Use open_file to create manager and save data
            fm = open_file(tmp_path, auto_create=True)
            with fm:
                fm.data = test_data

            # Use open_file again to load the data
            fm2 = open_file(tmp_path)
            with fm2:
                loaded_data = fm2.data
                assert loaded_data == test_data

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_error_handling(self):
        """Test error handling in open_file."""
        # Test with invalid path type
        with pytest.raises((TypeError, AttributeError)):
            open_file(123)  # Invalid path type

        # Test with None path
        with pytest.raises((TypeError, AttributeError)):
            open_file(None)

    def test_open_file_with_empty_format(self):
        """Test opening a file with empty format string."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with empty format - should keep original extension
            fm = open_file(tmp_path, format="")
            assert isinstance(fm, YAPFileManager)
            # Should keep original extension since empty format is ignored
            assert fm.path.suffix == ".json"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_whitespace_format(self):
        """Test opening a file with whitespace in format string."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with whitespace in format
            fm = open_file(tmp_path, format=" json ")
            assert isinstance(fm, YAPFileManager)
            # Should strip whitespace and add .json extension
            assert fm.path.suffix == ".json"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_open_file_with_only_whitespace_format(self):
        """Test opening a file with only whitespace in format string."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test with only whitespace in format
            fm = open_file(tmp_path, format="   ")
            assert isinstance(fm, YAPFileManager)
            # Should keep original extension since only whitespace is treated as empty
            assert fm.path.suffix == ".json"

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @patch("yapfm.manager.YAPFileManager")
    def test_open_file_calls_yapfilemanager_correctly(self, mock_yapfm):
        """Test that open_file calls YAPFileManager with correct parameters."""
        mock_instance = MagicMock()
        mock_yapfm.return_value = mock_instance

        test_path = "test.json"
        test_format = "toml"
        test_auto_create = True

        # Call open_file
        result = open_file(test_path, format=test_format, auto_create=test_auto_create)

        # Verify YAPFileManager was called with correct parameters
        mock_yapfm.assert_called_once()
        call_args = mock_yapfm.call_args

        # Check that the path was converted to Path object with correct extension
        expected_path = Path(test_path).with_suffix(".toml")
        assert call_args[0][0] == expected_path
        assert call_args[1]["strategy"] is None
        assert call_args[1]["auto_create"] is True

        # Verify the result is the mock instance
        assert result == mock_instance
