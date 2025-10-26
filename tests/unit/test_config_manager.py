"""
Unit tests for ConfigManager.

Tests configuration loading, saving, accessing, and template management.
"""

import os
from pathlib import Path

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


class TestConfigManagerResolveEnvVar:
    """Test environment variable resolution."""

    def test_resolve_env_var_with_placeholder(self, monkeypatch) -> None:
        """Test resolving ${VAR} placeholder."""
        monkeypatch.setenv("TEST_KEY", "secret123")

        result = ConfigManager.resolve_env_var("${TEST_KEY}")

        assert result == "secret123"

    def test_resolve_env_var_without_placeholder(self) -> None:
        """Test literal value passes through unchanged."""
        result = ConfigManager.resolve_env_var("literal_value")

        assert result == "literal_value"

    def test_resolve_env_var_missing_env_var(self) -> None:
        """Test missing env var returns empty string."""
        result = ConfigManager.resolve_env_var("${NONEXISTENT_VAR}")

        assert result == ""

    def test_resolve_env_var_non_string(self) -> None:
        """Test non-string values pass through unchanged."""
        assert ConfigManager.resolve_env_var(123) == 123
        assert ConfigManager.resolve_env_var(None) is None
        assert ConfigManager.resolve_env_var({"key": "value"}) == {"key": "value"}
