import logging
import time
from typing import Any, Callable, Optional


class FileManagerProxy:
    """
    Proxy for a FileManager with optional logging, metrics, and auditing.

    This proxy intercepts calls to the FileManager methods and can:
      - Log method calls and results (`enable_logging=True`)
      - Measure execution time of methods (`enable_metrics=True`)
      - Run a custom audit hook on each method call (`enable_audit=True`)

    Args:
        manager (Any): The underlying FileManager instance to proxy.
        enable_logging (bool, optional): Enable debug logging of method calls and results. Default: False.
        enable_metrics (bool, optional): Enable execution time measurement. Default: False.
        enable_audit (bool, optional): Enable audit hook execution. Default: False.
        logger (logging.Logger, optional): Custom logger. Defaults to `logging.getLogger(__name__)`.
        audit_hook (Callable, optional): Custom hook called as
            `audit_hook(method: str, args: tuple, kwargs: dict, result: Any)`.

    Returns:
        FileManagerProxy: The proxy instance.

    Example:
        >>> def my_audit(method, args, kwargs, result):
        ...     print(f"🔍 AUDIT: {method} called with {args}, {kwargs} => {result}")

        >>> fm = FileManager("config.toml")
        >>> fm_proxy = FileManagerProxy(
        ...     fm,
        ...     enable_logging=True,
        ...     enable_metrics=True,
        ...     enable_audit=True,
        ...     audit_hook=my_audit,
        ... )
        >>> fm_proxy.load()
        >>> fm_proxy.set_key("db.host", "127.0.0.1")
        >>> fm_proxy.save()
    """

    def __init__(
        self,
        manager: Any,
        *,
        enable_logging: bool = False,
        enable_metrics: bool = False,
        enable_audit: bool = False,
        logger: Optional[logging.Logger] = None,
        audit_hook: Optional[Callable[[str, tuple, dict, Any], None]] = None,
    ):
        self._manager = manager
        self._enable_logging = enable_logging
        self._enable_metrics = enable_metrics
        self._enable_audit = enable_audit
        self._logger = logger or logging.getLogger(__name__)
        self._audit_hook = audit_hook

    def __getattr__(self, item: str) -> Any:
        attr = getattr(self._manager, item)

        if callable(attr):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter() if self._enable_metrics else None

                if self._enable_logging:
                    self._logger.debug(
                        f"▶️ {self._manager.__class__.__name__}.{item} called "
                        f"with args={args}, kwargs={kwargs}"
                    )

                result = attr(*args, **kwargs)

                if self._enable_logging:
                    self._logger.debug(
                        f"✅ {self._manager.__class__.__name__}.{item} returned {result!r}"
                    )

                if self._enable_metrics and start_time is not None:
                    elapsed = (time.perf_counter() - start_time) * 1000
                    self._logger.info(
                        f"⏱ {self._manager.__class__.__name__}.{item} took {elapsed:.2f}ms"
                    )

                if self._enable_audit and self._audit_hook:
                    try:
                        self._audit_hook(item, args, kwargs, result)
                    except Exception as e:
                        self._logger.error(f"Audit hook error: {e}")

                return result

            return wrapper
        return attr
