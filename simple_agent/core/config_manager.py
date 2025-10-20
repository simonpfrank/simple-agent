"""
Configuration management module.
Handles loading, saving, and accessing configuration values.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading, saving, and access."""

    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file with validation.

        Args:
            path: Path to config file

        Returns:
            Dictionary containing configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If config is not a dictionary
        """
        config_path = Path(path)

        if not config_path.exists():
            logger.error(f"Config file not found: {path}")
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if config is None:
                config = {}

            # Validate that config is a dictionary
            if not isinstance(config, dict):
                raise ValueError(
                    f"Config must be a dictionary, got {type(config).__name__}"
                )

            logger.info(f"Config loaded from: {path}")
            return config

        except yaml.YAMLError as e:
            logger.exception(f"Invalid YAML in config file: {path}")
            raise ValueError(f"Invalid YAML in config file: {path}") from e

    @staticmethod
    def save(config: Dict[str, Any], path: str) -> None:
        """
        Save configuration to YAML file.

        Args:
            config: Configuration dictionary
            path: Path to save config file
        """
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Config saved to: {path}")

        except Exception:
            logger.exception(f"Failed to save config: {path}")
            raise

    @staticmethod
    def get(config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Get nested config value using dot notation.

        Args:
            config: Configuration dictionary
            key: Dot-separated key path (e.g., 'logging.level')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config = {'logging': {'level': 'INFO'}}
            >>> ConfigManager.get(config, 'logging.level')
            'INFO'
        """
        keys = key.split(".")
        value = config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @staticmethod
    def set(config: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set nested config value using dot notation.

        Args:
            config: Configuration dictionary (modified in place)
            key: Dot-separated key path (e.g., 'logging.level')
            value: Value to set

        Raises:
            ValueError: If intermediate key is not a dictionary

        Example:
            >>> config = {}
            >>> ConfigManager.set(config, 'logging.level', 'DEBUG')
            >>> config
            {'logging': {'level': 'DEBUG'}}
        """
        keys = key.split(".")
        current = config

        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                raise ValueError(
                    f"Cannot set {key}: '{k}' is not a dictionary "
                    f"(got {type(current[k]).__name__})"
                )
            current = current[k]

        # Set the final key
        current[keys[-1]] = value
        logger.debug(f"Config updated: {key} = {value}")

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Dictionary with default configuration
        """
        return {
            "app": {"name": "My Application", "version": "1.0.0"},
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "console_enabled": False,
            },
            "paths": {"input_dir": "data/input", "output_dir": "data/output"},
            "agent": {
                "enabled": False,  # EXPERIMENTAL: Agent mode not fully implemented
                "model": "gpt-4",
                "api_key_env": "OPENAI_API_KEY",
            },
            "custom": {
                # Project-specific settings go here
            },
        }

    @staticmethod
    def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded config with defaults.
        Config values override defaults.

        Args:
            config: Loaded configuration

        Returns:
            Merged configuration
        """
        defaults = ConfigManager.get_defaults()

        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Recursively merge two dictionaries."""
            result = base.copy()
            for key, value in override.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(defaults, config)
