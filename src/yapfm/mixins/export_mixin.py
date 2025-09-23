"""
Export Mixin

This module provides export functionality for the FileManager.
The ExportMixin contains operations for exporting data to different formats.
"""

# mypy: ignore-errors

import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

from yapfm.registry import FileStrategyRegistry


class ExportMixin:
    """
    Mixin for data export operations.
    """

    def _get_export_strategy(self, format_name: str):
        """Get the appropriate strategy for export (current or different format)."""
        # Check if we can use the current strategy
        current_format = self.path.suffix[1:].lower() if self.path.suffix else ""
        if format_name.lower() == current_format:
            # Use the current strategy directly
            return self.strategy
        else:
            # Get strategy for different format using registry directly
            strategy = FileStrategyRegistry.get_strategy(format_name)
            if not strategy:
                raise ValueError(f"No strategy available for format: {format_name}")
            return strategy

    def _export_to_string(self, data: Any, format_name: str) -> str:
        """Export data to string using the appropriate strategy."""
        strategy = self._get_export_strategy(format_name)

        # Create a temporary file to use the strategy's save method
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{format_name}", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # Use the strategy to save the data
            strategy.save(temp_path, data)

            # Read the content back
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            return content
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _export_to_file(
        self, data: Any, output_path: Union[str, Path], format_name: str
    ) -> Path:
        """Export data to file using the appropriate strategy."""
        output_path = Path(output_path)
        strategy = self._get_export_strategy(format_name)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use strategy to save the data
        strategy.save(output_path, data)

        return output_path

    def to_current_format(self) -> str:
        """
        Export data to the current file's format using the manager's strategy.

        Returns:
            String content in the current format

        Example:
            >>> fm = YAPFileManager("config.json")
            >>> json_str = fm.to_current_format()  # Uses JSON strategy
        """
        self.load_if_not_loaded()
        current_format = self.path.suffix[1:].lower() if self.path.suffix else ""
        return self._export_to_string(self.document, current_format)

    def to_json(self, pretty: bool = True) -> str:
        """
        Export data to JSON format.

        Args:
            pretty: If True, formats with indentation

        Returns:
            JSON string

        Example:
            >>> json_str = fm.to_json()
            >>> json_str = fm.to_json(pretty=False)  # Compact format
        """
        self.load_if_not_loaded()

        # For JSON, we can use the strategy directly or fallback to json module
        # if we need custom formatting options
        if pretty:
            return self._export_to_string(self.document, "json")
        else:
            # For compact JSON, we need to use json directly since strategies
            # typically format with indentation
            import json

            return json.dumps(self.document, ensure_ascii=False)

    def to_yaml(self) -> str:
        """
        Export data to YAML format.

        Returns:
            YAML string

        Example:
            >>> yaml_str = fm.to_yaml()
        """
        self.load_if_not_loaded()
        return self._export_to_string(self.document, "yaml")

    def to_toml(self) -> str:
        """
        Export data to TOML format.

        Returns:
            TOML string

        Example:
            >>> toml_str = fm.to_toml()
        """
        self.load_if_not_loaded()
        return self._export_to_string(self.document, "toml")

    def export_section(
        self,
        section_path: str,
        format: str = "json",
        output_path: Optional[Union[str, Path]] = None,
    ) -> Union[str, Path]:
        """
        Export a specific section to a file or return as string.

        Args:
            section_path: Dot-separated path to the section
            format: Output format ("json", "yaml", "toml")
            output_path: Optional output file path. If None, returns string

        Returns:
            String content or output file path

        Example:
            >>> fm.export_section("database", "json")  # Returns JSON string
            >>> fm.export_section("api", "yaml", "api_config.yaml")  # Saves to file
        """
        self.load_if_not_loaded()

        # Get the section data
        section_data = self.get(section_path)
        if section_data is None:
            raise KeyError(f"Section '{section_path}' not found")

        # Export using the appropriate method
        if output_path is not None:
            return self._export_to_file(section_data, output_path, format)
        else:
            return self._export_to_string(section_data, format)

    def export_to_file(
        self, output_path: Union[str, Path], format: Optional[str] = None
    ) -> Path:
        """
        Export the entire data to a file in the specified format.

        Args:
            output_path: Output file path
            format: Output format. If None, inferred from file extension

        Returns:
            Output file path

        Example:
            >>> fm.export_to_file("backup.json")
            >>> fm.export_to_file("config.yaml", "yaml")
        """
        output_path = Path(output_path)

        # Infer format from extension if not provided
        if format is None:
            format = FileStrategyRegistry.infer_format_from_extension(output_path)

        self.load_if_not_loaded()
        return self._export_to_file(self.document, output_path, format)
