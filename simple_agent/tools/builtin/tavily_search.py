"""Tavily web search tool for Simple Agent."""

import os
import requests
from smolagents import tool
import logging


def _get_verify_certificates() -> bool:
    """Get verify_certificates setting from runtime config.

    Returns:
        bool: True if certificates should be verified (default), False otherwise
    """
    try:
        from simple_agent.core.runtime_config import get_config_value

        return get_config_value("verify_certificates", default=True)
    except ImportError:
        # Fallback if runtime_config not available
        return True


@tool
def tavily_web_search(query: str, verify_certificates: bool = None) -> dict:
    """Search the web using Tavily API.

    Use this when you need quick search results about current topics.
    Returns structured search results with sources and snippets.

    Args:
        query: Search query string
        verify_certificates: Whether to verify SSL certificates.
                           If None (default), reads from config. Explicit values override config.

    Returns:
        dict with keys: success (bool), data (API response dict), message (str)
    """
    # Get verify_certificates from config if not explicitly provided
    if verify_certificates is None:
        verify_certificates = _get_verify_certificates()

    print(f"Verify certs:{verify_certificates}")

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "success": False,
            "data": None,
            "message": "TAVILY_API_KEY must be set in environment variables.",
        }

    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request_params = {"query": query}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=request_params,
            timeout=10,
            verify=verify_certificates,
        )
        response.raise_for_status()
        api_result = response.json()
        return {
            "success": True,
            "data": api_result,
            "message": f"Tavily search completed for '{query}'",
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "data": None,
            "message": f"Tavily search failed: {str(e)}",
        }
