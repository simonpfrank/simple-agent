"""
Configuration management module.
Handles loading, saving, and accessing configuration values.
"""

import os
import re
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
    def load_env(path: str = ".env") -> Dict[str, str]:
        """
        Load environment variables from .env file and set them in os.environ.

        Args:
            path: Path to .env file (defaults to ".env")

        Returns:
            Dictionary of environment variables loaded

        Raises:
            None - returns empty dict if file not found
        """
        env_path = Path(path)

        if not env_path.exists():
            logger.debug(f"Env file not found: {path}")
            return {}

        env_vars = {}
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        env_vars[key] = value
                        # Set in os.environ so it's available to child processes
                        os.environ[key] = value

            logger.info(f"Loaded {len(env_vars)} env variables from: {path}")
            return env_vars

        except Exception:
            logger.exception(f"Failed to load env file: {path}")
            raise

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

    @staticmethod
    def load_prompt_template(
        template_name: str, base_path: str = "."
    ) -> Dict[str, Any]:
        """
        Load prompt template from config/prompts/{template_name}.yaml

        Args:
            template_name: Name of template (without .yaml extension)
            base_path: Base directory path (defaults to current directory)

        Returns:
            Dictionary containing template data

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template YAML is invalid
        """
        template_path = Path(base_path) / "config" / "prompts" / f"{template_name}.yaml"

        if not template_path.exists():
            logger.error(f"Prompt template not found: {template_path}")
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)

            if not isinstance(template_data, dict):
                raise ValueError(
                    f"Prompt template must be a dictionary, got {type(template_data).__name__}"
                )

            logger.info(f"Loaded prompt template: {template_name}")
            return template_data

        except yaml.YAMLError as e:
            logger.exception(f"Invalid YAML in template: {template_path}")
            raise ValueError(f"Invalid YAML in template: {template_path}") from e

    @staticmethod
    def resolve_env_var(value: str) -> str:
        """
        Resolve a single environment variable placeholder to its actual value.

        Used for point-of-use substitution (e.g., when creating API clients).
        This keeps secrets out of the config dict and only resolves when needed.

        Args:
            value: String that may contain ${VAR_NAME} placeholder

        Returns:
            Resolved value with environment variable substituted, or original value

        Examples:
            >>> os.environ['API_KEY'] = 'secret123'
            >>> ConfigManager.resolve_env_var('${API_KEY}')
            'secret123'
            >>> ConfigManager.resolve_env_var('literal_value')
            'literal_value'
        """
        if not isinstance(value, str):
            return value

        # Check if it's a ${VAR} pattern
        pattern = r"^\$\{([^}]+)\}$"
        match = re.match(pattern, value)

        if match:
            var_name = match.group(1)
            env_value = os.environ.get(var_name, "")
            if not env_value:
                logger.warning(
                    f"Environment variable '{var_name}' not found, using empty string"
                )
            return env_value

        return value

    @staticmethod
    def substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively substitute ${VAR_NAME} patterns with environment variable values.

        NOTE: This method creates a NEW dict with substituted values.
        Only use for temporary display purposes (e.g., /config show).
        The main config dict should keep placeholders to avoid storing secrets.

        Args:
            config: Configuration dictionary

        Returns:
            NEW configuration dict with environment variables substituted
        """

        def substitute_value(value: Any) -> Any:
            """Recursively substitute env vars in values."""
            if isinstance(value, str):
                return ConfigManager.resolve_env_var(value)
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value

        return substitute_value(config)
