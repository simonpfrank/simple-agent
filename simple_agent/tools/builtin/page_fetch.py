"""Webpage fetching and markdown conversion tool for Simple Agent."""

from random import choice

import requests
from bs4 import BeautifulSoup
from smolagents import tool

import html2text

from simple_agent.tools.helpers import HTMLCleaner
from simple_agent.tools.helpers.token_counter import estimate_tokens


def _get_random_user_agent() -> str:
    """Get a random user agent string."""
    user_agents = [
        # Google Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
        # Mozilla Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
        # Microsoft Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36 Edg/117.0.2045.43",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36 Edg/117.0.2045.43",
    ]
    return choice(user_agents)


@tool
def fetch_webpage_markdown(
    url: str,
    strip_level: str = "minimal",
    max_chars: int = None
) -> dict:
    """Fetch a webpage and convert to markdown with token management.

    Use this when you need to read the full content of a specific webpage.
    Returns the page content as clean markdown text with token usage tracking.

    Args:
        url: URL to fetch
        strip_level: HTML cleaning level - "minimal", "moderate", or "aggressive"
        max_chars: Maximum characters to return (None = no limit)

    Returns:
        dict with keys:
            - success (bool): Whether fetch was successful
            - data (str): Markdown content
            - tokens_used (int): Estimated tokens in returned content
            - original_size (int): Character count of cleaned markdown
            - was_truncated (bool): Whether content was truncated by max_chars
            - message (str): Status message
    """
    headers = {"User-Agent": _get_random_user_agent()}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text

        if not html.strip():
            return {
                "success": False,
                "data": None,
                "tokens_used": 0,
                "original_size": 0,
                "was_truncated": False,
                "message": f"No content found at {url}.",
            }

        # Use HTMLCleaner for flexible HTML cleaning
        cleaner = HTMLCleaner(strip_level=strip_level)
        markdown, stats = cleaner.clean(html)

        if not markdown.strip():
            return {
                "success": False,
                "data": None,
                "tokens_used": 0,
                "original_size": 0,
                "was_truncated": False,
                "message": f"No readable content at {url}.",
            }

        # Handle truncation if max_chars is specified
        was_truncated = False
        if max_chars and len(markdown) > max_chars:
            markdown = markdown[:max_chars]
            was_truncated = True

        # Count tokens in final content
        tokens_used = estimate_tokens(markdown)
        original_size = len(markdown)

        return {
            "success": True,
            "data": markdown,
            "tokens_used": tokens_used,
            "original_size": original_size,
            "was_truncated": was_truncated,
            "message": f"Fetched and converted {url} to markdown.",
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "tokens_used": 0,
            "original_size": 0,
            "was_truncated": False,
            "message": f"Page request failed: {str(e)}",
        }
