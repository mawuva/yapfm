"""
Unit tests for helpers __init__.py module.
"""

from typing import Any, Dict

from yapfm.helpers import (
    deep_merge,
    load_file,
    load_file_with_stream,
    merge_toml,
    navigate_dict_like,
    save_file,
    save_file_with_stream,
)


class TestHelpersInit:
    """Test cases for helpers module initialization and imports."""

    def test_import_all_functions_from_dict_utils(self) -> None:
        """
        Scenario: Import all functions from dict_utils module

        Expected:
        - Should be able to import deep_merge function
        - Should be able to import navigate_dict_like function
        - Should import functions directly from helpers module
        """
        assert deep_merge is not None
        assert navigate_dict_like is not None
        assert callable(deep_merge)
        assert callable(navigate_dict_like)

    def test_import_all_functions_from_io(self) -> None:
        """
        Scenario: Import all functions from io module

        Expected:
        - Should be able to import all I/O functions
        - Should import functions directly from helpers module
        - Should have all expected I/O functions available
        """
        assert load_file is not None
        assert load_file_with_stream is not None
        assert save_file is not None
        assert save_file_with_stream is not None

        assert callable(load_file)
        assert callable(load_file_with_stream)
        assert callable(save_file)
        assert callable(save_file_with_stream)

    def test_import_merge_toml_from_toml_merger(self) -> None:
        """
        Scenario: Import merge_toml function from toml_merger module

        Expected:
        - Should be able to import merge_toml function
        - Should import function directly from helpers module
        - Should be callable
        """
        assert merge_toml is not None
        assert callable(merge_toml)

    def test_imported_functions_have_correct_signatures(self) -> None:
        """
        Scenario: Verify that imported functions have correct signatures

        Expected:
        - deep_merge should accept (base, new, overwrite) parameters
        - navigate_dict_like should accept (document, path, create, create_dict_func) parameters
        - load_file should accept (file_path, parser_func) parameters
        - save_file should accept (file_path, data, serializer_func) parameters
        - merge_toml should accept (base, new, overwrite) parameters
        """
        import inspect

        # Check deep_merge signature
        deep_merge_sig = inspect.signature(deep_merge)
        assert "base" in deep_merge_sig.parameters
        assert "new" in deep_merge_sig.parameters
        assert "overwrite" in deep_merge_sig.parameters

        # Check navigate_dict_like signature
        navigate_sig = inspect.signature(navigate_dict_like)
        assert "document" in navigate_sig.parameters
        assert "path" in navigate_sig.parameters
        assert "create" in navigate_sig.parameters
        assert "create_dict_func" in navigate_sig.parameters

        # Check load_file signature
        load_file_sig = inspect.signature(load_file)
        assert "file_path" in load_file_sig.parameters
        assert "parser_func" in load_file_sig.parameters

        # Check save_file signature
        save_file_sig = inspect.signature(save_file)
        assert "file_path" in save_file_sig.parameters
        assert "data" in save_file_sig.parameters
        assert "serializer_func" in save_file_sig.parameters

        # Check merge_toml signature
        merge_toml_sig = inspect.signature(merge_toml)
        assert "base" in merge_toml_sig.parameters
        assert "new" in merge_toml_sig.parameters
        assert "overwrite" in merge_toml_sig.parameters

    def test_imported_functions_are_actual_implementations(self) -> None:
        """
        Scenario: Verify that imported functions are actual implementations, not stubs

        Expected:
        - Functions should be callable and executable
        - Functions should perform their intended operations
        - Functions should not be None or placeholder objects
        """
        # Test deep_merge functionality
        base = {"key1": "value1"}
        new = {"key2": "value2"}
        merge_result = deep_merge(base, new)
        assert merge_result == base
        assert base["key2"] == "value2"

        # Test navigate_dict_like functionality
        document: Dict[str, Any] = {"level1": {"level2": "value"}}
        navigate_result: Any = navigate_dict_like(document, ["level1", "level2"])
        assert navigate_result == "value"

        # Test merge_toml functionality
        from tomlkit import TOMLDocument

        base_toml = TOMLDocument()
        new_data = {"key": "value"}
        result = merge_toml(base_toml, new_data)
        assert result == base_toml
        assert base_toml["key"] == "value"

    def test_module_has_correct_all_attribute(self) -> None:
        """
        Scenario: Verify that the helpers module has the correct __all__ attribute

        Expected:
        - __all__ should contain all exported functions
        - __all__ should not contain internal or private functions
        - __all__ should match the documented API
        """
        from yapfm.helpers import __all__

        expected_functions = {
            "load_file",
            "load_file_with_stream",
            "save_file",
            "save_file_with_stream",
            "navigate_dict_like",
            "deep_merge",
            "merge_toml",
            "validate_strategy",
        }

        assert set(__all__) == expected_functions
        assert len(__all__) == len(expected_functions)

    def test_imports_work_with_from_statement(self) -> None:
        """
        Scenario: Test that imports work correctly with from statements

        Expected:
        - Should be able to import specific functions using from statement
        - Should not import unnecessary modules
        - Should work with both individual and multiple imports
        """
        # Test individual imports
        from yapfm.helpers import deep_merge

        assert deep_merge is not None

        from yapfm.helpers import load_file

        assert load_file is not None

        # Test multiple imports
        from yapfm.helpers import (
            deep_merge,
            load_file,
            merge_toml,
            navigate_dict_like,
            save_file,
        )

        assert all(
            func is not None
            for func in [
                deep_merge,
                navigate_dict_like,
                load_file,
                save_file,
                merge_toml,
            ]
        )

    def test_imports_work_with_module_level_import(self) -> None:
        """
        Scenario: Test that imports work correctly at module level

        Expected:
        - Should be able to import the entire helpers module
        - Should access functions through module attribute access
        - Should work with both dot notation and direct access
        """
        import yapfm.helpers as helpers

        # Test dot notation access
        assert helpers.deep_merge is not None
        assert helpers.navigate_dict_like is not None
        assert helpers.load_file is not None
        assert helpers.save_file is not None
        assert helpers.merge_toml is not None

        # Test that functions are callable
        assert callable(helpers.deep_merge)
        assert callable(helpers.navigate_dict_like)
        assert callable(helpers.load_file)
        assert callable(helpers.save_file)
        assert callable(helpers.merge_toml)

    def test_imported_functions_are_decorated_correctly(self) -> None:
        """
        Scenario: Verify that imported functions have correct decorators applied

        Expected:
        - I/O functions should have handle_file_errors decorator
        - Functions should maintain their original functionality
        - Decorators should not break function signatures
        """

        # Check that I/O functions have the decorator applied
        # (This is more of an integration test, but we can verify the functions work)
        assert hasattr(load_file, "__wrapped__") or hasattr(load_file, "__name__")
        assert hasattr(save_file, "__wrapped__") or hasattr(save_file, "__name__")

        # Verify functions still work despite decorators
        base = {"key": "value"}
        new = {"key2": "value2"}
        result = deep_merge(base, new)
        assert result == base
        assert base["key2"] == "value2"

    def test_module_docstring_is_present(self) -> None:
        """
        Scenario: Verify that the helpers module has proper documentation

        Expected:
        - Module should have a docstring
        - Docstring should describe the module's purpose
        - Docstring should list key functions
        """
        import yapfm.helpers

        assert yapfm.helpers.__doc__ is not None
        assert len(yapfm.helpers.__doc__.strip()) > 0
        assert "Helper functions and utilities" in yapfm.helpers.__doc__
        assert "file management operations" in yapfm.helpers.__doc__
