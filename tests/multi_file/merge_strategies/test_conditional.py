# mypy: ignore-errors
"""
Tests for ConditionalMergeStrategy
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from yapfm.multi_file.merge_strategies.conditional import ConditionalMergeStrategy
from yapfm.multi_file.merge_strategies.deep import DeepMergeStrategy


class TestConditionalMergeStrategy:
    """Test cases for ConditionalMergeStrategy"""

    def test_init_default(self):
        """Test initialization with default values"""
        strategy = ConditionalMergeStrategy()
        assert strategy.condition is not None
        assert strategy.base_strategy is not None
        assert isinstance(strategy.base_strategy, DeepMergeStrategy)

    def test_init_with_condition(self):
        """Test initialization with custom condition"""

        def custom_condition(file_path, data):
            return "test" in str(file_path)

        strategy = ConditionalMergeStrategy(condition=custom_condition)
        assert strategy.condition == custom_condition
        assert strategy.base_strategy is not None

    def test_init_with_base_strategy(self):
        """Test initialization with custom base strategy"""
        base_strategy = DeepMergeStrategy()
        strategy = ConditionalMergeStrategy(base_strategy=base_strategy)
        assert strategy.base_strategy == base_strategy

    def test_init_with_both(self):
        """Test initialization with both condition and base strategy"""

        def custom_condition(file_path, data):
            return "test" in str(file_path)

        base_strategy = DeepMergeStrategy()
        strategy = ConditionalMergeStrategy(
            condition=custom_condition, base_strategy=base_strategy
        )
        assert strategy.condition == custom_condition
        assert strategy.base_strategy == base_strategy

    def test_default_condition(self):
        """Test the default condition function"""
        strategy = ConditionalMergeStrategy()
        file_path = Path("test.json")
        data = {"key": "value"}

        # Default condition should always return True
        assert strategy._default_condition(file_path, data) is True

    def test_get_name(self):
        """Test strategy name"""
        strategy = ConditionalMergeStrategy()
        assert strategy.get_name() == "conditional"

    def test_get_description(self):
        """Test strategy description"""
        strategy = ConditionalMergeStrategy()
        expected = "Merges files based on custom conditions, using a base strategy for the actual merge"
        assert strategy.get_description() == expected

    def test_get_optional_options(self):
        """Test optional options"""
        strategy = ConditionalMergeStrategy()
        options = strategy.get_optional_options()
        assert "condition" in options
        assert "base_strategy" in options
        assert options["condition"] is None
        assert options["base_strategy"] is None

    def test_validate_options(self):
        """Test option validation"""
        strategy = ConditionalMergeStrategy()

        # Valid options
        valid_options = strategy.validate_options(condition=None, base_strategy=None)
        assert valid_options["condition"] is None
        assert valid_options["base_strategy"] is None

        # Invalid condition
        with pytest.raises(ValueError, match="condition must be callable or None"):
            strategy.validate_options(condition="not_callable")

        # Invalid base_strategy
        with pytest.raises(
            ValueError,
            match="base_strategy must be a BaseMergeStrategy instance or None",
        ):
            strategy.validate_options(base_strategy="not_strategy")

    def test_merge_empty_files(self):
        """Test merging with no files"""
        strategy = ConditionalMergeStrategy()
        result = strategy.merge([])
        assert result == {}

    def test_merge_single_file(self):
        """Test merging with a single file"""
        strategy = ConditionalMergeStrategy()
        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)
        assert result == {"key": "value"}

    def test_merge_with_condition(self):
        """Test merging with custom condition"""

        def is_json_file(file_path, data):
            return file_path.suffix == ".json"

        strategy = ConditionalMergeStrategy(condition=is_json_file)
        files = [
            (Path("test.json"), {"key": "value1"}),
            (Path("test.txt"), {"key": "value2"}),
            (Path("config.json"), {"key": "value3"}),
        ]
        result = strategy.merge(files)
        # Should only include .json files
        assert result == {"key": "value3"}  # Last .json file wins

    def test_merge_with_base_strategy(self):
        """Test merging with custom base strategy"""
        # Mock base strategy that returns specific data
        mock_base = Mock()
        mock_base.merge.return_value = {"merged": "data"}

        strategy = ConditionalMergeStrategy(base_strategy=mock_base)
        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files)

        assert result == {"merged": "data"}
        mock_base.merge.assert_called_once_with(files)

    def test_merge_with_both(self):
        """Test merging with both condition and base strategy"""

        def is_json_file(file_path, data):
            return file_path.suffix == ".json"

        mock_base = Mock()
        mock_base.merge.return_value = {"merged": "data"}

        strategy = ConditionalMergeStrategy(
            condition=is_json_file, base_strategy=mock_base
        )
        files = [
            (Path("test.json"), {"key": "value1"}),
            (Path("test.txt"), {"key": "value2"}),
        ]
        result = strategy.merge(files)

        assert result == {"merged": "data"}
        # Should only pass filtered files to base strategy
        expected_files = [(Path("test.json"), {"key": "value1"})]
        mock_base.merge.assert_called_once_with(expected_files)

    def test_merge_multiple_matching_conditions(self):
        """Test merging with multiple files matching condition"""

        def is_json_file(file_path, data):
            return file_path.suffix == ".json"

        strategy = ConditionalMergeStrategy(condition=is_json_file)
        files = [
            (Path("test1.json"), {"key1": "value1"}),
            (Path("test2.json"), {"key2": "value2"}),
            (Path("test3.json"), {"key3": "value3"}),
        ]
        result = strategy.merge(files)
        # All files match, should merge all
        assert result == {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_merge_no_matching_conditions(self):
        """Test merging with no files matching condition"""

        def is_xml_file(file_path, data):
            return file_path.suffix == ".xml"

        strategy = ConditionalMergeStrategy(condition=is_xml_file)
        files = [
            (Path("test1.json"), {"key1": "value1"}),
            (Path("test2.txt"), {"key2": "value2"}),
        ]
        result = strategy.merge(files)
        # No files match, should return empty dict
        assert result == {}

    def test_merge_complex_conditions(self):
        """Test merging with complex conditions"""

        def is_config_file(file_path, data):
            return "config" in str(file_path) and data.get("type") == "config"

        strategy = ConditionalMergeStrategy(condition=is_config_file)
        files = [
            (Path("app_config.json"), {"type": "config", "app": "MyApp"}),
            (Path("data.json"), {"type": "data", "rows": 100}),
            (Path("user_config.json"), {"type": "config", "user": "admin"}),
        ]
        result = strategy.merge(files)
        # Should only include config files
        assert result == {"type": "config", "app": "MyApp", "user": "admin"}

    def test_merge_with_kwargs(self):
        """Test merging with additional kwargs"""
        strategy = ConditionalMergeStrategy()
        files = [(Path("test.json"), {"key": "value"})]
        result = strategy.merge(files, extra_option="test")
        assert result == {"key": "value"}

    def test_get_merge_info(self):
        """Test getting merge information"""
        strategy = ConditionalMergeStrategy()
        files = [
            (Path("test1.json"), {"key1": "value1"}),
            (Path("test2.json"), {"key2": "value2"}),
        ]
        info = strategy.get_merge_info(files)

        assert "base_strategy" in info
        assert "total_files" in info
        assert "filtered_files" in info
        assert "condition_applied" in info
        assert "merge_type" in info
        assert info["total_files"] == 2
        assert info["filtered_files"] == 2  # All files match default condition
        assert info["condition_applied"] is True
        assert info["merge_type"] == "conditional"

    def test_str_representation(self):
        """Test string representation"""
        strategy = ConditionalMergeStrategy()
        str_repr = str(strategy)
        assert "ConditionalMergeStrategy" in str_repr

    def test_repr_representation(self):
        """Test repr representation"""
        strategy = ConditionalMergeStrategy()
        repr_str = repr(strategy)
        assert "ConditionalMergeStrategy" in repr_str
