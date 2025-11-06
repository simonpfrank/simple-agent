"""Unit tests for YAML guardrail configuration - TDD approach."""

import tempfile
from pathlib import Path

import pytest

from simple_agent.guardrails.input_validators import PIIDetector
from simple_agent.guardrails.yaml_loader import load_guardrails_from_yaml


class TestGuardrailYAMLLoader:
    """Test YAML guardrail configuration loading."""

    def test_load_pii_detector_config(self):
        """Test loading PIIDetector from YAML."""
        yaml_content = """
input_guardrails:
  - type: "pii_detector"
    redact: true
    types:
      - "email"
      - "phone"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            guardrails_config = load_guardrails_from_yaml(temp_path)
            assert "input_guardrails" in guardrails_config
            assert len(guardrails_config["input_guardrails"]) == 1
        finally:
            # Clean up - file is now closed so Windows can delete it
            Path(temp_path).unlink(missing_ok=True)

    def test_load_multiple_guardrails(self):
        """Test loading multiple guardrails from YAML."""
        yaml_content = """
input_guardrails:
  - type: "pii_detector"
    redact: true
    types:
      - "email"
      - "ssn"
  - type: "custom"
    function: "my_module.check_sql"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            guardrails_config = load_guardrails_from_yaml(temp_path)
            assert len(guardrails_config["input_guardrails"]) == 2
            assert guardrails_config["input_guardrails"][0]["type"] == "pii_detector"
            assert guardrails_config["input_guardrails"][1]["type"] == "custom"
        finally:
            # Clean up - file is now closed so Windows can delete it
            Path(temp_path).unlink(missing_ok=True)

    def test_load_empty_guardrails(self):
        """Test loading YAML with no guardrails."""
        yaml_content = """
name: "test_agent"
role: "Test agent"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            guardrails_config = load_guardrails_from_yaml(temp_path)
            assert "input_guardrails" not in guardrails_config or not guardrails_config.get(
                "input_guardrails"
            )
        finally:
            # Clean up - file is now closed so Windows can delete it
            Path(temp_path).unlink(missing_ok=True)

    def test_instantiate_pii_detector_from_config(self):
        """Test creating PIIDetector instance from YAML config."""
        config = {"type": "pii_detector", "redact": True, "types": ["email", "phone"]}

        detector = PIIDetector(types=config["types"], redact=config["redact"])

        assert detector.redact is True
        assert "email" in detector.types
        assert "phone" in detector.types

    def test_pii_config_with_defaults(self):
        """Test PIIDetector config with default values."""
        config = {"type": "pii_detector"}  # No redact or types specified

        # Should use defaults
        detector = PIIDetector(
            types=config.get("types", ["email", "phone", "ssn"]),
            redact=config.get("redact", True),
        )

        assert detector.redact is True
        assert len(detector.types) == 3

    def test_yaml_with_custom_rule_reference(self):
        """Test YAML with custom rule function reference."""
        yaml_content = """
input_guardrails:
  - type: "custom"
    function: "validators.no_sql_injection"
    description: "Prevents SQL injection attempts"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name

        try:
            guardrails_config = load_guardrails_from_yaml(temp_path)
            assert guardrails_config["input_guardrails"][0]["function"] == "validators.no_sql_injection"
            assert (
                guardrails_config["input_guardrails"][0]["description"]
                == "Prevents SQL injection attempts"
            )
        finally:
            # Clean up - file is now closed so Windows can delete it
            Path(temp_path).unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent YAML file."""
        with pytest.raises(FileNotFoundError):
            load_guardrails_from_yaml("/nonexistent/path/config.yaml")
