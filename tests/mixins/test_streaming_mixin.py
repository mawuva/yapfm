"""
Tests for StreamingMixin.

This module tests the StreamingMixin functionality including streaming,
section extraction, search, and processing of large files.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from yapfm.mixins.streaming_mixin import StreamingMixin


class MockFileManager(StreamingMixin):
    """Mock file manager for testing StreamingMixin."""
    
    def __init__(self, enable_streaming=True, path=None):
        self.enable_streaming = enable_streaming
        self.path = Path(path) if path else None
        self._streaming_reader = None
    
    def exists(self):
        """Mock exists method."""
        return self.path is not None and self.path.exists()


class TestStreamingMixin:
    """Test cases for StreamingMixin class."""

    def create_test_file(self, content: str, encoding: str = "utf-8") -> Path:
        """Create a temporary test file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_streaming_mixin_initialization(self):
        """Test StreamingMixin initialization."""
        manager = MockFileManager(enable_streaming=True)
        
        assert manager.enable_streaming is True
        assert manager._streaming_reader is None

    def test_get_streaming_reader_without_streaming_enabled(self):
        """Test _get_streaming_reader without streaming enabled."""
        manager = MockFileManager(enable_streaming=False)
        
        with pytest.raises(RuntimeError, match="Streaming not enabled"):
            manager._get_streaming_reader()

    def test_get_streaming_reader_file_not_found(self):
        """Test _get_streaming_reader with nonexistent file."""
        manager = MockFileManager(enable_streaming=True, path="nonexistent.txt")
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            manager._get_streaming_reader()

    def test_get_streaming_reader_success(self):
        """Test _get_streaming_reader with valid file."""
        content = "Test content for streaming"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            reader = manager._get_streaming_reader()
            
            assert reader is not None
            assert reader.file_path == file_path
            assert reader.chunk_size == 1024 * 1024  # Default chunk size
            assert reader.buffer_size == 8192  # Default buffer size
            assert reader.encoding == "utf-8"  # Default encoding
            
        finally:
            file_path.unlink()

    def test_get_streaming_reader_with_custom_params(self):
        """Test _get_streaming_reader with custom parameters."""
        content = "Test content for streaming"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            reader = manager._get_streaming_reader(
                chunk_size=512,
                buffer_size=1024,
                encoding="latin-1"
            )
            
            assert reader.chunk_size == 512
            assert reader.buffer_size == 1024
            assert reader.encoding == "latin-1"
            
        finally:
            file_path.unlink()

    def test_create_streaming_reader(self):
        """Test create_streaming_reader method."""
        content = "Test content for streaming"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            reader = manager.create_streaming_reader()
            
            assert reader is not None
            assert reader.file_path == file_path
            
        finally:
            file_path.unlink()

    def test_stream_file(self):
        """Test stream_file method."""
        content = "Line 1\nLine 2\nLine 3\n"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            chunks = list(manager.stream_file(chunk_size=10))
            
            # Should have multiple chunks
            assert len(chunks) > 0
            # Reconstruct content
            reconstructed = "".join(chunks)
            assert reconstructed == content
            
        finally:
            file_path.unlink()

    def test_stream_sections(self):
        """Test stream_sections method."""
        content = """[database]
host = localhost
port = 5432

[app]
name = testapp
version = 1.0.0
"""
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            sections = list(manager.stream_sections("[", "]"))
            
            # Should have 2 sections
            assert len(sections) == 2
            
            # Check first section
            assert sections[0]["name"] == "[database]"
            assert "host = localhost" in sections[0]["content"]
            assert "port = 5432" in sections[0]["content"]
            
            # Check second section
            assert sections[1]["name"] == "[app]"
            assert "name = testapp" in sections[1]["content"]
            assert "version = 1.0.0" in sections[1]["content"]
            
        finally:
            file_path.unlink()

    def test_stream_sections_with_end_marker(self):
        """Test stream_sections with end marker."""
        content = """START
Line 1
Line 2
END
START
Line 3
Line 4
END
"""
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            sections = list(manager.stream_sections("START", "END"))
            
            # Should have 2 sections
            assert len(sections) == 2
            
            # Check sections
            assert sections[0]["name"] == "START"
            assert "Line 1" in sections[0]["content"]
            assert "Line 2" in sections[0]["content"]
            
            assert sections[1]["name"] == "START"
            assert "Line 3" in sections[1]["content"]
            assert "Line 4" in sections[1]["content"]
            
        finally:
            file_path.unlink()

    def test_stream_lines(self):
        """Test stream_lines method."""
        content = "Line 1\nLine 2\nLine 3\n"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            lines = list(manager.stream_lines())
            
            # Should have 3 lines
            assert len(lines) == 3
            assert lines[0] == "Line 1"
            assert lines[1] == "Line 2"
            assert lines[2] == "Line 3"
            
        finally:
            file_path.unlink()

    def test_process_large_file(self):
        """Test process_large_file method."""
        content = "Line 1\nLine 2\nLine 3\n"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            def line_counter(chunk):
                return chunk.count('\n')
            
            results = list(manager.process_large_file(line_counter))
            
            # Should have results from processing chunks
            assert len(results) > 0
            # Total line count should match
            total_lines = sum(results)
            assert total_lines == 3
            
        finally:
            file_path.unlink()

    def test_process_large_file_with_progress_callback(self):
        """Test process_large_file with progress callback."""
        content = "x" * 1000  # 1000 characters
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            progress_values = []
            
            def progress_callback(progress):
                progress_values.append(progress)
            
            def char_counter(chunk):
                return len(chunk)
            
            results = list(manager.process_large_file(char_counter, progress_callback))
            
            # Should have called progress callback
            assert len(progress_values) > 0
            assert all(0.0 <= p <= 1.0 for p in progress_values)
            
        finally:
            file_path.unlink()

    def test_search_in_file(self):
        """Test search_in_file method."""
        content = "This is a test file with some content.\nAnother line with test content.\n"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            matches = list(manager.search_in_file("test"))
            
            # Should find matches
            assert len(matches) > 0
            
            # Check match structure
            for match in matches:
                assert "chunk_index" in match
                assert "position" in match
                assert "match" in match
                assert "context" in match
                assert "test" in match["match"]
            
        finally:
            file_path.unlink()

    def test_search_in_file_case_insensitive(self):
        """Test search_in_file with case insensitive search."""
        content = "This is a TEST file with some content.\nAnother line with Test content.\n"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            matches = list(manager.search_in_file("test", case_sensitive=False))
            
            # Should find matches (both "TEST" and "Test")
            assert len(matches) > 0
            
        finally:
            file_path.unlink()

    def test_stream_json_objects(self):
        """Test stream_json_objects method."""
        content = """{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25}
{"name": "Charlie", "age": 35}
"""
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            objects = list(manager.stream_json_objects())
            
            # Should have 3 JSON objects
            assert len(objects) == 3
            
            # Check object structure
            for obj in objects:
                assert "name" in obj
                assert "content" in obj
                assert "start_position" in obj
                assert "end_position" in obj
            
        finally:
            file_path.unlink()

    def test_get_file_progress(self):
        """Test get_file_progress method."""
        manager = MockFileManager()
        
        # Without streaming reader, should return 0.0
        progress = manager.get_file_progress()
        assert progress == 0.0
        
        # With streaming reader
        content = "Test content"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            manager._streaming_reader = manager._get_streaming_reader()
            
            with manager._streaming_reader:
                progress = manager.get_file_progress()
                assert 0.0 <= progress <= 1.0
                
        finally:
            file_path.unlink()

    def test_get_file_size(self):
        """Test get_file_size method."""
        content = "Test content for size calculation"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            size = manager.get_file_size()
            expected_size = len(content.encode('utf-8'))
            assert size == expected_size
            
        finally:
            file_path.unlink()

    def test_get_file_size_nonexistent(self):
        """Test get_file_size with nonexistent file."""
        manager = MockFileManager(enable_streaming=True, path="nonexistent.txt")
        
        size = manager.get_file_size()
        assert size == 0

    def test_estimate_processing_time(self):
        """Test estimate_processing_time method."""
        content = "x" * 10000  # 10KB content
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            def simple_processor(chunk):
                return len(chunk)
            
            estimated_time = manager.estimate_processing_time(simple_processor)
            
            # Should return a positive number
            assert estimated_time > 0
            
        finally:
            file_path.unlink()

    def test_estimate_processing_time_nonexistent_file(self):
        """Test estimate_processing_time with nonexistent file."""
        manager = MockFileManager(enable_streaming=True, path="nonexistent.txt")
        
        def simple_processor(chunk):
            return len(chunk)
        
        estimated_time = manager.estimate_processing_time(simple_processor)
        assert estimated_time == 0.0

    def test_estimate_processing_time_empty_file(self):
        """Test estimate_processing_time with empty file."""
        file_path = self.create_test_file("")
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            def simple_processor(chunk):
                return len(chunk)
            
            estimated_time = manager.estimate_processing_time(simple_processor)
            assert estimated_time == 0.0
            
        finally:
            file_path.unlink()

    def test_close_streaming(self):
        """Test close_streaming method."""
        content = "Test content"
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            manager._streaming_reader = manager._get_streaming_reader()
            
            # Should have streaming reader
            assert manager._streaming_reader is not None
            
            # Close streaming
            manager.close_streaming()
            
            # Should be None after closing
            assert manager._streaming_reader is None
            
        finally:
            file_path.unlink()

    def test_close_streaming_without_reader(self):
        """Test close_streaming without active reader."""
        manager = MockFileManager()
        
        # Should not raise error
        manager.close_streaming()
        assert manager._streaming_reader is None

    def test_streaming_with_large_file(self):
        """Test streaming with a larger file."""
        # Create a larger file
        content = "".join("Line " + str(i) + "\n" for i in range(1000))
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            # Test streaming lines
            lines = list(manager.stream_lines(chunk_size=1024))
            assert len(lines) == 1000
            
            # Test streaming file
            chunks = list(manager.stream_file(chunk_size=1024))
            reconstructed = "".join(chunks)
            assert reconstructed == content
            
        finally:
            file_path.unlink()

    def test_streaming_error_handling(self):
        """Test streaming error handling."""
        manager = MockFileManager(enable_streaming=False)
        
        # Should raise error when streaming is not enabled
        # Note: These are generators, so we need to iterate to trigger the error
        with pytest.raises(RuntimeError, match="Streaming not enabled"):
            list(manager.stream_file())
        
        with pytest.raises(RuntimeError, match="Streaming not enabled"):
            list(manager.stream_lines())
        
        with pytest.raises(RuntimeError, match="Streaming not enabled"):
            list(manager.stream_sections("[", "]"))

    def test_streaming_with_different_encodings(self):
        """Test streaming with different encodings."""
        content = "Hello 世界"  # Contains non-ASCII characters
        file_path = self.create_test_file(content, encoding="utf-8")
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            # Test with UTF-8 encoding
            chunks = list(manager.stream_file(encoding="utf-8"))
            reconstructed = "".join(chunks)
            assert reconstructed == content
            
        finally:
            file_path.unlink()

    def test_streaming_performance(self):
        """Test streaming performance characteristics."""
        content = "x" * 100000  # 100KB content
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            # Test streaming performance
            start_time = time.time()
            chunks = list(manager.stream_file(chunk_size=1024))
            streaming_time = time.time() - start_time
            
            # Should complete in reasonable time
            assert streaming_time < 5.0  # Should complete in less than 5 seconds
            
            # Verify content integrity
            reconstructed = "".join(chunks)
            assert reconstructed == content
            
        finally:
            file_path.unlink()

    def test_streaming_thread_safety(self):
        """Test streaming thread safety."""
        import threading
        
        content = "".join("Line " + str(i) + "\n" for i in range(100))
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            results = []
            
            def worker():
                lines = list(manager.stream_lines())
                results.append(len(lines))
            
            # Create multiple threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # All should have processed the same number of lines
            assert all(result == 100 for result in results)
            assert len(results) == 3
            
        finally:
            file_path.unlink()

    def test_streaming_with_custom_chunk_sizes(self):
        """Test streaming with different chunk sizes."""
        content = "x" * 1000  # 1KB content
        file_path = self.create_test_file(content)
        
        try:
            manager = MockFileManager(enable_streaming=True, path=file_path)
            
            # Test with small chunk size
            chunks_small = list(manager.stream_file(chunk_size=100))
            assert len(chunks_small) == 10  # 1000 / 100 = 10 chunks
            
            # Test with large chunk size
            chunks_large = list(manager.stream_file(chunk_size=2000))
            assert len(chunks_large) == 1  # 1000 < 2000, so 1 chunk
            
            # Both should reconstruct the same content
            reconstructed_small = "".join(chunks_small)
            reconstructed_large = "".join(chunks_large)
            assert reconstructed_small == content
            assert reconstructed_large == content
            
        finally:
            file_path.unlink()
