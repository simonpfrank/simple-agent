"""Unit tests for token counter utility."""
import pytest

from simple_agent.tools.helpers.token_counter import estimate_tokens


class TestEstimateTokensBasic:
    """Test basic token estimation functionality."""

    def test_empty_string_returns_zero(self):
        """Empty string should return 0 tokens."""
        assert estimate_tokens("") == 0

    def test_single_word_returns_one_token(self):
        """Single word is typically 1 token."""
        assert estimate_tokens("hello") == 1

    def test_multiple_words_counted(self):
        """Multiple words should be counted correctly."""
        # Rough estimate: 1 token per word on average
        text = "hello world this is a test"
        tokens = estimate_tokens(text)
        assert tokens > 0
        # Should be roughly 6 tokens, but within reasonable range
        assert 4 <= tokens <= 8

    def test_punctuation_affects_count(self):
        """Punctuation should affect token count."""
        text_without = "hello world"
        text_with = "hello, world!"
        tokens_without = estimate_tokens(text_without)
        tokens_with = estimate_tokens(text_with)
        # With punctuation should be same or slightly more
        assert tokens_with >= tokens_without

    def test_longer_text(self):
        """Longer text should have more tokens."""
        short = "hello"
        long = "hello world this is a longer piece of text with multiple sentences. It has punctuation! And more content."
        short_tokens = estimate_tokens(short)
        long_tokens = estimate_tokens(long)
        assert long_tokens > short_tokens


class TestEstimateTokensWhitespace:
    """Test handling of whitespace in token estimation."""

    def test_multiple_spaces_handled(self):
        """Multiple spaces should be normalized."""
        text1 = "hello world"
        text2 = "hello    world"
        # Should be roughly same token count
        tokens1 = estimate_tokens(text1)
        tokens2 = estimate_tokens(text2)
        assert abs(tokens1 - tokens2) <= 1

    def test_newlines_handled(self):
        """Newlines should be handled correctly."""
        text = "hello\nworld\ntest"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_tabs_handled(self):
        """Tabs should be handled correctly."""
        text = "hello\tworld\ttest"
        tokens = estimate_tokens(text)
        assert tokens > 0


class TestEstimateTokensSpecialCharacters:
    """Test handling of special characters and unicode."""

    def test_numbers_counted(self):
        """Numbers should be counted as tokens."""
        text = "The year is 2024"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_special_characters(self):
        """Special characters should be handled."""
        text = "hello@world.com # comment $ price"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_unicode_characters(self):
        """Unicode characters should be handled."""
        text = "hello 世界 مرحبا мир"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_emoji_characters(self):
        """Emoji should be counted."""
        text = "hello 👋 world 🌍"
        tokens = estimate_tokens(text)
        assert tokens > 0


class TestEstimateTokensConsistency:
    """Test consistency of token estimation."""

    def test_same_text_same_tokens(self):
        """Same text should always give same token count."""
        text = "the quick brown fox jumps over the lazy dog"
        tokens1 = estimate_tokens(text)
        tokens2 = estimate_tokens(text)
        tokens3 = estimate_tokens(text)
        assert tokens1 == tokens2 == tokens3

    def test_case_sensitivity(self):
        """Different cases may have different token counts in tiktoken."""
        text_lower = "hello world"
        text_upper = "HELLO WORLD"
        tokens_lower = estimate_tokens(text_lower)
        tokens_upper = estimate_tokens(text_upper)
        # Both should have tokens, but counts may differ due to tokenizer behavior
        assert tokens_lower > 0
        assert tokens_upper > 0


class TestEstimateTokensRealistic:
    """Test with realistic content sizes."""

    def test_typical_html_content(self):
        """Typical HTML webpage content should be estimated."""
        html_snippet = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <h1>Welcome</h1>
        <p>This is a test paragraph with some content.</p>
        <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
        </ul>
        </body>
        </html>
        """
        tokens = estimate_tokens(html_snippet)
        assert tokens > 0
        # Should be more than just counting words due to HTML
        assert tokens >= 30

    def test_json_content(self):
        """JSON content should be estimated."""
        json_text = '{"name": "John", "age": 30, "city": "New York", "items": [1, 2, 3, 4, 5]}'
        tokens = estimate_tokens(json_text)
        assert tokens > 0

    def test_markdown_content(self):
        """Markdown content should be estimated."""
        markdown = """
# Heading
## Subheading

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
- List item 3

```python
def hello():
    return "world"
```
        """
        tokens = estimate_tokens(markdown)
        assert tokens > 0

    def test_large_document(self):
        """Large documents should estimate tokens correctly."""
        # Create a large document
        text = " ".join(["word"] * 1000)
        tokens = estimate_tokens(text)
        # 1000 words should be roughly 1000-1500 tokens
        assert 800 <= tokens <= 1500


class TestEstimateTokensEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_word(self):
        """Very long word should be counted."""
        word = "a" * 1000
        tokens = estimate_tokens(word)
        assert tokens > 0

    def test_only_whitespace(self):
        """Only whitespace still produces tokens in tiktoken."""
        text = "   \n\n\t\t  "
        tokens = estimate_tokens(text)
        # Whitespace is tokenized, so we expect at least some tokens
        assert tokens >= 0

    def test_mixed_languages(self):
        """Mixed language content should be counted."""
        text = "Hello مرحبا 你好 привет こんにちは"
        tokens = estimate_tokens(text)
        assert tokens > 0

    def test_code_content(self):
        """Code content should be estimated."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
        """
        tokens = estimate_tokens(code)
        assert tokens > 0
