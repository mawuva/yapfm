"""
Streaming reader for very large files.
"""

import io
import threading
from typing import Any, Dict, Iterator, Optional, Union, Callable, List
from pathlib import Path


class StreamingFileReader:
    """
    Streaming reader for very large files that don't fit in memory.
    
    This class provides chunked reading of large files, allowing processing
    of files larger than available memory.
    """
    
    def __init__(
        self,
        file_path: Union[str, Path],
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        buffer_size: int = 8192,  # 8KB buffer
        encoding: str = "utf-8"
    ):
        """
        Initialize the streaming reader.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of each chunk in bytes
            buffer_size: Buffer size for reading
            encoding: File encoding
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        self.encoding = encoding
        
        self._file_handle: Optional[io.TextIOWrapper] = None
        self._lock = threading.RLock()
        self._position = 0
        self._total_size = 0
        
        if self.file_path.exists():
            self._total_size = self.file_path.stat().st_size
    
    def __enter__(self) -> "StreamingFileReader":
        """Enter context manager."""
        self.open()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]) -> None:
        """Exit context manager."""
        self.close()
    
    def open(self) -> None:
        """Open the file for streaming."""
        with self._lock:
            if self._file_handle is None:
                self._file_handle = open(
                    self.file_path, 
                    'r', 
                    encoding=self.encoding,
                    buffering=self.buffer_size
                )
                self._position = 0
    
    def close(self) -> None:
        """Close the file."""
        with self._lock:
            if self._file_handle is not None:
                self._file_handle.close()
                self._file_handle = None
    
    def read_chunk(self) -> Optional[str]:
        """
        Read the next chunk from the file.
        
        Returns:
            Chunk content or None if EOF
        """
        with self._lock:
            if self._file_handle is None:
                raise RuntimeError("File not open. Call open() first.")
            
            chunk = self._file_handle.read(self.chunk_size)
            if chunk:
                self._position += len(chunk.encode(self.encoding))
                return chunk
            return None
    
    def read_chunks(self) -> Iterator[str]:
        """
        Generator that yields chunks from the file.
        
        Yields:
            File chunks
        """
        while True:
            chunk = self.read_chunk()
            if chunk is None:
                break
            yield chunk
    
    def read_lines(self) -> Iterator[str]:
        """
        Generator that yields lines from the file.
        
        Yields:
            File lines
        """
        with self._lock:
            if self._file_handle is None:
                raise RuntimeError("File not open. Call open() first.")
            
            # Reset position to beginning
            self._file_handle.seek(0)
            self._position = 0
            
            for line in self._file_handle:
                self._position += len(line.encode(self.encoding))
                yield line.rstrip('\n\r')
    
    def seek(self, position: int) -> None:
        """
        Seek to a specific position in the file.
        
        Args:
            position: Position to seek to
        """
        with self._lock:
            if self._file_handle is None:
                raise RuntimeError("File not open. Call open() first.")
            
            self._file_handle.seek(position)
            self._position = position
    
    def tell(self) -> int:
        """
        Get current position in the file.
        
        Returns:
            Current position
        """
        with self._lock:
            return self._position
    
    def get_progress(self) -> float:
        """
        Get reading progress as a percentage.
        
        Returns:
            Progress percentage (0.0 to 1.0)
        """
        with self._lock:
            if self._total_size == 0:
                return 0.0
            return min(self._position / self._total_size, 1.0)
    
    def get_size(self) -> int:
        """
        Get total file size.
        
        Returns:
            File size in bytes
        """
        return self._total_size
    
    def process_chunks(
        self, 
        processor: Callable[[str], Any], 
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Iterator[Any]:
        """
        Process file chunks with a custom processor function.
        
        Args:
            processor: Function to process each chunk
            progress_callback: Optional callback for progress updates
            
        Yields:
            Results from the processor function
        """
        for chunk in self.read_chunks():
            result = processor(chunk)
            if progress_callback:
                progress_callback(self.get_progress())
            yield result
    
    def find_in_chunks(
        self, 
        search_term: str, 
        case_sensitive: bool = True
    ) -> Iterator[Dict[str, Any]]:
        """
        Search for a term across file chunks.
        
        Args:
            search_term: Term to search for
            case_sensitive: Whether search is case sensitive
            
        Yields:
            Dictionary with match information
        """
        if not case_sensitive:
            search_term = search_term.lower()
        
        chunk_index = 0
        for chunk in self.read_chunks():
            if not case_sensitive:
                chunk_lower = chunk.lower()
            else:
                chunk_lower = chunk
            
            start = 0
            while True:
                pos = chunk_lower.find(search_term, start)
                if pos == -1:
                    break
                
                yield {
                    "chunk_index": chunk_index,
                    "position": self._position - len(chunk) + pos,
                    "match": chunk[pos:pos + len(search_term)],
                    "context": chunk[max(0, pos - 50):pos + len(search_term) + 50]
                }
                
                start = pos + 1
            
            chunk_index += 1
    
    def extract_sections(
        self, 
        section_marker: str, 
        end_marker: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Extract sections from a file based on markers.
        
        Args:
            section_marker: Marker that starts a section
            end_marker: Optional marker that ends a section
            
        Yields:
            Dictionary with section information
        """
        current_section: Optional[str] = None
        section_content: List[str] = []
        section_start = 0
        
        for line in self.read_lines():
            if section_marker in line:
                # Save previous section
                if current_section is not None:
                    yield {
                        "name": current_section,
                        "content": "\n".join(section_content),
                        "start_position": section_start,
                        "end_position": self._position
                    }
                
                # Start new section
                current_section = line.strip()
                section_content = []
                section_start = self._position
            
            elif end_marker and end_marker in line:
                # End current section
                if current_section is not None:
                    yield {
                        "name": current_section,
                        "content": "\n".join(section_content),
                        "start_position": section_start,
                        "end_position": self._position
                    }
                    current_section = None
                    section_content = []
            
            elif current_section is not None:
                # Add to current section
                section_content.append(line)
        
        # Yield final section if exists
        if current_section is not None:
            yield {
                "name": current_section,
                "content": "\n".join(section_content),
                "start_position": section_start,
                "end_position": self._position
            }
