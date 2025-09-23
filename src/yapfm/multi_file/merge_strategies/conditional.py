"""
Conditional Merge Strategy

This strategy merges files based on conditions. It allows for complex
merging logic where files are included or excluded based on their content,
file path, or other criteria. This is useful for environment-specific
configurations or dynamic file selection.

Key Features:
- Conditional file inclusion/exclusion
- Custom condition functions
- Environment-based merging
- Dynamic file selection

Example:
    >>> from yapfm.multi_file.strategies import ConditionalMergeStrategy
    >>>
    >>> def is_production_config(file_path, data):
    ...     return "prod" in str(file_path) or data.get("environment") == "production"
    >>>
    >>> strategy = ConditionalMergeStrategy(condition=is_production_config)
    >>> result = strategy.merge([
    ...     (Path("base.json"), {"app": {"name": "MyApp"}}),
    ...     (Path("prod.json"), {"app": {"debug": False}})
    ... ])
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .base import BaseMergeStrategy


class ConditionalMergeStrategy(BaseMergeStrategy):
    """
    Strategy for merging files based on conditions.

    This strategy allows for complex merging logic where files are
    included or excluded based on custom conditions. It supports
    both file-level and content-level conditions.
    """

    def __init__(
        self,
        condition: Optional[Callable[[Path, Dict[str, Any]], bool]] = None,
        base_strategy: Optional[BaseMergeStrategy] = None,
        **options: Any,
    ) -> None:
        """
        Initialize the conditional merge strategy.

        Args:
            condition: Function to determine if a file should be included.
            base_strategy: Strategy to use for merging filtered files.
            **options: Additional strategy options.
        """
        super().__init__(condition=condition, base_strategy=base_strategy, **options)
        self.condition = condition or self._default_condition
        self.base_strategy = base_strategy or self._get_default_base_strategy()

    def _default_condition(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Default condition that includes all files.

        Args:
            file_path: Path to the file.
            data: File data.

        Returns:
            Always True (include all files).
        """
        return True

    def _get_default_base_strategy(self) -> BaseMergeStrategy:
        """Get the default base strategy for merging."""
        from .deep import DeepMergeStrategy

        return DeepMergeStrategy()

    def merge(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Merge files based on conditions.

        Args:
            loaded_files: List of tuples containing (file_path, data).
            **kwargs: Additional merge options.

        Returns:
            Dictionary with merged data from filtered files.

        Example:
            >>> def is_config_file(file_path, data):
            ...     return file_path.suffix == ".json" and "config" in str(file_path)
            >>>
            >>> strategy = ConditionalMergeStrategy(condition=is_config_file)
            >>> result = strategy.merge([
            ...     (Path("config.json"), {"app": {"name": "MyApp"}}),
            ...     (Path("data.csv"), {"rows": 100}),
            ...     (Path("app_config.json"), {"app": {"version": "1.0"}})
            ... ])
            >>> # Only config.json and app_config.json will be merged
        """
        if not loaded_files:
            return {}

        # Filter files based on condition
        filtered_files = []
        for file_path, data in loaded_files:
            if self.condition(file_path, data):
                filtered_files.append((file_path, data))

        # Use base strategy to merge filtered files
        return self.base_strategy.merge(filtered_files, **kwargs)

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "conditional"

    def get_description(self) -> str:
        """Get description of this strategy."""
        return "Merges files based on custom conditions, using a base strategy for the actual merge"

    def get_optional_options(self) -> Dict[str, Any]:
        """Get optional options with defaults."""
        return {"condition": None, "base_strategy": None}

    def validate_options(self, **options: Any) -> Dict[str, Any]:
        """Validate and normalize options."""
        validated = super().validate_options(**options)

        # Validate condition
        if "condition" in validated:
            condition = validated["condition"]
            if condition is not None and not callable(condition):
                raise ValueError("condition must be callable or None")

        # Validate base_strategy
        if "base_strategy" in validated:
            base_strategy = validated["base_strategy"]
            if base_strategy is not None and not isinstance(
                base_strategy, BaseMergeStrategy
            ):
                raise ValueError(
                    "base_strategy must be a BaseMergeStrategy instance or None"
                )

        return validated

    def get_merge_info(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get detailed merge information."""
        info = super().get_merge_info(loaded_files)

        # Count filtered files
        filtered_count = sum(
            1 for file_path, data in loaded_files if self.condition(file_path, data)
        )

        info.update(
            {
                "base_strategy": self.base_strategy.get_name(),
                "total_files": len(loaded_files),
                "filtered_files": filtered_count,
                "condition_applied": True,
                "merge_type": "conditional",
            }
        )
        return info

    def preprocess_files(
        self, loaded_files: List[Tuple[Path, Dict[str, Any]]]
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """Preprocess files by applying condition filter."""
        return [
            (file_path, data)
            for file_path, data in loaded_files
            if self.condition(file_path, data)
        ]
