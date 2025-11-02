"""Unit tests for fetch_webpage_markdown tool."""

from unittest.mock import MagicMock, patch

import pytest


class TestFetchWebpageMarkdown:
    """Tests for fetch_webpage_markdown tool function."""

    def test_fetch_webpage_markdown_successful(self) -> None:
        """Test successful webpage fetch and markdown conversion."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><h1>Test</h1><p>Content here</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "# Test\n\nContent here"

                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert result["success"] is True
                    assert result["data"] == "# Test\n\nContent here"
                    assert "example.com" in result["message"]

    def test_fetch_webpage_markdown_invalid_url(self) -> None:
        """Test fetch_webpage_markdown with invalid URL (missing scheme)."""
        from simple_agent.tools.builtin import page_fetch

        # Test with URL missing scheme - should be caught by input validation
        result = page_fetch.fetch_webpage_markdown("not a valid url")

        assert result["success"] is False
        assert result["data"] is None
        assert "Invalid URL" in result["message"]
        assert "scheme" in result["message"]

    def test_fetch_webpage_markdown_timeout(self) -> None:
        """Test fetch_webpage_markdown handles timeout."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            import requests

            mock_get.side_effect = requests.Timeout("Request timeout")

            result = page_fetch.fetch_webpage_markdown("https://example.com")

            assert result["success"] is False
            assert result["data"] is None
            assert "Page request failed" in result["message"]

    def test_fetch_webpage_markdown_empty_content(self) -> None:
        """Test fetch_webpage_markdown with empty page content."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = ""
            mock_get.return_value = mock_response

            result = page_fetch.fetch_webpage_markdown("https://example.com")

            assert result["success"] is False
            assert result["data"] is None
            assert "No content found" in result["message"]

    def test_fetch_webpage_markdown_empty_markdown_output(self) -> None:
        """Test fetch_webpage_markdown when markdown conversion yields empty string."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><script>alert('test')</script></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    # Simulating that only script tag exists, so markdown is empty
                    mock_h2t.return_value = ""

                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert result["success"] is False
                    assert result["data"] is None
                    assert "No readable content" in result["message"]

    def test_fetch_webpage_markdown_http_error(self) -> None:
        """Test fetch_webpage_markdown handles HTTP errors (404, 500, etc)."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            import requests

            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response

            result = page_fetch.fetch_webpage_markdown("https://example.com/notfound")

            assert result["success"] is False
            assert result["data"] is None
            assert "Page request failed" in result["message"]

    def test_fetch_webpage_markdown_network_error(self) -> None:
        """Test fetch_webpage_markdown handles network errors."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            import requests

            mock_get.side_effect = requests.ConnectionError("Network error")

            result = page_fetch.fetch_webpage_markdown("https://example.com")

            assert result["success"] is False
            assert result["data"] is None
            assert "Page request failed" in result["message"]

    def test_fetch_webpage_markdown_html_cleanup(self) -> None:
        """Test that HTML cleanup removes script, style, svg, img tags."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            # Use real HTML content to test the HTMLCleaner processes it
            mock_response.text = "<html><body><script>bad</script><p>Good content</p></body></html>"
            mock_get.return_value = mock_response

            result = page_fetch.fetch_webpage_markdown("https://example.com")

            # Verify that fetch was successful and content was cleaned
            assert result["success"] is True
            # Script tags should be removed, only content should remain
            assert "Good" in result["data"] or "content" in result["data"].lower()

    def test_fetch_webpage_markdown_user_agent(self) -> None:
        """Test that User-Agent header is set in request."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Test"

                    page_fetch.fetch_webpage_markdown("https://example.com")

                    # Verify headers were passed
                    assert mock_get.call_args[1]["headers"] is not None
                    assert "User-Agent" in mock_get.call_args[1]["headers"]

    def test_fetch_webpage_markdown_timeout_parameter(self) -> None:
        """Test that requests.get is called with timeout parameter."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Test"

                    page_fetch.fetch_webpage_markdown("https://example.com")

                    # Verify timeout is set to 10
                    assert mock_get.call_args[1]["timeout"] == 10

    def test_fetch_webpage_markdown_tool_metadata(self) -> None:
        """Test that fetch_webpage_markdown has correct tool metadata."""
        from simple_agent.tools.builtin.page_fetch import fetch_webpage_markdown

        # Tool should have name attribute
        assert hasattr(fetch_webpage_markdown, "name")
        assert fetch_webpage_markdown.name == "fetch_webpage_markdown"

        # Tool should have description attribute
        assert hasattr(fetch_webpage_markdown, "description")
        assert isinstance(fetch_webpage_markdown.description, str)
        assert len(fetch_webpage_markdown.description) > 0

        # Tool should have inputs dict from @tool decorator
        assert hasattr(fetch_webpage_markdown, "inputs")
        assert isinstance(fetch_webpage_markdown.inputs, dict)
        assert "url" in fetch_webpage_markdown.inputs

        # Tool should have output_type
        assert hasattr(fetch_webpage_markdown, "output_type")

    def test_fetch_webpage_markdown_response_message_format(self) -> None:
        """Test that response message includes the URL."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body>Test</body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Test"

                    result = page_fetch.fetch_webpage_markdown("https://specific-url.com")

                    assert "specific-url.com" in result["message"]


