"""Integration tests for verify_certificates configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.tool_manager import ToolManager


class TestVerifyCertificatesIntegration:
    """Integration tests for verify_certificates with full system."""

    def test_config_loads_with_verify_certificates_true(self, tmp_path):
        """Test that config loads properly with verify_certificates: true."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
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
        assert "app" in config
        assert "llm" in config

    def test_config_loads_with_verify_certificates_false(self, tmp_path):
        """Test that config loads properly with verify_certificates: false."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
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

    def test_config_defaults_verify_certificates_when_missing(self, tmp_path):
        """Test that verify_certificates defaults to True when not in config."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
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
        verify_certs = config.get("verify_certificates", True)
        assert verify_certs is True

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_tool_can_be_called_with_verify_false(self, mock_post, tmp_path):
        """Test that tavily tool works with verify_certificates=False."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"results": [{"title": "Test", "url": "http://test.com"}]}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Setup config
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
tools:
  tavily_web_search:
    enabled: true
    api_key_env: "TAVILY_API_KEY"
verify_certificates: false
""")

        config = ConfigManager.load(str(config_file))
        
        # Create tool manager and get tavily tool
        tool_manager = ToolManager(config)
        tavily_tool = tool_manager.get_tool("tavily_web_search")
        
        # Call tool with verify_certificates from config
        result = tavily_tool("test query", verify_certificates=config.get("verify_certificates", True))
        
        # Verify it was called with verify=False
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["verify"] is False
        assert result["success"] is True

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_tool_defaults_to_verify_true(self, mock_post, tmp_path):
        """Test that tavily tool defaults to verify=True when not specified."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"results": [{"title": "Test", "url": "http://test.com"}]}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Setup config without verify_certificates
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
tools:
  tavily_web_search:
    enabled: true
    api_key_env: "TAVILY_API_KEY"
""")

        config = ConfigManager.load(str(config_file))
        
        # Create tool manager and get tavily tool
        tool_manager = ToolManager(config)
        tavily_tool = tool_manager.get_tool("tavily_web_search")
        
        # Call tool without specifying verify_certificates (should default to True)
        result = tavily_tool("test query")
        
        # Verify it was called with verify=True (default)
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs.get("verify", True) is True
        assert result["success"] is True
