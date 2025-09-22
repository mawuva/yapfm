"""
Tests for lazy loading system.

This module tests the LazySectionLoader class and its functionality.
"""

import time
from unittest.mock import Mock, patch

import pytest

from yapfm.cache.lazy_loading import LazySectionLoader
from yapfm.cache.smart_cache import SmartCache


class TestLazySectionLoader:
    """Test cases for LazySectionLoader class."""

    def test_lazy_section_loader_initialization(self):
        """Test LazySectionLoader initialization."""
        def loader_func():
            return {"data": "test"}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        assert loader._loader_func == loader_func
        assert loader._section_path == "test_section"
        assert loader._cache is None
        assert loader._loaded is False
        assert loader._value is None
        assert loader._load_error is None

    def test_lazy_section_loader_initialization_with_cache(self):
        """Test LazySectionLoader initialization with cache."""
        def loader_func():
            return {"data": "test"}
        
        cache = SmartCache()
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        assert loader._cache == cache

    def test_lazy_section_loader_get_first_time(self):
        """Test getting value for the first time (lazy loading)."""
        def loader_func():
            return {"data": "test", "timestamp": time.time()}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # First call should trigger loading
        result = loader.get()
        
        assert result["data"] == "test"
        assert "timestamp" in result
        assert loader._loaded is True
        assert loader._value == result

    def test_lazy_section_loader_get_subsequent_times(self):
        """Test getting value subsequent times (cached)."""
        def loader_func():
            return {"data": "test", "timestamp": time.time()}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # First call
        result1 = loader.get()
        
        # Second call should return cached value
        result2 = loader.get()
        
        assert result1 == result2
        assert loader._loaded is True

    def test_lazy_section_loader_with_cache_hit(self):
        """Test lazy loading with cache hit."""
        def loader_func():
            return {"data": "from_loader"}
        
        cache = SmartCache()
        cache.set("test_section", {"data": "from_cache"})
        
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        # Should get value from cache, not loader
        result = loader.get()
        
        assert result["data"] == "from_cache"
        assert loader._loaded is True

    def test_lazy_section_loader_with_cache_miss(self):
        """Test lazy loading with cache miss."""
        def loader_func():
            return {"data": "from_loader"}
        
        cache = SmartCache()
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        # Should get value from loader and cache it
        result = loader.get()
        
        assert result["data"] == "from_loader"
        assert loader._loaded is True
        
        # Check that value was cached
        cached_value = cache.get("test_section")
        assert cached_value["data"] == "from_loader"

    def test_lazy_section_loader_with_cache_none_value(self):
        """Test lazy loading with None value (should not cache)."""
        def loader_func():
            return None
        
        cache = SmartCache()
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        result = loader.get()
        
        assert result is None
        assert loader._loaded is True
        
        # None values should not be cached
        assert not cache.has_key("test_section")

    def test_lazy_section_loader_loader_exception(self):
        """Test lazy loading when loader function raises exception."""
        def loader_func():
            raise ValueError("Loader error")
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # Should raise the exception
        with pytest.raises(ValueError, match="Loader error"):
            loader.get()
        
        # Should store the error
        assert loader._load_error is not None
        assert isinstance(loader._load_error, ValueError)
        assert loader._loaded is False

    def test_lazy_section_loader_invalidate(self):
        """Test invalidating loaded section."""
        def loader_func():
            return {"data": "test"}
        
        cache = SmartCache()
        cache.set("test_section", {"data": "cached"})
        
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        # Load the section
        loader.get()
        assert loader._loaded is True
        
        # Invalidate
        loader.invalidate()
        
        assert loader._loaded is False
        assert loader._value is None
        assert loader._load_error is None
        
        # Should be removed from cache
        assert not cache.has_key("test_section")

    def test_lazy_section_loader_invalidate_without_cache(self):
        """Test invalidating without cache."""
        def loader_func():
            return {"data": "test"}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # Load the section
        loader.get()
        assert loader._loaded is True
        
        # Invalidate
        loader.invalidate()
        
        assert loader._loaded is False
        assert loader._value is None
        assert loader._load_error is None

    def test_lazy_section_loader_is_loaded(self):
        """Test checking if section is loaded."""
        def loader_func():
            return {"data": "test"}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # Initially not loaded
        assert loader.is_loaded() is False
        
        # Load the section
        loader.get()
        assert loader.is_loaded() is True
        
        # Invalidate
        loader.invalidate()
        assert loader.is_loaded() is False

    def test_lazy_section_loader_get_load_error(self):
        """Test getting load error."""
        def loader_func():
            raise RuntimeError("Test error")
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # Initially no error
        assert loader.get_load_error() is None
        
        # Try to load (should raise exception)
        with pytest.raises(RuntimeError):
            loader.get()
        
        # Should have stored the error
        error = loader.get_load_error()
        assert error is not None
        assert isinstance(error, RuntimeError)
        assert str(error) == "Test error"

    def test_lazy_section_loader_multiple_loads_same_result(self):
        """Test that multiple loads return the same result."""
        call_count = 0
        
        def loader_func():
            nonlocal call_count
            call_count += 1
            return {"data": "test", "call_count": call_count}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # First load
        result1 = loader.get()
        assert call_count == 1
        
        # Second load should return cached result
        result2 = loader.get()
        assert call_count == 1  # Should not call loader again
        assert result1 == result2

    def test_lazy_section_loader_with_different_section_paths(self):
        """Test multiple loaders with different section paths."""
        def loader1():
            return {"section": "1"}
        
        def loader2():
            return {"section": "2"}
        
        cache = SmartCache()
        
        loader1_obj = LazySectionLoader(loader1, "section1", cache)
        loader2_obj = LazySectionLoader(loader2, "section2", cache)
        
        # Load both sections
        result1 = loader1_obj.get()
        result2 = loader2_obj.get()
        
        assert result1["section"] == "1"
        assert result2["section"] == "2"
        
        # Both should be cached separately
        assert cache.has_key("section1")
        assert cache.has_key("section2")
        assert cache.get("section1")["section"] == "1"
        assert cache.get("section2")["section"] == "2"

    def test_lazy_section_loader_cache_invalidation_after_load(self):
        """Test that cache invalidation works after loading."""
        def loader_func():
            return {"data": "test"}
        
        cache = SmartCache()
        loader = LazySectionLoader(loader_func, "test_section", cache)
        
        # Load the section
        result = loader.get()
        assert result["data"] == "test"
        
        # Manually remove from cache
        cache.delete("test_section")
        
        # Invalidate and reload
        loader.invalidate()
        result2 = loader.get()
        
        # Should call loader function again
        assert result2["data"] == "test"

    def test_lazy_section_loader_with_complex_data(self):
        """Test lazy loading with complex data structures."""
        def loader_func():
            return {
                "users": [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"}
                ],
                "config": {
                    "database": {
                        "host": "localhost",
                        "port": 5432
                    }
                },
                "metadata": {
                    "created_at": time.time(),
                    "version": "1.0.0"
                }
            }
        
        loader = LazySectionLoader(loader_func, "complex_section")
        
        result = loader.get()
        
        assert "users" in result
        assert "config" in result
        assert "metadata" in result
        assert len(result["users"]) == 2
        assert result["config"]["database"]["host"] == "localhost"

    def test_lazy_section_loader_error_handling_different_exceptions(self):
        """Test handling of different exception types."""
        def loader_func():
            raise KeyError("Missing key")
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        with pytest.raises(KeyError):
            loader.get()
        
        error = loader.get_load_error()
        assert isinstance(error, KeyError)
        assert str(error) == "'Missing key'"

    def test_lazy_section_loader_loader_function_side_effects(self):
        """Test that loader function side effects are preserved."""
        side_effect_data = []
        
        def loader_func():
            side_effect_data.append("loaded")
            return {"side_effect": len(side_effect_data)}
        
        loader = LazySectionLoader(loader_func, "test_section")
        
        # First load
        result1 = loader.get()
        assert side_effect_data == ["loaded"]
        assert result1["side_effect"] == 1
        
        # Second load should not call loader again
        result2 = loader.get()
        assert side_effect_data == ["loaded"]  # No change
        assert result2["side_effect"] == 1

    def test_lazy_section_loader_with_empty_result(self):
        """Test lazy loading with empty result."""
        def loader_func():
            return {}
        
        loader = LazySectionLoader(loader_func, "empty_section")
        
        result = loader.get()
        assert result == {}
        assert loader._loaded is True

    def test_lazy_section_loader_with_falsy_values(self):
        """Test lazy loading with falsy values."""
        def loader_func():
            return 0  # Falsy but not None
        
        cache = SmartCache()
        loader = LazySectionLoader(loader_func, "falsy_section", cache)
        
        result = loader.get()
        assert result == 0
        assert loader._loaded is True
        
        # Should be cached (0 is not None)
        assert cache.has_key("falsy_section")
        assert cache.get("falsy_section") == 0
