"""
Tests for streaming file reader.

This module tests the StreamingFileReader class and its functionality
for reading large files in chunks.
"""

import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from yapfm.cache.streaming_reader import StreamingFileReader


class TestStreamingFileReader:
    """Test cases for StreamingFileReader class."""

    def create_test_file(self, content: str, encoding: str = "utf-8") -> Path:
        """Create a temporary test file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, delete=False) as f:
            f.write(content)
            return Path(f.name)

    def test_streaming_reader_initialization(self):
        """Test StreamingFileReader initialization."""
        file_path = self.create_test_file("test content")
        
        try:
            reader = StreamingFileReader(file_path)
            
            assert reader.file_path == file_path
            assert reader.chunk_size == 1024 * 1024  # 1MB default
            assert reader.buffer_size == 8192  # 8KB default
            assert reader.encoding == "utf-8"
            assert reader._file_handle is None
            assert reader._position == 0
            assert reader._total_size > 0
        finally:
            file_path.unlink()

    def test_streaming_reader_initialization_custom_params(self):
        """Test StreamingFileReader initialization with custom parameters."""
        file_path = self.create_test_file("test content")
        
        try:
            reader = StreamingFileReader(
                file_path,
                chunk_size=512,
                buffer_size=1024,
                encoding="latin-1"
            )
            
            assert reader.chunk_size == 512
            assert reader.buffer_size == 1024
            assert reader.encoding == "latin-1"
        finally:
            file_path.unlink()

    def test_streaming_reader_nonexistent_file(self):
        """Test StreamingFileReader with nonexistent file."""
        file_path = Path("nonexistent_file.txt")
        reader = StreamingFileReader(file_path)
        
        assert reader._total_size == 0

    def test_streaming_reader_context_manager(self):
        """Test StreamingFileReader as context manager."""
        file_path = self.create_test_file("test content")
        
        try:
            with StreamingFileReader(file_path) as reader:
                assert reader._file_handle is not None
                assert reader._position == 0
            
            # File should be closed after context
            assert reader._file_handle is None
        finally:
            file_path.unlink()

    def test_streaming_reader_open_close(self):
        """Test manual open and close operations."""
        file_path = self.create_test_file("test content")
        
        try:
            reader = StreamingFileReader(file_path)
            
            # Initially closed
            assert reader._file_handle is None
            
            # Open file
            reader.open()
            assert reader._file_handle is not None
            
            # Close file
            reader.close()
            assert reader._file_handle is None
        finally:
            file_path.unlink()

    def test_streaming_reader_read_chunk(self):
        """Test reading chunks from file."""
        content = "Hello, World! This is a test file with some content."
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=10)
            
            with reader:
                chunks = []
                while True:
                    chunk = reader.read_chunk()
                    if chunk is None:
                        break
                    chunks.append(chunk)
                
                # Verify all content was read
                reconstructed = "".join(chunks)
                assert reconstructed == content
                
                # Verify we got multiple chunks
                assert len(chunks) > 1
                
                # Verify chunk sizes are reasonable
                for chunk in chunks:
                    assert len(chunk) <= 10  # chunk_size
        finally:
            file_path.unlink()

    def test_streaming_reader_read_chunks_generator(self):
        """Test read_chunks generator."""
        content = "Line 1\nLine 2\nLine 3\n"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=5)
            
            with reader:
                chunks = list(reader.read_chunks())
                
                # Should have multiple chunks
                assert len(chunks) > 1
                assert "".join(chunks) == content
        finally:
            file_path.unlink()

    def test_streaming_reader_read_lines(self):
        """Test reading lines from file."""
        content = "Line 1\nLine 2\nLine 3\n"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path)
            
            with reader:
                lines = list(reader.read_lines())
                
                assert lines == ["Line 1", "Line 2", "Line 3"]
        finally:
            file_path.unlink()

    def test_streaming_reader_seek_tell(self):
        """Test seek and tell operations."""
        content = "0123456789"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=3)
            
            with reader:
                # Initial position
                assert reader.tell() == 0
                
                # Read a chunk
                chunk = reader.read_chunk()
                assert chunk == "012"
                assert reader.tell() == 3
                
                # Seek to beginning
                reader.seek(0)
                assert reader.tell() == 0
                
                # Read again
                chunk = reader.read_chunk()
                assert chunk == "012"
        finally:
            file_path.unlink()

    def test_streaming_reader_progress(self):
        """Test progress calculation."""
        content = "x" * 1000  # 1000 characters
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=100)
            
            with reader:
                # Initial progress
                assert reader.get_progress() == 0.0
                
                # Read some chunks
                reader.read_chunk()  # 100 chars
                progress = reader.get_progress()
                assert 0.0 < progress < 1.0
                
                # Read all chunks
                while reader.read_chunk() is not None:
                    pass
                
                # Should be at 100% or close
                assert reader.get_progress() >= 0.99
        finally:
            file_path.unlink()

    def test_streaming_reader_get_size(self):
        """Test getting file size."""
        content = "test content"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path)
            
            # Size should match file size
            expected_size = len(content.encode('utf-8'))
            assert reader.get_size() == expected_size
        finally:
            file_path.unlink()

    def test_streaming_reader_process_chunks(self):
        """Test processing chunks with custom function."""
        content = "Hello\nWorld\nTest\n"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=5)
            
            def processor(chunk):
                return chunk.upper()
            
            with reader:
                results = list(reader.process_chunks(processor))
                
                # Should process all chunks
                assert len(results) > 0
                assert all(isinstance(result, str) for result in results)
        finally:
            file_path.unlink()

    def test_streaming_reader_process_chunks_with_progress_callback(self):
        """Test processing chunks with progress callback."""
        content = "x" * 100
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=10)
            
            progress_values = []
            
            def progress_callback(progress):
                progress_values.append(progress)
            
            def processor(chunk):
                return len(chunk)
            
            with reader:
                list(reader.process_chunks(processor, progress_callback))
                
                # Should have called progress callback
                assert len(progress_values) > 0
                assert all(0.0 <= p <= 1.0 for p in progress_values)
        finally:
            file_path.unlink()

    def test_streaming_reader_find_in_chunks(self):
        """Test finding text in chunks."""
        content = "Hello World\nThis is a test\nAnother line\n"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=10)
            
            with reader:
                matches = list(reader.find_in_chunks("test"))
                
                assert len(matches) == 1
                match = matches[0]
                assert "test" in match["match"]
                assert "test" in match["context"]
        finally:
            file_path.unlink()

    def test_streaming_reader_find_in_chunks_case_insensitive(self):
        """Test case-insensitive search in chunks."""
        content = "Hello World\nThis is a TEST\nAnother line\n"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=10)
            
            with reader:
                matches = list(reader.find_in_chunks("test", case_sensitive=False))
                
                assert len(matches) == 1
                match = matches[0]
                assert "TEST" in match["match"]
        finally:
            file_path.unlink()

    def test_streaming_reader_extract_sections(self):
        """Test extracting sections from file."""
        content = """[section1]
