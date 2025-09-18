"""
Smart Cache System

This module provides an advanced caching system with TTL (Time-To-Live), LRU
(Least Recently Used) eviction, and automatic invalidation. The cache is
thread-safe and provides comprehensive statistics and monitoring.

Key Features:
- TTL (Time-To-Live) support with automatic expiration
- LRU (Least Recently Used) eviction policy
- Size-based eviction when cache limit is reached
- Thread-safe operations with locking
- Pattern-based invalidation
- Comprehensive statistics and monitoring
- Memory usage tracking
"""

from typing import Optional, Any, List, Dict
from threading import RLock
from collections import OrderedDict
import time
import sys
import fnmatch

from .types import CacheEntry

class SmartCache:
    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: float = 100.0,
        default_ttl: Optional[float] = None,
        cleanup_interval: float = 60.0,
        track_stats: bool = True
    ):
        """
        Initialize the intelligent cache.
        
        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
            default_ttl: Default TTL in seconds (None = no expiration)
            cleanup_interval: Interval for automatic cleanup in seconds
            track_stats: Track statistics
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.track_stats = track_stats

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()
        self._total_memory = 0
        self._last_cleanup = time.time()
        
        if self.track_stats:
            self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_cleanups": 0,
            "memory_cleanups": 0
        }
            
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is expired."""
        if entry.ttl is None:
            return False
        return time.time() - entry.timestamp > entry.ttl
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate the size of a value in bytes."""
        try:
            return sys.getsizeof(value)
        except:
            # Fallback estimation
            return 1024  # 1KB default
        
    def _get_expired_keys(self) -> List[str]:
        """Get expired keys."""
        return [key for key, entry in self._cache.items() if self._is_expired(entry)]
        
    def _remove_from_cache(self, key_or_entry: str | CacheEntry) -> None:
        """Remove a key from the cache."""
        with self._lock:
            entry = self._cache[key_or_entry] if isinstance(key_or_entry, str) else key_or_entry
            self._total_memory -= entry.size
            del self._cache[key_or_entry]
            
        
    def _cleanup_if_needed(self) -> None:
        """Clean up expired entries if needed."""
        current_time = time.time()
        if current_time - self._last_cleanup < self.cleanup_interval:
            return
        
        self._last_cleanup = current_time
        
        # Remove expired entries
        expired_keys = self._get_expired_keys()
        
        if expired_keys:
            with self._lock:
                for key in expired_keys:
                    self._remove_from_cache(key)
                    
                    if self.track_stats:
                        self._stats["expired_cleanups"] += 1
                        
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return
        
        # Remove the first (oldest) entry
        with self._lock:
            key, entry = self._cache.popitem(last=False)
            self._total_memory -= entry.size
            
            if self.track_stats:
                self._stats["evictions"] += 1
                self._stats["memory_cleanups"] += entry.size
    
    def _evict_if_needed(self) -> None:
        """Evict entries if cache limits are exceeded."""
        # Evict by size limit
        while len(self._cache) > self.max_size:
            self._evict_lru()
        
        # Evict by memory limit
        while self._total_memory > self.max_memory_bytes:
            self._evict_lru()
    
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            self._cleanup_if_needed()
            
            if key not in self._cache:
                if self.track_stats:
                    self._stats["misses"] += 1
                return default
            
            entry = self._cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                self._remove_from_cache(entry)
                
                if self.track_stats:
                    self._stats["misses"] += 1
                    self._stats["expired_cleanups"] += 1
                return default
            
            # Update access statistics
            entry.access_count += 1
            entry.last_access = time.time()
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            if self.track_stats:
                self._stats["hits"] += 1
                
            return entry.value
            
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[float] = None,
        size: Optional[int] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            size: Estimated size in bytes (None = auto-calculate)
        """
        with self._lock:
            self._cleanup_if_needed()
            
            # Calculate size if not provided
            if size is None:
                size = self._estimate_size(value)
            
            # Use default TTL if not provided
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove existing entry if it exists
            if key in self._cache:
                self._remove_from_cache(key)
                
            # Create new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                last_access=time.time(),
                ttl=ttl,
                size=size
            )
            
            self._cache[key] = entry
            self._total_memory += size
            
            # Evict if necessary
            self._evict_if_needed()
            
            
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            self._remove_from_cache(key)
                
            return True
        
    def has_key(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        with self._lock:
            return key in self._cache
        
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._total_memory = 0
            
            
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Number of keys invalidated
        """
        
        with self._lock:
            keys_to_delete = [
                key for key in self._cache.keys() 
                if fnmatch.fnmatch(key, pattern)
            ]
            
            for key in keys_to_delete:
                self.delete(key)
            
            return len(keys_to_delete)
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            hit_rate = 0.0
            total_requests = self._stats["hits"] + self._stats["misses"]
            if total_requests > 0:
                hit_rate = self._stats["hits"] / total_requests
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_mb": self._total_memory / (1024 * 1024),
                "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                "hit_rate": hit_rate,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "expired_cleanups": self._stats["expired_cleanups"],
                "memory_cleanups": self._stats["memory_cleanups"]
            }