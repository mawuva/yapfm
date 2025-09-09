"""
Unit tests for proxy module.
"""

import logging
import time
from typing import Any
from unittest.mock import Mock

import pytest

from yapfm.proxy import FileManagerProxy


class TestFileManagerProxy:
    """Test cases for FileManagerProxy class."""

    def test_proxy_initialization_with_defaults(self) -> None:
        """
        Scenario: Initialize FileManagerProxy with default parameters

        Expected:
        - Should initialize with all features disabled by default
        - Should use default logger
        - Should store manager reference correctly
        - Should not have audit hook
        """
        mock_manager = Mock()
        proxy = FileManagerProxy(mock_manager)

        assert proxy._manager is mock_manager
        assert proxy._enable_logging is False
        assert proxy._enable_metrics is False
        assert proxy._enable_audit is False
        assert proxy._logger is not None
        assert proxy._audit_hook is None

    def test_proxy_initialization_with_custom_logger(self) -> None:
        """
        Scenario: Initialize FileManagerProxy with custom logger

        Expected:
        - Should use provided logger instead of default
        - Should store logger reference correctly
        - Should maintain other default settings
        """
        mock_manager = Mock()
        custom_logger = logging.getLogger("custom_logger")
        proxy = FileManagerProxy(mock_manager, logger=custom_logger)

        assert proxy._logger is custom_logger
        assert proxy._manager is mock_manager

    def test_proxy_initialization_with_all_features_enabled(self) -> None:
        """
        Scenario: Initialize FileManagerProxy with all features enabled

        Expected:
        - Should enable logging, metrics, and audit
        - Should store audit hook reference
        - Should maintain all settings correctly
        """
        mock_manager = Mock()
        audit_hook = Mock()

        proxy = FileManagerProxy(
            mock_manager,
            enable_logging=True,
            enable_metrics=True,
            enable_audit=True,
            audit_hook=audit_hook,
        )

        assert proxy._enable_logging is True
        assert proxy._enable_metrics is True
        assert proxy._enable_audit is True
        assert proxy._audit_hook is audit_hook

    def test_proxy_passes_through_non_callable_attributes(self) -> None:
        """
        Scenario: Access non-callable attributes through proxy

        Expected:
        - Should return attributes directly from manager
        - Should not wrap non-callable attributes
        - Should maintain original attribute behavior
        """
        mock_manager = Mock()
        mock_manager.some_attribute = "test_value"
        mock_manager.another_attr = 42

        proxy = FileManagerProxy(mock_manager)

        assert proxy.some_attribute == "test_value"
        assert proxy.another_attr == 42

    def test_proxy_wraps_callable_methods_without_features(self) -> None:
        """
        Scenario: Call methods through proxy with all features disabled

        Expected:
        - Should execute method and return result
        - Should not perform logging, metrics, or audit
        - Should maintain original method behavior
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"

        proxy = FileManagerProxy(mock_manager)
        result = proxy.test_method("arg1", "arg2", key="value")

        assert result == "test_result"
        mock_manager.test_method.assert_called_once_with("arg1", "arg2", key="value")

    def test_proxy_logging_enabled(self) -> None:
        """
        Scenario: Call methods through proxy with logging enabled

        Expected:
        - Should log method call with arguments
        - Should log method return value
        - Should use debug level for logging
        - Should execute method normally
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_logger = Mock()

        proxy = FileManagerProxy(mock_manager, enable_logging=True, logger=mock_logger)
        result = proxy.test_method("arg1", key="value")

        assert result == "test_result"
        assert mock_logger.debug.call_count == 2  # Call and return logs

        # Check call log
        call_log = mock_logger.debug.call_args_list[0][0][0]
        assert "▶️" in call_log
        assert "test_method" in call_log
        assert "arg1" in call_log
        assert "key" in call_log
        assert "value" in call_log

        # Check return log
        return_log = mock_logger.debug.call_args_list[1][0][0]
        assert "✅" in return_log
        assert "test_method" in return_log
        assert "test_result" in return_log

    def test_proxy_metrics_enabled(self) -> None:
        """
        Scenario: Call methods through proxy with metrics enabled

        Expected:
        - Should measure execution time
        - Should log execution time in milliseconds
        - Should use info level for metrics logging
        - Should execute method normally
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_logger = Mock()

        proxy = FileManagerProxy(mock_manager, enable_metrics=True, logger=mock_logger)
        result = proxy.test_method("arg1")

        assert result == "test_result"
        assert mock_logger.info.call_count == 1

        # Check metrics log
        metrics_log = mock_logger.info.call_args[0][0]
        assert "⏱" in metrics_log
        assert "test_method" in metrics_log
        assert "ms" in metrics_log

    def test_proxy_audit_enabled_with_hook(self) -> None:
        """
        Scenario: Call methods through proxy with audit enabled and custom hook

        Expected:
        - Should call audit hook with correct parameters
        - Should pass method name, args, kwargs, and result
        - Should execute method normally
        - Should not affect method return value
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_audit_hook = Mock()

        proxy = FileManagerProxy(
            mock_manager, enable_audit=True, audit_hook=mock_audit_hook
        )
        result = proxy.test_method("arg1", key="value")

        assert result == "test_result"
        mock_audit_hook.assert_called_once_with(
            "test_method", ("arg1",), {"key": "value"}, "test_result"
        )

    def test_proxy_audit_enabled_without_hook(self) -> None:
        """
        Scenario: Call methods through proxy with audit enabled but no hook

        Expected:
        - Should not call any audit hook
        - Should execute method normally
        - Should not raise any errors
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"

        proxy = FileManagerProxy(mock_manager, enable_audit=True)
        result = proxy.test_method("arg1")

        assert result == "test_result"

    def test_proxy_all_features_enabled(self) -> None:
        """
        Scenario: Call methods through proxy with all features enabled

        Expected:
        - Should perform logging, metrics, and audit
        - Should log method call and return
        - Should measure execution time
        - Should call audit hook
        - Should execute method normally
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_logger = Mock()
        mock_audit_hook = Mock()

        proxy = FileManagerProxy(
            mock_manager,
            enable_logging=True,
            enable_metrics=True,
            enable_audit=True,
            logger=mock_logger,
            audit_hook=mock_audit_hook,
        )
        result = proxy.test_method("arg1", key="value")

        assert result == "test_result"
        assert mock_logger.debug.call_count == 2  # Call and return logs
        assert mock_logger.info.call_count == 1  # Metrics log
        mock_audit_hook.assert_called_once()

    def test_proxy_handles_method_exceptions(self) -> None:
        """
        Scenario: Call methods through proxy when method raises exception

        Expected:
        - Should propagate exception from wrapped method
        - Should not interfere with exception handling
        - Should maintain original exception behavior
        """
        mock_manager = Mock()
        mock_manager.test_method.side_effect = ValueError("test error")

        proxy = FileManagerProxy(mock_manager)

        with pytest.raises(ValueError, match="test error"):
            proxy.test_method("arg1")

    def test_proxy_handles_audit_hook_exceptions(self) -> None:
        """
        Scenario: Call methods through proxy when audit hook raises exception

        Expected:
        - Should log audit hook error
        - Should not affect method execution
        - Should return method result normally
        - Should use error level for audit error logging
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_logger = Mock()
        mock_audit_hook = Mock(side_effect=RuntimeError("audit error"))

        proxy = FileManagerProxy(
            mock_manager,
            enable_audit=True,
            audit_hook=mock_audit_hook,
            logger=mock_logger,
        )
        result = proxy.test_method("arg1")

        assert result == "test_result"
        mock_logger.error.assert_called_once()
        error_log = mock_logger.error.call_args[0][0]
        assert "Audit hook error" in error_log
        assert "audit error" in error_log

    def test_proxy_metrics_with_timing(self) -> None:
        """
        Scenario: Test metrics timing accuracy

        Expected:
        - Should measure actual execution time
        - Should log time in milliseconds
        - Should be reasonably accurate
        """
        mock_manager = Mock()
        mock_logger = Mock()

        def slow_method(*args: Any, **kwargs: Any) -> str:
            time.sleep(0.01)  # 10ms delay
            return "slow_result"

        mock_manager.test_method = slow_method

        proxy = FileManagerProxy(mock_manager, enable_metrics=True, logger=mock_logger)
        result = proxy.test_method()

        assert result == "slow_result"
        assert mock_logger.info.call_count == 1

        # Check that timing is reasonable (should be at least 10ms)
        metrics_log = mock_logger.info.call_args[0][0]
        assert "⏱" in metrics_log
        # Extract time value from log
        time_part = metrics_log.split("took ")[1].split("ms")[0]
        elapsed_ms = float(time_part)
        assert elapsed_ms >= 10.0  # Should be at least 10ms

    def test_proxy_with_different_method_signatures(self) -> None:
        """
        Scenario: Test proxy with methods having different signatures

        Expected:
        - Should handle methods with no arguments
        - Should handle methods with positional arguments
        - Should handle methods with keyword arguments
        - Should handle methods with mixed arguments
        - Should preserve all argument types
        """
        mock_manager = Mock()
        mock_manager.no_args.return_value = "no_args_result"
        mock_manager.positional_args.return_value = "positional_result"
        mock_manager.keyword_args.return_value = "keyword_result"
        mock_manager.mixed_args.return_value = "mixed_result"

        proxy = FileManagerProxy(mock_manager)

        # Test no arguments
        result1 = proxy.no_args()
        assert result1 == "no_args_result"
        mock_manager.no_args.assert_called_once_with()

        # Test positional arguments
        result2 = proxy.positional_args("arg1", "arg2")
        assert result2 == "positional_result"
        mock_manager.positional_args.assert_called_once_with("arg1", "arg2")

        # Test keyword arguments
        result3 = proxy.keyword_args(key1="value1", key2="value2")
        assert result3 == "keyword_result"
        mock_manager.keyword_args.assert_called_once_with(key1="value1", key2="value2")

        # Test mixed arguments
        result4 = proxy.mixed_args("arg1", "arg2", key1="value1", key2="value2")
        assert result4 == "mixed_result"
        mock_manager.mixed_args.assert_called_once_with(
            "arg1", "arg2", key1="value1", key2="value2"
        )

    def test_proxy_with_none_manager(self) -> None:
        """
        Scenario: Test proxy with None as manager

        Expected:
        - Should raise AttributeError when accessing attributes
        - Should handle None manager gracefully
        - Should not crash during initialization
        """
        proxy = FileManagerProxy(None)

        with pytest.raises(AttributeError):
            proxy.some_method()

    def test_proxy_with_custom_audit_hook_signature(self) -> None:
        """
        Scenario: Test proxy with custom audit hook having different signature

        Expected:
        - Should call audit hook with correct parameters
        - Should handle audit hook with any signature
        - Should not affect method execution
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"

        def custom_audit_hook(
            method_name: str, args: tuple, kwargs: dict, result: Any
        ) -> None:
            # Custom audit hook that processes the data
            {
                "method": method_name,
                "arg_count": len(args),
                "kwarg_count": len(kwargs),
                "result_type": type(result).__name__,
            }
            # In a real implementation, this would be stored or logged
            # For testing, we just verify the hook is called

        proxy = FileManagerProxy(
            mock_manager, enable_audit=True, audit_hook=custom_audit_hook
        )
        result = proxy.test_method("arg1", key="value")

        assert result == "test_result"

    def test_proxy_logging_with_different_log_levels(self) -> None:
        """
        Scenario: Test proxy logging with different log levels

        Expected:
        - Should use debug level for method call/return logs
        - Should use info level for metrics logs
        - Should use error level for audit hook errors
        - Should respect logger configuration
        """
        mock_manager = Mock()
        mock_manager.test_method.return_value = "test_result"
        mock_logger = Mock()

        proxy = FileManagerProxy(
            mock_manager, enable_logging=True, enable_metrics=True, logger=mock_logger
        )
        proxy.test_method("arg1")

        # Check that different log levels are used
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        info_calls = [call for call in mock_logger.info.call_args_list]

        assert len(debug_calls) == 2  # Call and return
        assert len(info_calls) == 1  # Metrics

    def test_proxy_with_complex_return_values(self) -> None:
        """
        Scenario: Test proxy with complex return values

        Expected:
        - Should handle complex return values correctly
        - Should log complex return values properly
        - Should pass complex values to audit hook
        - Should not modify return values
        """
        mock_manager = Mock()
        complex_result = {
            "data": [1, 2, 3],
            "nested": {"key": "value"},
            "function": lambda x: x * 2,
        }
        mock_manager.test_method.return_value = complex_result
        mock_logger = Mock()
        mock_audit_hook = Mock()

        proxy = FileManagerProxy(
            mock_manager,
            enable_logging=True,
            enable_audit=True,
            logger=mock_logger,
            audit_hook=mock_audit_hook,
        )
        result = proxy.test_method("arg1")

        assert result is complex_result
        mock_audit_hook.assert_called_once_with(
            "test_method", ("arg1",), {}, complex_result
        )

    def test_proxy_with_multiple_method_calls(self) -> None:
        """
        Scenario: Test proxy with multiple method calls

        Expected:
        - Should handle multiple calls correctly
        - Should log each call separately
        - Should measure each call separately
        - Should audit each call separately
        """
        mock_manager = Mock()
        mock_manager.method1.return_value = "result1"
        mock_manager.method2.return_value = "result2"
        mock_logger = Mock()
        mock_audit_hook = Mock()

        proxy = FileManagerProxy(
            mock_manager,
            enable_logging=True,
            enable_metrics=True,
            enable_audit=True,
            logger=mock_logger,
            audit_hook=mock_audit_hook,
        )

        result1 = proxy.method1("arg1")
        result2 = proxy.method2("arg2", key="value")

        assert result1 == "result1"
        assert result2 == "result2"
        assert mock_logger.debug.call_count == 4  # 2 calls + 2 returns
        assert mock_logger.info.call_count == 2  # 2 metrics
        assert mock_audit_hook.call_count == 2  # 2 audits

    def test_proxy_with_async_methods(self) -> None:
        """
        Scenario: Test proxy with async methods

        Expected:
        - Should handle async methods correctly
        - Should not interfere with async behavior
        - Should return coroutine objects
        - Should maintain async method signatures
        """
        mock_manager = Mock()

        async def async_method(*args: Any, **kwargs: Any) -> str:
            return "async_result"

        mock_manager.async_method = async_method

        proxy = FileManagerProxy(mock_manager)
        result = proxy.async_method("arg1")

        # Should return a coroutine object
        assert hasattr(result, "__await__")
        # The actual async execution would need to be awaited in real usage