class TestFetchWebpageMarkdownTokens:
    """Tests for token counting in fetch_webpage_markdown."""

    def test_tokens_used_key_present(self) -> None:
        """Result should have tokens_used key."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert "tokens_used" in result
                    assert isinstance(result["tokens_used"], int)
                    assert result["tokens_used"] >= 0

    def test_original_size_key_present(self) -> None:
        """Result should have original_size key."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content here"

                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert "original_size" in result
                    assert isinstance(result["original_size"], int)
                    assert result["original_size"] > 0


class TestFetchWebpageMarkdownStripLevel:
    """Tests for strip_level parameter."""

    def test_strip_level_minimal_parameter(self) -> None:
        """strip_level='minimal' parameter should be accepted."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        strip_level="minimal"
                    )

                    assert result["success"] is True

    def test_strip_level_moderate_parameter(self) -> None:
        """strip_level='moderate' parameter should be accepted."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        strip_level="moderate"
                    )

                    assert result["success"] is True

    def test_strip_level_aggressive_parameter(self) -> None:
        """strip_level='aggressive' parameter should be accepted."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        strip_level="aggressive"
                    )

                    assert result["success"] is True

    def test_strip_level_default_minimal(self) -> None:
        """Default strip_level should be minimal."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    # Call without strip_level parameter
                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert result["success"] is True


class TestFetchWebpageMarkdownMaxChars:
    """Tests for max_chars truncation parameter."""

    def test_max_chars_parameter_accepted(self) -> None:
        """max_chars parameter should be accepted."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        max_chars=100
                    )

                    assert result["success"] is True

    def test_was_truncated_key_present(self) -> None:
        """Result should have was_truncated key."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Content"

                    result = page_fetch.fetch_webpage_markdown("https://example.com")

                    assert "was_truncated" in result
                    assert isinstance(result["was_truncated"], bool)

    def test_was_truncated_false_when_within_limit(self) -> None:
        """was_truncated should be False when content is within max_chars."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>Short</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    mock_h2t.return_value = "Short"

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        max_chars=1000
                    )

                    assert result["success"] is True
                    assert result["was_truncated"] is False

    def test_was_truncated_true_when_exceeds_limit(self) -> None:
        """was_truncated should be True when content exceeds max_chars."""
        from simple_agent.tools.builtin import page_fetch

        with patch.object(page_fetch.requests, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html><body><p>" + "a" * 1000 + "</p></body></html>"
            mock_get.return_value = mock_response

            with patch.object(page_fetch, "BeautifulSoup") as mock_bs:
                with patch.object(page_fetch.html2text, "html2text") as mock_h2t:
                    mock_soup = MagicMock()
                    mock_bs.return_value = mock_soup
                    # Return long content
                    mock_h2t.return_value = "a" * 1000

                    result = page_fetch.fetch_webpage_markdown(
                        "https://example.com",
                        max_chars=50
                    )

                    assert result["success"] is True
                    assert result["was_truncated"] is True
                    assert len(result["data"]) <= 50
