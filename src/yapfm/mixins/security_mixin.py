"""
Security Mixin

This module provides security functionality for the FileManager.
The SecurityMixin contains operations for freezing, unfreezing, and masking sensitive data.
"""

# mypy: ignore-errors

from typing import Any, Dict, List, Optional, Set


class SecurityMixin:
    """
    Mixin for security operations.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._frozen = False

    def freeze(self) -> None:
        """
        Make the file read-only by preventing modifications.

        Example:
            >>> fm.freeze()
            >>> fm.set("new.key", "value")  # Raises PermissionError
        """
        self._frozen = True

    def unfreeze(self) -> None:
        """
        Re-enable write operations on the file.

        Example:
            >>> fm.unfreeze()
            >>> fm.set("new.key", "value")  # Now works
        """
        self._frozen = False

    def is_frozen(self) -> bool:
        """
        Check if the file is frozen (read-only).

        Returns:
            True if frozen, False otherwise

        Example:
            >>> if fm.is_frozen():
            ...     print("File is read-only")
        """
        return self._frozen

    def check_frozen(self) -> None:
        """Check if file is frozen and raise error if so."""
        if self._frozen:
            raise PermissionError(
                "File is frozen (read-only). Call unfreeze() to enable modifications."
            )

    def _get_default_sensitive_keys(self) -> Set[str]:
        """Get the default set of sensitive key patterns."""
        return {
            "password",
            "passwd",
            "pwd",
            "secret",
            "key",
            "token",
            "auth",
            "credential",
            "private",
            "sensitive",
            "confidential",
            "api_key",
            "access_token",
            "refresh_token",
            "session_id",
            "cookie",
        }

    def _is_sensitive_key(self, key: str, sensitive_keys: Set[str]) -> bool:
        """Check if a key is considered sensitive."""
        key_lower = key.lower()
        return any(sensitive_key in key_lower for sensitive_key in sensitive_keys)

    def _process_sensitive_data(
        self, data: Any, sensitive_keys: Set[str], action: str, mask: str = "***"
    ) -> Any:
        """
        Process data to handle sensitive information.

        Args:
            data: Data to process
            sensitive_keys: Set of sensitive key patterns
            action: Either 'mask' or 'remove'
            mask: String to use for masking (only used when action='mask')
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                is_sensitive = self._is_sensitive_key(key, sensitive_keys)

                if is_sensitive:
                    if action == "mask":
                        result[key] = mask
                    # If action == 'remove', we simply don't add the key to result
                else:
                    if isinstance(value, (dict, list)):
                        result[key] = self._process_sensitive_data(
                            value, sensitive_keys, action, mask
                        )
                    else:
                        result[key] = value
            return result
        elif isinstance(data, list):
            return [
                self._process_sensitive_data(item, sensitive_keys, action, mask)
                for item in data
            ]
        else:
            return data

    def mask_sensitive(
        self, keys_to_mask: Optional[List[str]] = None, mask: str = "***"
    ) -> Dict[str, Any]:
        """
        Create a masked version of the data with sensitive information hidden.

        Args:
            keys_to_mask: List of keys to mask. If None, uses default sensitive keys
            mask: String to use for masking

        Returns:
            Dictionary with sensitive data masked

        Example:
            >>> masked = fm.mask_sensitive()
            >>> masked = fm.mask_sensitive(["password", "secret"], "HIDDEN")
        """
        if keys_to_mask is None:
            sensitive_keys = self._get_default_sensitive_keys()
        else:
            sensitive_keys = set(keys_to_mask)

        self.load_if_not_loaded()

        return self._process_sensitive_data(self.document, sensitive_keys, "mask", mask)

    def get_public_config(
        self, sensitive_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get a public version of the configuration with sensitive data removed.

        Args:
            sensitive_keys: List of keys to remove. If None, uses default sensitive keys

        Returns:
            Dictionary with sensitive data removed

        Example:
            >>> public = fm.get_public_config()
            >>> public = fm.get_public_config(["password", "secret"])
        """
        if sensitive_keys is None:
            sensitive_keys_set = self._get_default_sensitive_keys()
        else:
            sensitive_keys_set = set(sensitive_keys)

        self.load_if_not_loaded()

        return self._process_sensitive_data(self.document, sensitive_keys_set, "remove")
