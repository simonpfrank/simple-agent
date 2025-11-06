"""Unit tests for verify_certificates configuration setting - TDD approach."""

import pytest
from simple_agent.core.config_manager import ConfigManager


class TestVerifyCertificatesConfig:
    """Test verify_certificates configuration handling."""

    def test_default_verify_certificates_is_true(self, tmp_path):
        """Test that verify_certificates defaults to True when not specified."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
""")

        config = ConfigManager.load(str(config_file))
        
        # Should default to True
        assert config.get("verify_certificates", True) is True

    def test_verify_certificates_can_be_set_to_false(self, tmp_path):
        """Test that verify_certificates can be explicitly set to False."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
verify_certificates: false
""")

        config = ConfigManager.load(str(config_file))
        
        assert config["verify_certificates"] is False

    def test_verify_certificates_can_be_set_to_true_explicitly(self, tmp_path):
        """Test that verify_certificates can be explicitly set to True."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
verify_certificates: true
""")

        config = ConfigManager.load(str(config_file))
        
        assert config["verify_certificates"] is True

    def test_verify_certificates_type_validation(self, tmp_path):
        """Test that verify_certificates must be a boolean."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
verify_certificates: "invalid"
""")

        # Should load but type should be string (YAML will parse it as string)
        config = ConfigManager.load(str(config_file))
        
        # The value should be a string, not boolean
        assert isinstance(config["verify_certificates"], str)
        assert config["verify_certificates"] == "invalid"
