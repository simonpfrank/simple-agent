"""
Unit tests for core business logic.
These tests demonstrate testing core functions without CLI/REPL.
"""

import pytest
from pathlib import Path

from repl_cli_template.core.processor import process_data
from repl_cli_template.core.config_manager import ConfigManager


class TestProcessor:
    """Tests for the processor module."""

    def test_process_data_success(self, tmp_path):
        """Test successful data processing."""
        # Create a temporary input file
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("hello\nworld\n")

        # Configure output directory
        output_dir = tmp_path / "output"
        config = {"paths": {"output_dir": str(output_dir)}}

        # Process data
        result = process_data(str(input_file), config)

        # Verify results
        assert result["status"] == "success"
        assert result["rows"] == 2
        assert Path(result["output"]).exists()

        # Verify output content
        output_content = Path(result["output"]).read_text()
        assert "HELLO" in output_content
        assert "WORLD" in output_content

    def test_process_data_file_not_found(self):
        """Test processing with non-existent file."""
        config = {}

        # Non-existent files raise ValueError (invalid path)
        with pytest.raises(ValueError) as exc_info:
            process_data("nonexistent.txt", config)

        assert "invalid input path" in str(exc_info.value).lower()


class TestConfigManager:
    """Tests for the configuration manager."""

    def test_load_config(self, tmp_path):
        """Test loading configuration from file."""
        # Create a temporary config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
  version: "1.0.0"

logging:
  level: "DEBUG"
        """)

        # Load config
        config = ConfigManager.load(str(config_file))

        assert config["app"]["name"] == "Test App"
        assert config["logging"]["level"] == "DEBUG"

    def test_load_nonexistent_config(self):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError):
            ConfigManager.load("nonexistent.yaml")

    def test_save_config(self, tmp_path):
        """Test saving configuration to file."""
        config_file = tmp_path / "saved_config.yaml"

        config = {"app": {"name": "Test"}, "logging": {"level": "INFO"}}

        ConfigManager.save(config, str(config_file))

        assert config_file.exists()

        # Verify saved content
        loaded = ConfigManager.load(str(config_file))
        assert loaded["app"]["name"] == "Test"

    def test_get_nested_value(self):
        """Test getting nested config values."""
        config = {"logging": {"level": "INFO", "file": "app.log"}}

        value = ConfigManager.get(config, "logging.level")
        assert value == "INFO"

        # Test default value
        value = ConfigManager.get(config, "nonexistent.key", "default")
        assert value == "default"

    def test_set_nested_value(self):
        """Test setting nested config values."""
        config = {}

        ConfigManager.set(config, "logging.level", "DEBUG")
        ConfigManager.set(config, "logging.file", "test.log")

        assert config["logging"]["level"] == "DEBUG"
        assert config["logging"]["file"] == "test.log"

    def test_merge_with_defaults(self):
        """Test merging config with defaults."""
        custom_config = {
            "app": {
                "name": "Custom App"  # Override default
            },
            "custom": {
                "new_setting": "value"  # Add new setting
            },
        }

        merged = ConfigManager.merge_with_defaults(custom_config)

        # Custom value overrides default
        assert merged["app"]["name"] == "Custom App"

        # Default value is preserved
        assert "version" in merged["app"]

        # New custom value is included
        assert merged["custom"]["new_setting"] == "value"
