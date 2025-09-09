"""
Unit tests for io module.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from yapfm.helpers.io import (
    load_file,
    load_file_with_stream,
    save_file,
    save_file_with_stream,
)


class TestLoadFile:
    """Test cases for load_file function."""

    def test_load_file_with_json_parser(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using JSON parser

        Expected:
        - Should read file content and parse it as JSON
        - Should return the parsed data structure
        - Should handle file reading correctly
        """
        test_data = {"key": "value", "number": 42}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_file(file_path, json.loads)
        assert result == test_data

    def test_load_file_with_custom_parser(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using a custom parser function

        Expected:
        - Should read file content and apply custom parser
        - Should return the result of the parser function
        - Should handle custom parsing logic correctly
        """
        file_content = "line1\nline2\nline3"
        file_path = tmp_path / "test.txt"
        file_path.write_text(file_content, encoding="utf-8")

        def line_parser(content: str) -> list[str]:
            return content.splitlines()

        result = load_file(file_path, line_parser)
        assert result == ["line1", "line2", "line3"]

    def test_load_file_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using string path instead of Path object

        Expected:
        - Should convert string to Path object internally
        - Should read and parse file content correctly
        - Should handle string path conversion properly
        """
        test_data = {"test": "data"}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_file(str(file_path), json.loads)
        assert result == test_data

    def test_load_file_with_parser_that_returns_none(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file with a parser that returns None

        Expected:
        - Should return None from the parser function
        - Should handle None return values correctly
        - Should not raise any exceptions
        """
        file_path = tmp_path / "test.txt"
        file_path.write_text("some content", encoding="utf-8")

        def none_parser(content: str) -> None:
            return None

        result = load_file(file_path, none_parser)
        assert result is None

    def test_load_file_with_parser_that_raises_exception(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file with a parser that raises an exception

        Expected:
        - Should transform parser exception into FileReadError
        - Should preserve the original error message
        - Should allow error handling decorator to handle it
        """
        from yapfm.exceptions.file_operations import FileReadError

        file_path = tmp_path / "test.txt"
        file_path.write_text("invalid json", encoding="utf-8")

        with pytest.raises(FileReadError) as exc_info:
            load_file(file_path, json.loads)

        assert "Expecting value" in str(exc_info.value)

    def test_load_file_nonexistent_file(self) -> None:
        """
        Scenario: Load a file that doesn't exist

        Expected:
        - Should transform FileNotFoundError into FileReadError
        - Should not create the file
        - Should handle missing file gracefully
        """
        from yapfm.exceptions.file_operations import FileReadError

        nonexistent_path = Path("nonexistent_file.txt")

        with pytest.raises(FileReadError) as exc_info:
            load_file(nonexistent_path, json.loads)

        assert "File not found" in str(exc_info.value)

    def test_load_file_with_encoding_handling(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file with special characters requiring UTF-8 encoding

        Expected:
        - Should read file with correct UTF-8 encoding
        - Should handle special characters properly
        - Should preserve all characters in the content
        """
        special_content = "café naïve résumé"
        file_path = tmp_path / "special.txt"
        file_path.write_text(special_content, encoding="utf-8")

        def identity_parser(content: str) -> str:
            return content

        result = load_file(file_path, identity_parser)
        assert result == special_content


class TestLoadFileWithStream:
    """Test cases for load_file_with_stream function."""

    def test_load_file_with_stream_json_parser(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using stream-based JSON parser

        Expected:
        - Should pass file stream to parser function
        - Should return parsed data from stream parser
        - Should handle file stream correctly
        """
        test_data = {"key": "value", "nested": {"data": 123}}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        def stream_parser(file_stream: Any) -> dict[str, Any]:
            return json.load(file_stream)

        result = load_file_with_stream(file_path, stream_parser)
        assert result == test_data

    def test_load_file_with_stream_custom_parser(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using custom stream-based parser

        Expected:
        - Should pass file stream to custom parser
        - Should return result from custom parser
        - Should handle custom stream processing correctly
        """
        file_content = "line1\nline2\nline3"
        file_path = tmp_path / "test.txt"
        file_path.write_text(file_content, encoding="utf-8")

        def line_count_parser(file_stream: Any) -> int:
            return sum(1 for _ in file_stream)

        result = load_file_with_stream(file_path, line_count_parser)
        assert result == 3

    def test_load_file_with_stream_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Load a file using string path with stream parser

        Expected:
        - Should convert string to Path object
        - Should open file stream correctly
        - Should pass stream to parser function
        """
        test_data = {"test": "stream_data"}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(test_data), encoding="utf-8")

        def stream_parser(file_stream: Any) -> dict[str, Any]:
            return json.load(file_stream)

        result = load_file_with_stream(str(file_path), stream_parser)
        assert result == test_data

    def test_load_file_with_stream_nonexistent_file(self) -> None:
        """
        Scenario: Load a nonexistent file with stream parser

        Expected:
        - Should transform FileNotFoundError into FileReadError
        - Should not create the file
        - Should handle missing file gracefully
        """
        from yapfm.exceptions.file_operations import FileReadError

        nonexistent_path = Path("nonexistent_stream_file.txt")

        def dummy_parser(file_stream: Any) -> Any:
            return file_stream.read()

        with pytest.raises(FileReadError) as exc_info:
            load_file_with_stream(nonexistent_path, dummy_parser)

        assert "File not found" in str(exc_info.value)


class TestSaveFile:
    """Test cases for save_file function."""

    def test_save_file_with_json_serializer(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using JSON serializer

        Expected:
        - Should serialize data to JSON string
        - Should write content to file with correct encoding
        - Should create parent directories if needed
        """
        test_data = {"key": "value", "number": 42}
        file_path = tmp_path / "subdir" / "test.json"

        save_file(file_path, test_data, json.dumps)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_with_custom_serializer(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using custom serializer

        Expected:
        - Should apply custom serializer to data
        - Should write serialized content to file
        - Should handle custom serialization logic correctly
        """
        test_data = ["line1", "line2", "line3"]
        file_path = tmp_path / "test.txt"

        def line_serializer(data: list[str]) -> str:
            return "\n".join(data)

        save_file(file_path, test_data, line_serializer)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert content == "line1\nline2\nline3"

    def test_save_file_with_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using string path

        Expected:
        - Should convert string to Path object
        - Should create file and write content correctly
        - Should handle string path conversion properly
        """
        test_data = {"test": "string_path"}
        file_path = tmp_path / "test.json"

        save_file(str(file_path), test_data, json.dumps)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_creates_parent_directories(self, tmp_path: Path) -> None:
        """
        Scenario: Save file to path with non-existent parent directories

        Expected:
        - Should create all parent directories automatically
        - Should save file in the correct location
        - Should handle directory creation gracefully
        """
        test_data = {"nested": "data"}
        file_path = tmp_path / "level1" / "level2" / "level3" / "test.json"

        save_file(file_path, test_data, json.dumps)

        assert file_path.exists()
        assert file_path.parent.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_with_serializer_that_raises_exception(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save file with serializer that raises an exception

        Expected:
        - Should transform serializer exception into FileWriteError
        - Should create the file but leave it empty if serialization fails
        - Should allow error handling decorator to handle it
        """
        from yapfm.exceptions.file_operations import FileWriteError

        test_data = {"invalid": "data"}
        file_path = tmp_path / "test.json"

        def failing_serializer(data: Any) -> str:
            raise ValueError("Serialization failed")

        with pytest.raises(FileWriteError) as exc_info:
            save_file(file_path, test_data, failing_serializer)

        assert "Serialization failed" in str(exc_info.value)
        assert file_path.exists()  # File is created before serialization
        assert file_path.read_text() == ""  # But remains empty due to exception

    def test_save_file_overwrites_existing_file(self, tmp_path: Path) -> None:
        """
        Scenario: Save file to path that already exists

        Expected:
        - Should overwrite existing file content
        - Should replace old content with new content
        - Should not append to existing file
        """
        file_path = tmp_path / "test.json"
        file_path.write_text('{"old": "data"}', encoding="utf-8")

        new_data = {"new": "data"}
        save_file(file_path, new_data, json.dumps)

        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == new_data

    def test_save_file_with_utf8_encoding(self, tmp_path: Path) -> None:
        """
        Scenario: Save file with UTF-8 encoded content

        Expected:
        - Should save content with UTF-8 encoding
        - Should handle special characters correctly
        - Should preserve all characters in the content
        """
        special_data = {"message": "café naïve résumé"}
        file_path = tmp_path / "special.json"

        save_file(file_path, special_data, json.dumps)

        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == special_data


class TestSaveFileWithStream:
    """Test cases for save_file_with_stream function."""

    def test_save_file_with_stream_json_writer(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using stream-based JSON writer

        Expected:
        - Should pass data and file stream to writer function
        - Should write content to file correctly
        - Should handle file stream operations properly
        """
        test_data = {"key": "value", "nested": {"data": 123}}
        file_path = tmp_path / "test.json"

        def stream_writer(data: Any, file_stream: Any) -> None:
            json.dump(data, file_stream, indent=2)

        save_file_with_stream(file_path, test_data, stream_writer)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_with_stream_custom_writer(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using custom stream-based writer

        Expected:
        - Should pass data and file stream to custom writer
        - Should write content using custom writer logic
        - Should handle custom stream writing correctly
        """
        test_data = ["line1", "line2", "line3"]
        file_path = tmp_path / "test.txt"

        def line_writer(data: list[str], file_stream: Any) -> None:
            for line in data:
                file_stream.write(f"{line}\n")

        save_file_with_stream(file_path, test_data, line_writer)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert content == "line1\nline2\nline3\n"

    def test_save_file_with_stream_string_path(self, tmp_path: Path) -> None:
        """
        Scenario: Save data to file using string path with stream writer

        Expected:
        - Should convert string to Path object
        - Should create file and write content correctly
        - Should handle string path conversion properly
        """
        test_data = {"test": "stream_writer"}
        file_path = tmp_path / "test.json"

        def stream_writer(data: Any, file_stream: Any) -> None:
            json.dump(data, file_stream)

        save_file_with_stream(str(file_path), test_data, stream_writer)

        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_with_stream_creates_parent_directories(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save file to path with non-existent parent directories using stream writer

        Expected:
        - Should create all parent directories automatically
        - Should save file in the correct location
        - Should handle directory creation gracefully
        """
        test_data = {"nested": "stream_data"}
        file_path = tmp_path / "level1" / "level2" / "level3" / "test.json"

        def stream_writer(data: Any, file_stream: Any) -> None:
            json.dump(data, file_stream)

        save_file_with_stream(file_path, test_data, stream_writer)

        assert file_path.exists()
        assert file_path.parent.exists()
        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == test_data

    def test_save_file_with_stream_writer_that_raises_exception(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save file with stream writer that raises an exception

        Expected:
        - Should transform writer exception into FileWriteError
        - Should create the file but leave it empty if writing fails
        - Should allow error handling decorator to handle it
        """
        from yapfm.exceptions.file_operations import FileWriteError

        test_data = {"invalid": "data"}
        file_path = tmp_path / "test.json"

        def failing_writer(data: Any, file_stream: Any) -> None:
            raise ValueError("Writing failed")

        with pytest.raises(FileWriteError) as exc_info:
            save_file_with_stream(file_path, test_data, failing_writer)

        assert "Writing failed" in str(exc_info.value)
        assert file_path.exists()  # File is created before writing
        assert file_path.read_text() == ""  # But remains empty due to exception

    def test_save_file_with_stream_overwrites_existing_file(
        self, tmp_path: Path
    ) -> None:
        """
        Scenario: Save file to path that already exists using stream writer

        Expected:
        - Should overwrite existing file content
        - Should replace old content with new content
        - Should not append to existing file
        """
        file_path = tmp_path / "test.json"
        file_path.write_text('{"old": "data"}', encoding="utf-8")

        new_data = {"new": "stream_data"}

        def stream_writer(data: Any, file_stream: Any) -> None:
            json.dump(data, file_stream)

        save_file_with_stream(file_path, new_data, stream_writer)

        content = file_path.read_text(encoding="utf-8")
        assert json.loads(content) == new_data
