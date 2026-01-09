"""Runtime configuration access for tools and components.

This module provides a global runtime configuration that can be accessed
by tools and other components that don't have direct access to the config dict.

Thread-safe implementation using a lock for concurrent access.

Usage:
    # In app.py initialization:
    from simple_agent.core.runtime_config import set_config
    config = ConfigManager.load("config.yaml")
    set_config(config)

    # In tools or components:
    from simple_agent.core.runtime_config import get_config, get_config_value
    config = get_config()
    verify_certs = get_config_value("verify_certificates", default=True)
"""

import threading
from typing import Any, Dict, Optional

# Module-level config storage with thread-safety lock
_config_lock = threading.Lock()
_runtime_config: Optional[Dict[str, Any]] = None


def set_config(config: Optional[Dict[str, Any]]) -> None:
    """Set the runtime configuration (thread-safe).

    This should be called once during application initialization.

    Args:
        config: Configuration dictionary from ConfigManager.load()
               Pass None to clear the config.
    """
    global _runtime_config
    with _config_lock:
        _runtime_config = config if config is not None else None


def get_config() -> Dict[str, Any]:
    """Get the runtime configuration (thread-safe).

    Returns:
        Configuration dictionary, or empty dict if not set.
    """
    with _config_lock:
        if _runtime_config is None:
            return {}
        return _runtime_config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific configuration value by key (thread-safe).

    Args:
        key: Configuration key to retrieve
        default: Default value if key not found or config not set

    Returns:
        Configuration value or default
    """
    config = get_config()
    return config.get(key, default)


def _reset_config() -> None:
    """Reset the runtime config to None (thread-safe).

    This is primarily for testing purposes to ensure clean state
    between test cases.
    """
    global _runtime_config
    with _config_lock:
        _runtime_config = None
