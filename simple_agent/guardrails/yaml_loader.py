"""YAML configuration loader for guardrails."""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_guardrails_from_yaml(file_path: str) -> Dict[str, Any]:
    """Load guardrail configuration from YAML file.

    Args:
        file_path: Path to YAML configuration file

    Returns:
        Dictionary with 'input_guardrails' key containing list of guardrail configs

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f) or {}

    return config
