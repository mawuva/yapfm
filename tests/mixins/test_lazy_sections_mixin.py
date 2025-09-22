"""
Tests for LazySectionsMixin.

This module tests the LazySectionsMixin functionality including lazy loading,
caching, invalidation, and integration with the unified cache system.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from yapfm.cache.smart_cache import SmartCache
from yapfm.mixins.lazy_sections_mixin import LazySectionsMixin
from yapfm.mixins.section_operations_mixin import SectionOperationsMixin


class MockFileManager(LazySectionsMixin, SectionOperationsMixin):
    """Mock file manager for testing LazySectionsMixin."""
    
    def __init__(self, enable_lazy_loading=True, enable_cache=True, cache_size=100, cache_ttl=3600):
        self.enable_lazy_loading = enable_lazy_loading
        self.enable_cache = enable_cache
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.document = {}
        self._loaded = False
        self._dirty = False
        
        # Initialize strategy
        from yapfm.strategies.json_strategy import JsonStrategy
        self.strategy = JsonStrategy()
        
        # Initialize cache
        if enable_cache:
            self.unified_cache = SmartCache(
                max_size=cache_size,
                default_ttl=cache_ttl,
                track_stats=True
            )
        else:
            self.unified_cache = None
        
        # Initialize lazy sections
        self._lazy_sections = {}
        
        # Initialize key cache
        self._key_cache = {}
    
    def get_cache(self):
        """Get the unified cache."""
        if self.enable_cache:
            return self.unified_cache
        return None
    
    def _generate_cache_key(self, dot_key, path, key_name, key_type="key"):
        """Generate a cache key."""
        if dot_key is not None:
            return f"{key_type}:{dot_key}"
        elif path is not None and key_name is not None:
            path_str = ".".join(path) if path else ""
            return f"{key_type}:{path_str}.{key_name}" if path_str else f"{key_type}:{key_name}"
        else:
            raise ValueError("Cannot generate cache key without key parameters")
    
    def is_loaded(self):
        """Mock is_loaded method."""
        return self._loaded
    
    def load(self):
        """Mock load method."""
        self._loaded = True
    
    def save(self):
        """Mock save method."""
        pass

    def mark_as_dirty(self):
        """Mock mark_as_dirty method."""
        self._dirty = True
    
    def delete_key(self, dot_key=None, path=None, key_name=None):
        """Mock delete_key method."""
        if dot_key is not None:
            keys = dot_key.split('.')
            current = self.document
            for key in keys[:-1]:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False
            if isinstance(current, dict) and keys[-1] in current:
                del current[keys[-1]]
                return True
        elif path is not None and key_name is not None:
            current = self.document
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False
            if isinstance(current, dict) and key_name in current:
                del current[key_name]
                return True
        return False

    def resolve_and_navigate(self, dot_key=None, path=None, key_name=None, create=False):
        """Mock resolve_and_navigate method."""
        if dot_key is not None:
            keys = dot_key.split('.')
            if len(keys) == 1:
                # For single key like "database", parent is document root, key is "database"
                if keys[0] in self.document:
                    return (self.document, keys[0])
                elif create:
                    # Create the key if it doesn't exist
                    self.document[keys[0]] = {}
                    return (self.document, keys[0])
                return None
            else:
                # For nested keys like "database.host", navigate to parent
                value = self.document
                for key in keys[:-1]:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    elif create:
                        # Create intermediate dicts if they don't exist
                        if not isinstance(value, dict):
                            return None
                        value[key] = {}
                        value = value[key]
                    else:
                        return None
                if isinstance(value, dict) and keys[-1] in value:
                    return (value, keys[-1])
                elif create and isinstance(value, dict):
                    # Create the key if it doesn't exist
                    value[keys[-1]] = {}
                    return (value, keys[-1])
                return None
        elif path is not None and key_name is not None:
            value = self.document
            for key in path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                elif create:
                    # Create intermediate dicts if they don't exist
                    if not isinstance(value, dict):
                        return None
                    value[key] = {}
                    value = value[key]
                else:
                    return None
            if isinstance(value, dict) and key_name in value:
                return (value, key_name)
            elif create and isinstance(value, dict):
                # Create the key if it doesn't exist
                value[key_name] = {}
                return (value, key_name)
            return None
        return None


class TestLazySectionsMixin:
    """Test cases for LazySectionsMixin class."""

    def test_lazy_sections_mixin_initialization(self):
        """Test LazySectionsMixin initialization."""
        manager = MockFileManager()
        
        assert manager.enable_lazy_loading is True
        assert manager.unified_cache is not None
        assert isinstance(manager._lazy_sections, dict)

    def test_lazy_sections_mixin_without_lazy_loading(self):
        """Test LazySectionsMixin without lazy loading enabled."""
        manager = MockFileManager(enable_lazy_loading=False)
        
        assert manager.enable_lazy_loading is False

    def test_get_section_with_lazy_loading(self):
        """Test get_section with lazy loading enabled."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb"
            }
        }
        
        # First call should create lazy loader
        section = manager.get_section("database", lazy=True)
        assert section == {
            "host": "localhost",
            "port": 5432,
            "name": "testdb"
        }
        
        # Should have created a lazy loader
        assert len(manager._lazy_sections) == 1
        assert "section:database" in manager._lazy_sections

    def test_get_section_without_lazy_loading(self):
        """Test get_section without lazy loading."""
        manager = MockFileManager(enable_lazy_loading=False)
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Should call SectionOperationsMixin directly
        section = manager.get_section("database", lazy=True)
        assert section == {
            "host": "localhost",
            "port": 5432
        }
        
        # Should not create lazy loaders
        assert len(manager._lazy_sections) == 0

    def test_get_section_lazy_false(self):
        """Test get_section with lazy=False."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Should call SectionOperationsMixin directly even if lazy loading is enabled
        section = manager.get_section("database", lazy=False)
        assert section == {
            "host": "localhost",
            "port": 5432
        }
        
        # Should not create lazy loaders
        assert len(manager._lazy_sections) == 0

    def test_get_section_with_path_and_key_name(self):
        """Test get_section with path and key_name parameters."""
        manager = MockFileManager()
        manager.document = {
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432
                }
            }
        }
        
        # Test with path and key_name
        section = manager.get_section(path=["config"], key_name="database", lazy=True)
        assert section == {
            "host": "localhost",
            "port": 5432
        }
        
        # Should create lazy loader with correct key
        assert len(manager._lazy_sections) == 1
        assert "section:config.database" in manager._lazy_sections

    def test_get_section_caching_behavior(self):
        """Test caching behavior of get_section."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Mock SectionOperationsMixin.get_section to track calls
        original_get_section = SectionOperationsMixin.get_section
        call_count = 0
        
        def mock_get_section(self, dot_key=None, path=None, key_name=None, default=None, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_get_section(self, dot_key, path=path, key_name=key_name, default=default, **kwargs)
        
        with patch.object(SectionOperationsMixin, 'get_section', side_effect=mock_get_section):
            # First call should call SectionOperationsMixin.get_section
            section1 = manager.get_section("database", lazy=True)
            assert section1 == {"host": "localhost", "port": 5432}
            assert call_count == 1
            
            # Second call should use lazy loader, not call SectionOperationsMixin.get_section
            section2 = manager.get_section("database", lazy=True)
            assert section2 == {"host": "localhost", "port": 5432}
            assert call_count == 1  # Should not increase

    def test_set_section_with_lazy_cache_update(self):
        """Test set_section with lazy cache update."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # First load the section to create lazy loader
        manager.get_section("database", lazy=True)
        assert len(manager._lazy_sections) == 1
        
        # Update the section
        new_data = {"host": "newhost", "port": 3306, "name": "newdb"}
        manager.set_section(new_data, "database", update_lazy_cache=True)
        
        # Verify document was updated
        assert manager.document["database"] == new_data
        
        # Lazy loader should be invalidated
        lazy_loader = manager._lazy_sections.get("section:database")
        assert lazy_loader is not None
        assert not lazy_loader.is_loaded()  # Should be invalidated

    def test_set_section_without_lazy_cache_update(self):
        """Test set_section without lazy cache update."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # First load the section to create lazy loader
        manager.get_section("database", lazy=True)
        lazy_loader = manager._lazy_sections["section:database"]
        assert lazy_loader.is_loaded()
        
        # Update the section without cache update
        new_data = {"host": "newhost", "port": 3306}
        manager.set_section(new_data, "database", update_lazy_cache=False)
        
        # Lazy loader should still be loaded (not invalidated)
        assert lazy_loader.is_loaded()

    def test_delete_section_with_lazy_cache_invalidation(self):
        """Test delete_section with lazy cache invalidation."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # First load the section to create lazy loader
        manager.get_section("database", lazy=True)
        assert len(manager._lazy_sections) == 1
        
        # Delete the section
        result = manager.delete_section("database")
        assert result is True
        
        # Verify section was deleted from document
        assert "database" not in manager.document
        
        # Lazy loader should be invalidated
        lazy_loader = manager._lazy_sections.get("section:database")
        assert lazy_loader is not None
        assert not lazy_loader.is_loaded()  # Should be invalidated

    def test_delete_section_nonexistent(self):
        """Test delete_section with nonexistent section."""
        manager = MockFileManager()
        manager.document = {}
        
        # Try to delete nonexistent section
        result = manager.delete_section("nonexistent")
        assert result is False
        
        # Should not create lazy loaders
        assert len(manager._lazy_sections) == 0

    def test_get_section_lazy_with_default(self):
        """Test _get_section_lazy with default value."""
        manager = MockFileManager()
        manager.document = {}
        
        # Test with default value
        section = manager._get_section_lazy("nonexistent", default={"default": "value"})
        assert section == {"default": "value"}
        
        # Should create lazy loader
        assert len(manager._lazy_sections) == 1

    def test_invalidate_lazy_section(self):
        """Test _invalidate_lazy_section method."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Load section to create lazy loader
        manager.get_section("database", lazy=True)
        lazy_loader = manager._lazy_sections["section:database"]
        assert lazy_loader.is_loaded()
        
        # Invalidate the section
        manager._invalidate_lazy_section("database")
        
        # Lazy loader should be invalidated
        assert not lazy_loader.is_loaded()

    def test_invalidate_lazy_section_nonexistent(self):
        """Test _invalidate_lazy_section with nonexistent section."""
        manager = MockFileManager()
        
        # Should not raise error
        manager._invalidate_lazy_section("nonexistent")

    def test_clear_lazy_cache(self):
        """Test clear_lazy_cache method."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "app": {
                "name": "testapp",
                "version": "1.0.0"
            }
        }
        
        # Load multiple sections
        manager.get_section("database", lazy=True)
        manager.get_section("app", lazy=True)
        
        # Verify lazy loaders exist
        assert len(manager._lazy_sections) == 2
        
        # Clear lazy cache
        manager.clear_lazy_cache()
        
        # All lazy loaders should be cleared
        assert len(manager._lazy_sections) == 0

    def test_get_lazy_stats(self):
        """Test get_lazy_stats method."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "app": {
                "name": "testapp",
                "version": "1.0.0"
            }
        }
        
        # Initially no sections loaded
        stats = manager.get_lazy_stats()
        assert stats["loaded_sections"] == 0
        assert stats["total_sections"] == 0
        
        # Load one section
        manager.get_section("database", lazy=True)
        stats = manager.get_lazy_stats()
        assert stats["loaded_sections"] == 1
        assert stats["total_sections"] == 1
        
        # Load another section
        manager.get_section("app", lazy=True)
        stats = manager.get_lazy_stats()
        assert stats["loaded_sections"] == 2
        assert stats["total_sections"] == 2
        
        # Invalidate one section
        manager._invalidate_lazy_section("database")
        stats = manager.get_lazy_stats()
        assert stats["loaded_sections"] == 1  # Only app section still loaded
        assert stats["total_sections"] == 2  # Total sections unchanged

    def test_lazy_loading_with_complex_data(self):
        """Test lazy loading with complex data structures."""
        manager = MockFileManager()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ],
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {
                        "username": "admin",
                        "password": "secret"
                    }
                },
                "cache": {
                    "enabled": True,
                    "ttl": 3600
                }
            }
        }
        manager.document = complex_data
        
        # Load users section
        users = manager.get_section("users", lazy=True)
        assert users == complex_data["users"]
        
        # Load config section
        config = manager.get_section("config", lazy=True)
        assert config == complex_data["config"]
        
        # Verify both sections are cached
        assert len(manager._lazy_sections) == 2
        assert "section:users" in manager._lazy_sections
        assert "section:config" in manager._lazy_sections

    def test_lazy_loading_performance(self):
        """Test lazy loading performance characteristics."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Mock SectionOperationsMixin.get_section to track calls
        call_count = 0
        
        def mock_get_section(self, dot_key=None, path=None, key_name=None, default=None):
            nonlocal call_count
            call_count += 1
            # Simulate some processing time
            time.sleep(0.01)
            return manager.document.get(dot_key, default)
        
        with patch.object(SectionOperationsMixin, 'get_section', side_effect=mock_get_section):
            # First call should call the mock
            start_time = time.time()
            section1 = manager.get_section("database", lazy=True)
            first_call_time = time.time() - start_time
            assert call_count == 1
            
            # Second call should use lazy loader (faster)
            start_time = time.time()
            section2 = manager.get_section("database", lazy=True)
            second_call_time = time.time() - start_time
            assert call_count == 1  # Should not call mock again
            
            # Both should return same data
            assert section1 == section2
            
            # Second call should be faster (no mock call)
            assert second_call_time < first_call_time

    def test_lazy_loading_with_cache_integration(self):
        """Test lazy loading integration with unified cache."""
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Load section with lazy loading
        section = manager.get_section("database", lazy=True)
        assert section == {"host": "localhost", "port": 5432}
        
        # Verify it's also in the unified cache
        assert manager.unified_cache.has_key("section:database")
        cached_section = manager.unified_cache.get("section:database")
        assert cached_section == {"host": "localhost", "port": 5432}

    def test_lazy_loading_error_handling(self):
        """Test lazy loading error handling."""
        manager = MockFileManager()
        
        # Mock SectionOperationsMixin.get_section to raise error
        def mock_get_section(self, dot_key=None, path=None, key_name=None, default=None):
            raise ValueError("Test error")
        
        with patch.object(SectionOperationsMixin, 'get_section', side_effect=mock_get_section):
            # Should propagate the error
            with pytest.raises(ValueError, match="Test error"):
                manager.get_section("database", lazy=True)

    def test_lazy_loading_thread_safety(self):
        """Test lazy loading thread safety."""
        import threading
        
        manager = MockFileManager()
        manager.document = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        results = []
        
        def worker():
            for i in range(5):
                section = manager.get_section("database", lazy=True)
                results.append(section)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All results should be the same
        expected = {"host": "localhost", "port": 5432}
        assert all(result == expected for result in results)
        assert len(results) == 15  # 3 threads * 5 calls each

    def test_lazy_loading_with_empty_sections(self):
        """Test lazy loading with empty sections."""
        manager = MockFileManager()
        manager.document = {
            "empty_section": {},
            "none_section": None
        }
        
        # Test with empty dict
        empty_section = manager.get_section("empty_section", lazy=True)
        assert empty_section == {}
        
        # Test with None
        none_section = manager.get_section("none_section", lazy=True)
        assert none_section is None
        
        # Both should create lazy loaders
        assert len(manager._lazy_sections) == 2

    def test_lazy_loading_with_default_values(self):
        """Test lazy loading with default values."""
        manager = MockFileManager()
        manager.document = {}
        
        # Test with default value
        section = manager.get_section("nonexistent", default={"default": "value"}, lazy=True)
        assert section == {"default": "value"}
        
        # Should create lazy loader
        assert len(manager._lazy_sections) == 1
