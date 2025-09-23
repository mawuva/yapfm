# StreamingMixin

Provides streaming functionality for processing large files that don't fit in memory.

## Features

- **Chunked Reading**: Process files in configurable chunks
- **Memory Efficient**: Handle files larger than available RAM
- **Multiple Formats**: Support for different file encodings
- **Progress Tracking**: Monitor processing progress
- **Search Capabilities**: Search within large files
- **Section Extraction**: Extract specific sections from large files
- **Thread Safety**: Safe for concurrent access

## Methods

### create_streaming_reader

```python
def create_streaming_reader(
    self,
    chunk_size: Optional[int] = 1024 * 1024,
    buffer_size: int = 8192,
    encoding: str = "utf-8"
) -> StreamingFileReader
```

Create a streaming reader for use as a context manager.

**Parameters:**
- `chunk_size` (Optional[int]): Size of each chunk in bytes
- `buffer_size` (int): Buffer size for reading
- `encoding` (str): File encoding

**Returns:**
- `StreamingFileReader`: StreamingFileReader instance for use as context manager

**Example:**
```python
with fm.create_streaming_reader() as reader:
    for chunk in reader.read_chunks():
        process_chunk(chunk)
```

### stream_file

```python
def stream_file(
    self,
    chunk_size: Optional[int] = 1024 * 1024,  # 1MB par défaut
    buffer_size: int = 8192,  # 8KB par défaut
    encoding: str = "utf-8"  # utf-8 par défaut
) -> Iterator[str]
```

Stream file chunks from a large file.

**Parameters:**
- `chunk_size` (Optional[int]): Size of each chunk in bytes. Default: 1MB
- `buffer_size` (int): Buffer size for reading. Default: 8KB
- `encoding` (str): File encoding. Default: utf-8

**Yields:**
- `str`: File chunks as strings

**Example:**
```python
for chunk in fm.stream_file():
    process_chunk(chunk)
```

### stream_lines

```python
def stream_lines(
    self,
    chunk_size: Optional[int] = 1024 * 1024  # 1MB par défaut
) -> Iterator[str]
```

Stream file lines from a large file.

**Parameters:**
- `chunk_size` (Optional[int]): Size of each chunk in bytes. Default: 1MB

**Yields:**
- `str`: File lines

**Example:**
```python
for line in fm.stream_lines():
    if "error" in line.lower():
        print(f"Error line: {line}")
```

### stream_sections

```python
def stream_sections(
    self,
    section_marker: str,
    end_marker: Optional[str] = None,
    chunk_size: Optional[int] = 1024 * 1024  # 1MB par défaut
) -> Iterator[Dict[str, Any]]
```

Stream file sections from a large file.

**Parameters:**
- `section_marker` (str): Marker that starts a section
- `end_marker` (Optional[str]): Optional marker that ends a section
- `chunk_size` (Optional[int]): Size of each chunk in bytes. Default: 1MB

**Yields:**
- `Dict[str, Any]`: Dictionary with section information

**Example:**
```python
for section in fm.stream_sections("[", "]"):
    print(f"Section: {section['name']}")
    print(f"Content: {section['content']}")
```

### process_large_file

```python
def process_large_file(
    self,
    processor: Callable[[str], Any],
    progress_callback: Optional[Callable[[float], None]] = None
) -> Iterator[Any]
```

Process a large file with a custom processor function.

**Parameters:**
- `processor` (Callable[[str], Any]): Function to process each chunk
- `progress_callback` (Optional[Callable[[float], None]]): Callback for progress updates

**Yields:**
- `Any`: Results from the processor function

**Example:**
```python
def count_lines(chunk):
    return chunk.count('\n')

def progress_callback(progress):
    print(f"Progress: {progress:.1%}")

results = list(fm.process_large_file(count_lines, progress_callback))
total_lines = sum(results)
```

### search_in_file

```python
def search_in_file(
    self,
    pattern: str,
    case_sensitive: bool = True,
    context_lines: int = 2
) -> Iterator[Dict[str, Any]]
```

Search for a pattern in a large file.

**Parameters:**
- `pattern` (str): Pattern to search for
- `case_sensitive` (bool): Whether search is case sensitive. Default: True
- `context_lines` (int): Number of context lines around matches. Default: 2

**Yields:**
- `Dict[str, Any]`: Match information with context

**Example:**
```python
for match in fm.search_in_file("error", case_sensitive=False):
    print(f"Found: {match['match']}")
    print(f"Context: {match['context']}")
```

### get_file_progress

```python
def get_file_progress(self) -> float
```

Get the current progress of file processing.

**Returns:**
- `float`: Progress as a value between 0.0 and 1.0

**Example:**
```python
progress = fm.get_file_progress()
print(f"Progress: {progress:.1%}")
```

### get_file_size

```python
def get_file_size(self) -> int
```

Get the size of the current file in bytes.

**Returns:**
- `int`: File size in bytes

**Example:**
```python
size = fm.get_file_size()
print(f"File size: {size} bytes")
```

### estimate_processing_time

```python
def estimate_processing_time(
    self,
    processor: Callable[[str], Any]
) -> float
```

Estimate the time needed to process the file with a given processor.

**Parameters:**
- `processor` (Callable[[str], Any]): Function to estimate processing time for

**Returns:**
- `float`: Estimated processing time in seconds

**Example:**
```python
def simple_processor(chunk):
    return len(chunk)

estimated_time = fm.estimate_processing_time(simple_processor)
print(f"Estimated time: {estimated_time:.2f} seconds")
```
