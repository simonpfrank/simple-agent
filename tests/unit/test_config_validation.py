"""Unit tests for config structure validation (Issue 2-C)."""

import pytest

from simple_agent.core.config_manager import ConfigManager, ConfigValidationError


class TestConfigValidationRequired:
    """Test required keys validation."""

    def test_valid_config_with_all_required_keys(self):
        """Test config with all required top-level keys is valid."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
        }
        # Should not raise
        ConfigManager.validate(config)

    def test_config_missing_required_app_key(self):
        """Test config missing 'app' key raises error."""
        config = {
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="app"):
            ConfigManager.validate(config)

    def test_config_missing_required_logging_key(self):
        """Test config missing 'logging' key raises error."""
        config = {
            "app": {"name": "test"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="logging"):
            ConfigManager.validate(config)

    def test_config_missing_required_paths_key(self):
        """Test config missing 'paths' key raises error."""
        config = {
            "app": {"name": "test"},
            "logging": {"level": "INFO"},
        }
        with pytest.raises(ConfigValidationError, match="paths"):
            ConfigManager.validate(config)

    def test_config_with_all_required_plus_optional_keys(self):
        """Test config with required + optional keys is valid."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
            "custom": {"setting": "value"},  # Optional
            "agent": {"model": "test"},  # Optional
        }
        # Should not raise
        ConfigManager.validate(config)


class TestConfigValidationTypes:
    """Test config value type validation."""

    def test_app_section_must_be_dict(self):
        """Test 'app' value must be a dictionary."""
        config = {
            "app": "invalid_string",
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="must be a dict"):
            ConfigManager.validate(config)

    def test_logging_section_must_be_dict(self):
        """Test 'logging' value must be a dictionary."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": ["invalid", "list"],
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
        }
        with pytest.raises(ConfigValidationError, match="must be a dict"):
            ConfigManager.validate(config)

    def test_paths_section_must_be_dict(self):
        """Test 'paths' value must be a dictionary."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": 123,
        }
        with pytest.raises(ConfigValidationError, match="must be a dict"):
            ConfigManager.validate(config)

    def test_optional_sections_must_be_dict(self):
        """Test optional sections must be dictionaries if present."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
            "custom": "invalid_string",
        }
        with pytest.raises(ConfigValidationError, match="custom.*must be a dict"):
            ConfigManager.validate(config)


class TestConfigValidationAppRequired:
    """Test required keys within 'app' section."""

    def test_app_missing_name_key(self):
        """Test 'app' section missing 'name' key raises error."""
        config = {
            "app": {"version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="app.name"):
            ConfigManager.validate(config)

    def test_app_missing_version_key(self):
        """Test 'app' section missing 'version' key raises error."""
        config = {
            "app": {"name": "test"},
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="app.version"):
            ConfigManager.validate(config)

    def test_app_name_must_be_string(self):
        """Test 'app.name' must be a string."""
        config = {
            "app": {"name": 123, "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="app.name.*string"):
            ConfigManager.validate(config)

    def test_app_version_must_be_string(self):
        """Test 'app.version' must be a string."""
        config = {
            "app": {"name": "test", "version": 1.0},
            "logging": {"level": "INFO"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="app.version.*string"):
            ConfigManager.validate(config)


class TestConfigValidationLoggingRequired:
    """Test required keys within 'logging' section."""

    def test_logging_missing_level_key(self):
        """Test 'logging' section missing 'level' key raises error."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"file": "app.log"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="logging.level"):
            ConfigManager.validate(config)

    def test_logging_level_must_be_string(self):
        """Test 'logging.level' must be a string."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": 123},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="logging.level.*string"):
            ConfigManager.validate(config)

    def test_logging_level_must_be_valid_level(self):
        """Test 'logging.level' must be a valid log level."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INVALID_LEVEL"},
            "paths": {},
        }
        with pytest.raises(ConfigValidationError, match="logging.level.*valid"):
            ConfigManager.validate(config)

    def test_logging_valid_levels(self):
        """Test all valid logging levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = {
                "app": {"name": "test", "version": "1.0"},
                "logging": {"level": level},
                "paths": {"prompts": "config/prompts/", "tools": "tools/"},
            }
            # Should not raise
            ConfigManager.validate(config)


class TestConfigValidationPathsRequired:
    """Test required keys within 'paths' section."""

    def test_paths_missing_prompts_key(self):
        """Test 'paths' section missing 'prompts' key raises error."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"tools": "tools/"},
        }
        with pytest.raises(ConfigValidationError, match="prompts"):
            ConfigManager.validate(config)

    def test_paths_missing_tools_key(self):
        """Test 'paths' section missing 'tools' key raises error."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/"},
        }
        with pytest.raises(ConfigValidationError, match="tools"):
            ConfigManager.validate(config)

    def test_paths_values_must_be_strings(self):
        """Test 'paths' values must be strings."""
        config = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": 123},
        }
        with pytest.raises(ConfigValidationError, match="paths.tools.*string"):
            ConfigManager.validate(config)


class TestConfigValidationIntegration:
    """Integration tests for config validation."""

    def test_valid_default_config(self):
        """Test default config structure is valid."""
        defaults = ConfigManager.get_defaults()
        # Should not raise
        ConfigManager.validate(defaults)

    def test_empty_config_invalid(self):
        """Test empty config is invalid."""
        config = {}
        with pytest.raises(ConfigValidationError):
            ConfigManager.validate(config)

    def test_none_config_invalid(self):
        """Test None config is invalid."""
        with pytest.raises(ConfigValidationError):
            ConfigManager.validate(None)

    def test_non_dict_config_invalid(self):
        """Test non-dict config is invalid."""
        with pytest.raises(ConfigValidationError, match="must be a dict"):
            ConfigManager.validate("not_a_dict")

    def test_validation_error_has_clear_message(self):
        """Test validation errors have clear messages."""
        config = {
            "app": "invalid",
            "logging": {"level": "INFO"},
            "paths": {},
        }
        try:
            ConfigManager.validate(config)
            pytest.fail("Should have raised ConfigValidationError")
        except ConfigValidationError as e:
            assert "app" in str(e)
            assert "dict" in str(e)


class TestLoadWithValidation:
    """Test that load() validates the loaded config."""

    def test_load_with_valid_config(self, tmp_path):
        """Test load() validates and accepts valid config."""
        import yaml

        config_file = tmp_path / "config.yaml"
        config_data = {
            "app": {"name": "test", "version": "1.0"},
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
        }
        config_file.write_text(yaml.dump(config_data))

        # Should not raise
        result = ConfigManager.load(str(config_file), validate=True)
        assert result == config_data

    def test_load_with_invalid_config_raises_error(self, tmp_path):
        """Test load() raises error for invalid config structure."""
        import yaml

        config_file = tmp_path / "config.yaml"
        config_data = {
            "app": "invalid",  # Should be dict
            "logging": {"level": "INFO"},
            "paths": {"prompts": "config/prompts/", "tools": "tools/"},
        }
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ConfigValidationError):
            ConfigManager.load(str(config_file), validate=True)

    def test_load_without_validation_skips_structure_check(self, tmp_path):
        """Test load() with validate=False skips structure validation."""
        import yaml

        config_file = tmp_path / "config.yaml"
        config_data = {"app": "invalid"}  # Invalid structure
        config_file.write_text(yaml.dump(config_data))

        # Should not raise (validation disabled)
        result = ConfigManager.load(str(config_file), validate=False)
        assert result == config_data
