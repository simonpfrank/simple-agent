"""
Unit tests for ConfigManager.

Tests configuration loading, saving, accessing, and template management.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml

from simple_agent.core.config_manager import ConfigManager


class TestConfigManagerLoad:
    """Test YAML configuration loading."""

    def test_load_valid_yaml(self, tmp_path: Path) -> None:
        """Test loading valid YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_data = {"app": {"name": "test"}, "logging": {"level": "DEBUG"}}
        config_file.write_text(yaml.dump(config_data))

        result = ConfigManager.load(str(config_file))

        assert result == config_data

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        """Test loading empty YAML file returns empty dict."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        result = ConfigManager.load(str(config_file))

        assert result == {}

    def test_load_nonexistent_file(self) -> None:
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigManager.load("nonexistent.yaml")

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test loading invalid YAML raises ValueError."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:")

        with pytest.raises(ValueError, match="Invalid YAML"):
            ConfigManager.load(str(config_file))

    def test_load_non_dict_yaml(self, tmp_path: Path) -> None:
        """Test loading non-dict YAML raises ValueError."""
        config_file = tmp_path / "list.yaml"
        config_file.write_text("- item1\n- item2")

        with pytest.raises(ValueError, match="must be a dictionary"):
            ConfigManager.load(str(config_file))


class TestConfigManagerGet:
    """Test nested configuration value access."""

    def test_get_simple_key(self) -> None:
        """Test getting simple top-level key."""
        config = {"name": "test"}

        result = ConfigManager.get(config, "name")

        assert result == "test"

    def test_get_nested_key(self) -> None:
        """Test getting nested key with dot notation."""
        config = {"logging": {"level": "INFO", "file": "app.log"}}

        result = ConfigManager.get(config, "logging.level")

        assert result == "INFO"

    def test_get_deeply_nested_key(self) -> None:
        """Test getting deeply nested key."""
        config = {"llm": {"openai": {"api_key": "sk-test"}}}

        result = ConfigManager.get(config, "llm.openai.api_key")

        assert result == "sk-test"

    def test_get_nonexistent_key_returns_default(self) -> None:
        """Test getting non-existent key returns default value."""
        config = {"logging": {"level": "INFO"}}

        result = ConfigManager.get(config, "logging.nonexistent", default="DEFAULT")

        assert result == "DEFAULT"

    def test_get_nonexistent_nested_path_returns_default(self) -> None:
        """Test getting non-existent nested path returns default."""
        config = {"logging": {"level": "INFO"}}

        result = ConfigManager.get(config, "nonexistent.path.here", default=None)

        assert result is None


class TestConfigManagerLoadEnv:
    """Test environment variable loading from .env file."""

    def test_load_env_file_exists(self, tmp_path: Path) -> None:
        """Test loading .env file with valid variables."""
        env_file = tmp_path / ".env"
        env_file.write_text("OPENAI_API_KEY=sk-test123\nANTHROPIC_API_KEY=sk-ant-456")

        result = ConfigManager.load_env(str(env_file))

        assert result["OPENAI_API_KEY"] == "sk-test123"
        assert result["ANTHROPIC_API_KEY"] == "sk-ant-456"

    def test_load_env_file_not_found(self) -> None:
        """Test loading non-existent .env file returns empty dict."""
        result = ConfigManager.load_env("nonexistent.env")

        assert result == {}

    def test_load_env_with_comments_and_empty_lines(self, tmp_path: Path) -> None:
        """Test .env file with comments and empty lines."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# API Keys\nOPENAI_API_KEY=sk-test\n\n# Empty line above\nDEBUG=true"
        )

        result = ConfigManager.load_env(str(env_file))

        assert result["OPENAI_API_KEY"] == "sk-test"
        assert result["DEBUG"] == "true"
        assert "#" not in str(result)

    def test_load_env_default_path(self, tmp_path: Path) -> None:
        """Test load_env uses default .env path when not specified."""
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            env_file = tmp_path / ".env"
            env_file.write_text("TEST_VAR=test_value")

            result = ConfigManager.load_env()

            assert result["TEST_VAR"] == "test_value"
        finally:
            os.chdir(original_cwd)


class TestConfigManagerLoadPromptTemplate:
    """Test prompt template loading from config/prompts/ directory."""

    def test_load_prompt_template_default(self, tmp_path: Path) -> None:
        """Test loading default.yaml prompt template."""
        prompts_dir = tmp_path / "config" / "prompts"
        prompts_dir.mkdir(parents=True)
        template_file = prompts_dir / "default.yaml"
        template_data = {
            "name": "default",
            "system": "You are a helpful AI assistant.\nAnswer questions clearly.",
        }
        template_file.write_text(yaml.dump(template_data))

        result = ConfigManager.load_prompt_template("default", str(tmp_path))

        assert result["name"] == "default"
        assert "helpful AI assistant" in result["system"]

    def test_load_prompt_template_researcher(self, tmp_path: Path) -> None:
        """Test loading researcher.yaml prompt template."""
        prompts_dir = tmp_path / "config" / "prompts"
        prompts_dir.mkdir(parents=True)
        template_file = prompts_dir / "researcher.yaml"
        template_data = {
            "name": "researcher",
            "system": "You are a research assistant.\nProvide detailed answers.",
        }
        template_file.write_text(yaml.dump(template_data))

        result = ConfigManager.load_prompt_template("researcher", str(tmp_path))

        assert result["name"] == "researcher"
        assert "research assistant" in result["system"]

    def test_load_prompt_template_not_found(self, tmp_path: Path) -> None:
        """Test loading non-existent template raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigManager.load_prompt_template("nonexistent", str(tmp_path))

    def test_load_prompt_template_default_base_path(self) -> None:
        """Test load_prompt_template uses current directory by default."""
        # This will fail initially since we don't have the template
        # but tests the default path behavior
        with pytest.raises(FileNotFoundError):
            ConfigManager.load_prompt_template("default")


class TestConfigManagerMergeWithDefaults:
    """Test merging config with default values."""

    def test_merge_empty_config_returns_defaults(self) -> None:
        """Test merging empty config returns full defaults."""
        config = {}

        result = ConfigManager.merge_with_defaults(config)

        defaults = ConfigManager.get_defaults()
        assert result == defaults

    def test_merge_overrides_defaults(self) -> None:
        """Test user config overrides default values."""
        config = {"logging": {"level": "DEBUG"}}

        result = ConfigManager.merge_with_defaults(config)

        assert result["logging"]["level"] == "DEBUG"
        # Other defaults should still be present
        assert "file" in result["logging"]

    def test_merge_preserves_new_keys(self) -> None:
        """Test merge preserves keys not in defaults."""
        config = {"custom_key": "custom_value"}

        result = ConfigManager.merge_with_defaults(config)

        assert result["custom_key"] == "custom_value"
        # Defaults should also be present
        assert "logging" in result
