"""
Types for the cache system.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheEntry:
    """
    A cache entry with metadata.

    This dataclass represents a single entry in the cache with all its
    associated metadata for tracking usage, expiration, and statistics.

    Attributes:
        value (Any): The cached value.
        timestamp (float): When the entry was created (Unix timestamp).
        access_count (int): Number of times this entry has been accessed.
        last_access (float): When the entry was last accessed (Unix timestamp).
        ttl (Optional[float]): Time-to-live in seconds, None for no expiration.
        size (int): Size of the entry in bytes (estimated).

    Example:
        >>> entry = CacheEntry(
        ...     value="cached_data",
        ...     timestamp=time.time(),
        ...     ttl=3600  # 1 hour
        ... )
        >>> print(f"Entry created at: {entry.timestamp}")
        >>> print(f"TTL: {entry.ttl} seconds")
    """

    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    ttl: Optional[float] = None
    size: int = 0
