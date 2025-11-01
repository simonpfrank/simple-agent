"""Unit tests for tavily_web_search tool."""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestTavilyWebSearch:
    """Tests for tavily_web_search tool function."""

    def test_tavily_web_search_successful(self) -> None:
        """Test successful web search with mocked API response."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                # Mock successful response
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "results": [{"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}]
                }
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("test query")

                assert result["success"] is True
                assert result["data"] == {
                    "results": [{"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}]
                }
                assert "test query" in result["message"]

    def test_tavily_web_search_missing_api_key(self) -> None:
        """Test tavily_web_search with missing TAVILY_API_KEY."""
        with patch.dict(os.environ, {}, clear=True):
            from simple_agent.tools.builtin.tavily_search import tavily_web_search

            result = tavily_web_search("test query")

            assert result["success"] is False
            assert result["data"] is None
            assert "TAVILY_API_KEY" in result["message"]

    def test_tavily_web_search_network_error(self) -> None:
        """Test tavily_web_search handles network errors gracefully."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                # Mock network error (requests.ConnectionError is a RequestException)
                import requests

                mock_post.side_effect = requests.ConnectionError("Network error")

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("test query")

                assert result["success"] is False
                assert result["data"] is None
                assert "Tavily search failed" in result["message"]

    def test_tavily_web_search_timeout_error(self) -> None:
        """Test tavily_web_search handles timeout errors."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                # Mock timeout error
                import requests

                mock_post.side_effect = requests.Timeout("Request timeout")

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("test query")

                assert result["success"] is False
                assert result["data"] is None
                assert "Tavily search failed" in result["message"]

    def test_tavily_web_search_http_error(self) -> None:
        """Test tavily_web_search handles HTTP errors (401, 500, etc)."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "invalid_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                # Mock HTTP error (401 Unauthorized)
                import requests

                mock_response = MagicMock()
                mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("test query")

                assert result["success"] is False
                assert result["data"] is None
                assert "Tavily search failed" in result["message"]

    def test_tavily_web_search_empty_query(self) -> None:
        """Test tavily_web_search with empty query string."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                # Mock response for empty query
                mock_response = MagicMock()
                mock_response.json.return_value = {"results": []}
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("")

                assert result["success"] is True
                assert result["data"] == {"results": []}

    def test_tavily_web_search_api_request_format(self) -> None:
        """Test that API request is formatted correctly."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"results": []}
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                tavily_web_search("quantum computing")

                # Verify API endpoint
                assert mock_post.call_args[0][0] == "https://api.tavily.com/search"

                # Verify headers
                assert "Authorization" in mock_post.call_args[1]["headers"]
                assert mock_post.call_args[1]["headers"]["Authorization"] == "Bearer test_key"
                assert mock_post.call_args[1]["headers"]["Content-Type"] == "application/json"

                # Verify payload
                assert mock_post.call_args[1]["json"] == {"query": "quantum computing"}

    def test_tavily_web_search_tool_metadata(self) -> None:
        """Test that tavily_web_search has correct tool metadata."""
        from simple_agent.tools.builtin.tavily_search import tavily_web_search

        # Tool should have name attribute
        assert hasattr(tavily_web_search, "name")
        assert tavily_web_search.name == "tavily_web_search"

        # Tool should have description attribute
        assert hasattr(tavily_web_search, "description")
        assert isinstance(tavily_web_search.description, str)
        assert len(tavily_web_search.description) > 0

        # Tool should have inputs dict from @tool decorator
        assert hasattr(tavily_web_search, "inputs")
        assert isinstance(tavily_web_search.inputs, dict)
        assert "query" in tavily_web_search.inputs

        # Tool should have output_type
        assert hasattr(tavily_web_search, "output_type")

    def test_tavily_web_search_response_message_format(self) -> None:
        """Test that response message includes the query."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"results": []}
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                result = tavily_web_search("specific query")

                assert "specific query" in result["message"]

    def test_tavily_web_search_timeout_parameter(self) -> None:
        """Test that requests.post is called with timeout parameter."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch("simple_agent.tools.builtin.tavily_search.requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"results": []}
                mock_post.return_value = mock_response

                from simple_agent.tools.builtin.tavily_search import tavily_web_search

                tavily_web_search("test")

                # Verify timeout is set
                assert mock_post.call_args[1]["timeout"] == 10
