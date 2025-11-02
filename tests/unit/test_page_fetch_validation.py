"""Unit tests for page_fetch input validation (Issue 8-D)."""

import pytest

from simple_agent.tools.builtin.page_fetch import (
    _validate_url,
    _validate_strip_level,
    _validate_max_chars,
)


class TestURLValidation:
    """Test URL validation."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        error = _validate_url("http://example.com")
        assert error is None

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        error = _validate_url("https://example.com/path")
        assert error is None

    def test_empty_url(self):
        """Test empty URL."""
        error = _validate_url("")
        assert error is not None
        assert "non-empty string" in error

    def test_none_url(self):
        """Test None URL."""
        error = _validate_url(None)
        assert error is not None

    def test_non_string_url(self):
        """Test non-string URL."""
        error = _validate_url(123)
        assert error is not None
        assert "string" in error

    def test_url_too_long(self):
        """Test URL exceeding max length."""
        long_url = "https://example.com/" + "a" * 2100
        error = _validate_url(long_url)
        assert error is not None
        assert "too long" in error

    def test_url_without_scheme(self):
        """Test URL without scheme."""
        error = _validate_url("example.com")
        assert error is not None
        assert "scheme" in error

    def test_url_with_invalid_scheme(self):
        """Test URL with invalid scheme."""
        error = _validate_url("ftp://example.com")
        assert error is not None
        assert "ftp" in error or "Unsupported" in error

    def test_url_without_domain(self):
        """Test URL without domain."""
        error = _validate_url("https://")
        assert error is not None
        assert "domain" in error

    def test_valid_url_with_query_params(self):
        """Test valid URL with query parameters."""
        error = _validate_url("https://example.com/path?key=value&foo=bar")
        assert error is None

    def test_valid_url_with_fragment(self):
        """Test valid URL with fragment."""
        error = _validate_url("https://example.com/path#section")
        assert error is None


class TestStripLevelValidation:
    """Test strip level parameter validation."""

    def test_valid_minimal(self):
        """Test 'minimal' strip level."""
        error = _validate_strip_level("minimal")
        assert error is None

    def test_valid_moderate(self):
        """Test 'moderate' strip level."""
        error = _validate_strip_level("moderate")
        assert error is None

    def test_valid_aggressive(self):
        """Test 'aggressive' strip level."""
        error = _validate_strip_level("aggressive")
        assert error is None

    def test_invalid_strip_level(self):
        """Test invalid strip level."""
        error = _validate_strip_level("invalid")
        assert error is not None
        assert "minimal" in error

    def test_case_sensitive_strip_level(self):
        """Test that strip level is case-sensitive."""
        error = _validate_strip_level("Minimal")
        assert error is not None


class TestMaxCharsValidation:
    """Test max_chars parameter validation."""

    def test_none_max_chars(self):
        """Test None is valid for max_chars."""
        error = _validate_max_chars(None)
        assert error is None

    def test_valid_positive_max_chars(self):
        """Test positive integer."""
        error = _validate_max_chars(1000)
        assert error is None

    def test_max_chars_one(self):
        """Test max_chars = 1."""
        error = _validate_max_chars(1)
        assert error is None

    def test_max_chars_large_valid(self):
        """Test large but valid max_chars."""
        error = _validate_max_chars(10_000_000)
        assert error is None

    def test_max_chars_zero(self):
        """Test max_chars = 0."""
        error = _validate_max_chars(0)
        assert error is not None
        assert "greater than 0" in error

    def test_max_chars_negative(self):
        """Test negative max_chars."""
        error = _validate_max_chars(-100)
        assert error is not None
        assert "greater than 0" in error

    def test_max_chars_too_large(self):
        """Test max_chars exceeding max limit."""
        error = _validate_max_chars(10_000_001)
        assert error is not None
        assert "too large" in error

    def test_max_chars_non_integer(self):
        """Test non-integer max_chars."""
        error = _validate_max_chars("1000")
        assert error is not None
        assert "integer" in error

    def test_max_chars_float(self):
        """Test float max_chars."""
        error = _validate_max_chars(1000.5)
        assert error is not None
        assert "integer" in error


class TestFetchWebpageValidation:
    """Test fetch_webpage_markdown with invalid inputs."""

    def test_fetch_with_invalid_url(self):
        """Test fetch with invalid URL returns error."""
        from simple_agent.tools.builtin.page_fetch import fetch_webpage_markdown

        result = fetch_webpage_markdown(url="invalid url", strip_level="minimal")

        assert result["success"] is False
        assert result["data"] is None
        assert "Invalid URL" in result["message"]

    def test_fetch_with_invalid_strip_level(self):
        """Test fetch with invalid strip level returns error."""
        from simple_agent.tools.builtin.page_fetch import fetch_webpage_markdown

        result = fetch_webpage_markdown(
            url="https://example.com",
            strip_level="invalid_level",
        )

        assert result["success"] is False
        assert "Invalid parameter" in result["message"]

    def test_fetch_with_invalid_max_chars(self):
        """Test fetch with invalid max_chars returns error."""
        from simple_agent.tools.builtin.page_fetch import fetch_webpage_markdown

        result = fetch_webpage_markdown(
            url="https://example.com",
            max_chars=0,
        )

        assert result["success"] is False
        assert "Invalid parameter" in result["message"]
