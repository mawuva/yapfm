"""
Streaming Mixin

This module provides streaming functionality for large files.
The StreamingMixin integrates StreamingFileReader with file operations
to enable processing of very large files that don't fit in memory.
"""

# mypy: ignore-errors

from typing import Any, Callable, Dict, Iterator, Optional

from yapfm.cache.streaming_reader import StreamingFileReader


class StreamingMixin:
    """
    Mixin providing streaming functionality for large files.

    This mixin enables processing of very large files:
    - Chunked reading for memory efficiency
    - Section extraction from large files
    - Custom processing with progress tracking
    - Search across large files
    """

    def _get_streaming_reader(
        self,
        chunk_size: Optional[int] = 1024 * 1024,
        buffer_size: int = 8192,
        encoding: str = "utf-8",
    ) -> StreamingFileReader:
        """Get or create a streaming reader for the current file."""
        if not getattr(self, "enable_streaming", False):
            raise RuntimeError(
                "Streaming not enabled. Set enable_streaming=True in constructor."
            )

        if not self.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        # Create new reader with current parameters
        reader = StreamingFileReader(
            self.path, chunk_size=chunk_size, buffer_size=buffer_size, encoding=encoding
        )

        return reader

    def create_streaming_reader(
        self,
        chunk_size: Optional[int] = 1024 * 1024,
        buffer_size: int = 8192,
        encoding: str = "utf-8",
    ) -> StreamingFileReader:
        """
        Create a streaming reader for use as a context manager.

        Args:
            chunk_size: Size of each chunk in bytes
            buffer_size: Buffer size for reading
            encoding: File encoding

        Returns:
            StreamingFileReader instance for use as context manager

        Example:
            >>> with fm.create_streaming_reader() as reader:
            ...     for chunk in reader.read_chunks():
            ...         process_chunk(chunk)
        """
        return self._get_streaming_reader(chunk_size, buffer_size, encoding)

    def stream_file(
        self,
        chunk_size: Optional[int] = 1024 * 1024,  # 1MB default
        buffer_size: int = 8192,  # 8KB default
        encoding: str = "utf-8",  # utf-8 default
    ) -> Iterator[str]:
        """
        Stream file chunks from a large file.

        Args:
            chunk_size: Size of each chunk in bytes (default: 1MB)
            buffer_size: Buffer size for reading
            encoding: File encoding

        Yields:
            File chunks as strings

        Example:
            >>> for chunk in fm.stream_file():
            ...     process_chunk(chunk)
        """
        reader = self._get_streaming_reader(chunk_size, buffer_size, encoding)

        with reader:
            for chunk in reader.read_chunks():
                yield chunk

    def stream_sections(
        self,
        section_marker: str,
        end_marker: Optional[str] = None,
        chunk_size: Optional[int] = 1024 * 1024,  # 1MB default
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream file sections from a large file.

        Args:
            section_marker: Marker that starts a section
            end_marker: Optional marker that ends a section
            chunk_size: Size of each chunk in bytes

        Yields:
            Dictionary with section information

        Example:
            >>> for section in fm.stream_sections("[database]"):
            ...     print(f"Section: {section['name']}")
            ...     print(f"Content: {section['content']}")
        """
        reader = self._get_streaming_reader(chunk_size)

        with reader:
            yield from reader.extract_sections(section_marker, end_marker)

    def stream_lines(
        self,
        chunk_size: Optional[int] = 1024 * 1024,  # 1MB default
    ) -> Iterator[str]:
        """
        Stream file lines from a large file.

        Args:
            chunk_size: Size of each chunk in bytes

        Yields:
            File lines

        Example:
            >>> for line in fm.stream_lines():
            ...     if "error" in line.lower():
            ...         print(f"Error line: {line}")
        """
        reader = self._get_streaming_reader(chunk_size)

        with reader:
            for line in reader.read_lines():
                yield line

    def process_large_file(
        self,
        processor: Callable[[str], Any],
        progress_callback: Optional[Callable[[float], None]] = None,
        chunk_size: Optional[int] = 1024 * 1024,  # 1MB default
    ) -> Iterator[Any]:
        """
        Process a large file with a custom processor function.

        Args:
            processor: Function to process each chunk
            progress_callback: Optional callback for progress updates
            chunk_size: Size of each chunk in bytes

        Yields:
            Results from the processor function

        Example:
            >>> def count_lines(chunk):
            ...     return chunk.count('\n')
            >>>
            >>> total_lines = 0
            >>> for line_count in fm.process_large_file(count_lines):
            ...     total_lines += line_count
            ...     print(f"Processed {total_lines} lines so far")
        """
        reader = self._get_streaming_reader(chunk_size)

        with reader:
            yield from reader.process_chunks(processor, progress_callback)

    def search_in_file(
        self,
        search_term: str,
        case_sensitive: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Search for a term across a large file.

        Args:
            search_term: Term to search for
            case_sensitive: Whether search is case sensitive
            chunk_size: Size of each chunk in bytes

        Yields:
            Dictionary with match information

        Example:
            >>> for match in fm.search_in_file("database"):
            ...     print(f"Found at position {match['position']}")
            ...     print(f"Context: {match['context']}")
        """
        reader = self._get_streaming_reader(chunk_size)

        with reader:
            yield from reader.find_in_chunks(search_term, case_sensitive)

    def stream_json_objects(
        self,
        object_marker: str = "{",
        end_marker: str = "}",
        chunk_size: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream JSON objects from a large file.

        Args:
            object_marker: Marker that starts a JSON object
            end_marker: Marker that ends a JSON object
            chunk_size: Size of each chunk in bytes

        Yields:
            Dictionary with JSON object information

        Example:
            >>> for obj in fm.stream_json_objects():
            ...     print(f"JSON object: {obj['content']}")
        """
        reader = self._get_streaming_reader(chunk_size)

        with reader:
            yield from reader.extract_sections(object_marker, end_marker)

    def get_file_progress(self) -> float:
        """
        Get current streaming progress as a percentage.

        Returns:
            Progress percentage (0.0 to 1.0)
        """
        if self._streaming_reader is not None:
            return self._streaming_reader.get_progress()
        return 0.0

    def get_file_size(self) -> int:
        """
        Get total file size in bytes.

        Returns:
            File size in bytes
        """
        if not self.exists():
            return 0
        return self.path.stat().st_size

    def estimate_processing_time(
        self,
        processor: Callable[[str], Any],
        sample_chunk_size: int = 1024 * 1024,  # 1MB sample
    ) -> float:
        """
        Estimate processing time for the entire file.

        Args:
            processor: Function to process chunks
            sample_chunk_size: Size of sample chunk for estimation

        Returns:
            Estimated processing time in seconds
        """
        import time

        if not self.exists():
            return 0.0

        file_size = self.get_file_size()
        if file_size == 0:
            return 0.0

        # Process a sample chunk
        reader = self._get_streaming_reader(sample_chunk_size)

        with reader:
            reader.open()
            sample_chunk = reader.read_chunk()
            if sample_chunk is None:
                return 0.0

            start_time = time.time()
            processor(sample_chunk)
            end_time = time.time()

            sample_time = end_time - start_time
            sample_ratio = len(sample_chunk) / file_size

            return sample_time / sample_ratio

    def close_streaming(self) -> None:
        """Close any active streaming reader."""
        if self._streaming_reader is not None:
            self._streaming_reader.close()
            self._streaming_reader = None
