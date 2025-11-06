"""Unit tests for tavily_search verify_certificates support - TDD approach."""

import os
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests


class TestTavilyVerifyCertificates:
    """Test that tavily_search respects verify_certificates setting."""

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_uses_verify_true_by_default(self, mock_post):
        """Test that tavily uses verify=True by default."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search
        from simple_agent.core.runtime_config import _reset_config
        
        # Ensure no config set (will use default)
        _reset_config()
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call without config (should default to True)
        tavily_web_search("test query")

        # Should have been called with verify=True
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs.get("verify", True) is True

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_respects_verify_false_from_config(self, mock_post):
        """Test that tavily respects verify=False from runtime config."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search
        from simple_agent.core.runtime_config import set_config
        
        # Set config with verify_certificates=False
        set_config({"verify_certificates": False})
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call without explicit parameter (should use config)
        tavily_web_search("test query")

        # Should have been called with verify=False from config
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["verify"] is False

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_respects_verify_true_from_config(self, mock_post):
        """Test that tavily respects verify=True from runtime config."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search
        from simple_agent.core.runtime_config import set_config
        
        # Set config with verify_certificates=True
        set_config({"verify_certificates": True})
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call without explicit parameter (should use config)
        tavily_web_search("test query")

        # Should have been called with verify=True from config
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["verify"] is True

    @patch("simple_agent.tools.builtin.tavily_search.requests.post")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_handles_ssl_errors_gracefully(self, mock_post):
        """Test that tavily handles SSL errors gracefully."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search
        
        # Simulate SSL error
        mock_post.side_effect = requests.exceptions.SSLError("Certificate verification failed")

        result = tavily_web_search("test query")

        assert result["success"] is False
        assert "Certificate verification failed" in result["message"]
        assert result["data"] is None

    @patch.dict(os.environ, {}, clear=True)
    def test_tavily_requires_api_key(self):
        """Test that tavily requires TAVILY_API_KEY to be set."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search
        
        result = tavily_web_search("test query")

        assert result["success"] is False
        assert "TAVILY_API_KEY must be set" in result["message"]
        assert result["data"] is None
