"""Tavily web search tool for Simple Agent."""

import os
import requests
from smolagents import tool


@tool
def tavily_web_search(query: str) -> dict:
    """Search the web using Tavily API.

    Use this when you need quick search results about current topics.
    Returns structured search results with sources and snippets.

    Args:
        query: Search query string

    Returns:
        dict with keys: success (bool), data (API response dict), message (str)
    """
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
        response = requests.post(url, headers=headers, json=request_params, timeout=10)
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