key1 = value1
key2 = value2

[section2]
key3 = value3
key4 = value4
"""
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path)
            
            with reader:
                sections = list(reader.extract_sections("[", "]"))
                
                assert len(sections) == 2
                assert sections[0]["name"] == "[section1]"
                assert "key1 = value1" in sections[0]["content"]
                assert sections[1]["name"] == "[section2]"
                assert "key3 = value3" in sections[1]["content"]
        finally:
            file_path.unlink()

    def test_streaming_reader_extract_sections_with_end_marker(self):
        """Test extracting sections with end marker."""
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
            reader = StreamingFileReader(file_path)
            
            with reader:
                sections = list(reader.extract_sections("START", "END"))
                
                assert len(sections) == 2
                assert sections[0]["name"] == "START"
                assert "Line 1" in sections[0]["content"]
                assert "Line 2" in sections[0]["content"]
                assert sections[1]["name"] == "START"
                assert "Line 3" in sections[1]["content"]
                assert "Line 4" in sections[1]["content"]
        finally:
            file_path.unlink()

    def test_streaming_reader_error_handling(self):
        """Test error handling for various scenarios."""
        file_path = Path("nonexistent_file.txt")
        reader = StreamingFileReader(file_path)
        
        # Should not raise error for nonexistent file
        assert reader._total_size == 0
        
        # Should raise error when trying to read without opening
        with pytest.raises(RuntimeError, match="File not open"):
            reader.read_chunk()

    def test_streaming_reader_thread_safety(self):
        """Test thread safety of streaming reader."""
        content = "x" * 1000
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=100)
            results = []
            
            def worker():
                with reader:
                    chunk = reader.read_chunk()
                    if chunk:
                        results.append(len(chunk))
            
            # Create multiple threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Should have some results
            assert len(results) > 0
        finally:
            file_path.unlink()

    def test_streaming_reader_different_encodings(self):
        """Test streaming reader with different encodings."""
        # Test with UTF-8
        content_utf8 = "Hello 世界"
        file_path_utf8 = self.create_test_file(content_utf8, "utf-8")
        
        try:
            reader = StreamingFileReader(file_path_utf8, encoding="utf-8")
            
            with reader:
                chunk = reader.read_chunk()
                assert chunk == content_utf8
        finally:
            file_path_utf8.unlink()

    def test_streaming_reader_empty_file(self):
        """Test streaming reader with empty file."""
        file_path = self.create_test_file("")
        
        try:
            reader = StreamingFileReader(file_path)
            
            with reader:
                chunk = reader.read_chunk()
                assert chunk is None
                
                progress = reader.get_progress()
                assert progress == 0.0
        finally:
            file_path.unlink()

    def test_streaming_reader_large_file_simulation(self):
        """Test streaming reader with simulated large file."""
        # Create a file with known size
        content = "x" * 10000  # 10KB
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=1000)  # 1KB chunks
            
            with reader:
                chunks = list(reader.read_chunks())
                
                # Should have 10 chunks
                assert len(chunks) == 10
                assert all(len(chunk) == 1000 for chunk in chunks)
                
                # Reconstruct content
                reconstructed = "".join(chunks)
                assert reconstructed == content
        finally:
            file_path.unlink()

    def test_streaming_reader_position_tracking(self):
        """Test position tracking during reading."""
        content = "0123456789"
        file_path = self.create_test_file(content)
        
        try:
            reader = StreamingFileReader(file_path, chunk_size=3)
            
            with reader:
                # Read first chunk
                chunk1 = reader.read_chunk()
                assert chunk1 == "012"
                assert reader.tell() == 3
                
                # Read second chunk
                chunk2 = reader.read_chunk()
                assert chunk2 == "345"
                assert reader.tell() == 6
                
                # Read third chunk
                chunk3 = reader.read_chunk()
                assert chunk3 == "678"
                assert reader.tell() == 9
                
                # Read last chunk
                chunk4 = reader.read_chunk()
                assert chunk4 == "9"
                assert reader.tell() == 10
        finally:
            file_path.unlink()
