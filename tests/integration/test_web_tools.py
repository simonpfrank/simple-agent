"""Integration tests for web tools (tavily_web_search and fetch_webpage_markdown)."""

from unittest.mock import MagicMock, patch

import pytest

from simple_agent.core.agent_manager import AgentManager
from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.tool_manager import ToolManager


class TestWebToolsIntegration:
    """Integration tests for web tools with ToolManager and AgentManager."""

    def test_toolmanager_loads_web_tools_with_auto_load(self) -> None:
        """Test that ToolManager auto-loads web tools when auto_load_builtin=True."""
        manager = ToolManager(auto_load_builtin=True)

        # Verify both web tools are loaded
        assert manager.has_tool("tavily_web_search")
        assert manager.has_tool("fetch_webpage_markdown")

        # Verify calculator tools are still loaded
        assert manager.has_tool("add")
        assert manager.has_tool("subtract")
        assert manager.has_tool("multiply")
        assert manager.has_tool("divide")

        # Should have 6 tools total
        tools = manager.list_tools()
        assert len(tools) == 6

    def test_tavily_web_search_tool_metadata(self) -> None:
        """Test that tavily_web_search tool has correct metadata."""
        manager = ToolManager(auto_load_builtin=True)
        info = manager.get_tool_info("tavily_web_search")

        assert info["name"] == "tavily_web_search"
        assert "search" in info["description"].lower()
        assert isinstance(info["inputs"], dict)
        assert "query" in info["inputs"]
        assert info["output_type"] is not None

    def test_fetch_webpage_markdown_tool_metadata(self) -> None:
        """Test that fetch_webpage_markdown tool has correct metadata."""
        manager = ToolManager(auto_load_builtin=True)
        info = manager.get_tool_info("fetch_webpage_markdown")

        assert info["name"] == "fetch_webpage_markdown"
        assert "fetch" in info["description"].lower() or "webpage" in info["description"].lower()
        assert isinstance(info["inputs"], dict)
        assert "url" in info["inputs"]
        assert info["output_type"] is not None

    def test_create_agent_with_tavily_web_search(self) -> None:
        """Test creating an agent with tavily_web_search tool."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with tavily_web_search tool
        agent_manager.create_agent(
            name="researcher",
            role="Research specialist",
            tools=["tavily_web_search"],
        )

        agent = agent_manager.get_agent("researcher")
        assert agent is not None

        # Verify tool is registered with agent
        agent_tools = agent_manager.get_agent_tools("researcher")
        assert "tavily_web_search" in agent_tools

    def test_create_agent_with_fetch_webpage_markdown(self) -> None:
        """Test creating an agent with fetch_webpage_markdown tool."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with fetch_webpage_markdown tool
        agent_manager.create_agent(
            name="reader",
            role="Page reader",
            tools=["fetch_webpage_markdown"],
        )

        agent = agent_manager.get_agent("reader")
        assert agent is not None

        # Verify tool is registered with agent
        agent_tools = agent_manager.get_agent_tools("reader")
        assert "fetch_webpage_markdown" in agent_tools

    def test_create_agent_with_both_web_tools(self) -> None:
        """Test creating an agent with both web tools."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with both tools
        agent_manager.create_agent(
            name="web_assistant",
            role="Web assistant with search and fetch capabilities",
            tools=["tavily_web_search", "fetch_webpage_markdown"],
        )

        agent = agent_manager.get_agent("web_assistant")
        assert agent is not None

        # Verify both tools are registered
        agent_tools = agent_manager.get_agent_tools("web_assistant")
        assert "tavily_web_search" in agent_tools
        assert "fetch_webpage_markdown" in agent_tools
        assert len(agent_tools) == 2

    def test_add_web_tools_to_existing_agent(self) -> None:
        """Test adding web tools to an existing agent."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent without tools
        agent_manager.create_agent(
            name="assistant",
            role="Helper",
        )

        # Add web tools
        agent_manager.add_tool_to_agent("assistant", "tavily_web_search")
        agent_manager.add_tool_to_agent("assistant", "fetch_webpage_markdown")

        # Verify tools are added
        agent_tools = agent_manager.get_agent_tools("assistant")
        assert "tavily_web_search" in agent_tools
        assert "fetch_webpage_markdown" in agent_tools

    def test_remove_web_tool_from_agent(self) -> None:
        """Test removing a web tool from an agent."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with both web tools
        agent_manager.create_agent(
            name="researcher",
            role="Researcher",
            tools=["tavily_web_search", "fetch_webpage_markdown"],
        )

        # Remove one tool
        agent_manager.remove_tool_from_agent("researcher", "fetch_webpage_markdown")

        # Verify only tavily_web_search remains
        agent_tools = agent_manager.get_agent_tools("researcher")
        assert "tavily_web_search" in agent_tools
        assert "fetch_webpage_markdown" not in agent_tools

    def test_web_tools_do_not_break_existing_tools(self) -> None:
        """Test that web tools don't interfere with existing calculator tools."""
        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with calculator and web tools
        agent_manager.create_agent(
            name="calculator_researcher",
            role="Calculator and researcher",
            tools=["add", "multiply", "tavily_web_search", "fetch_webpage_markdown"],
        )

        agent_tools = agent_manager.get_agent_tools("calculator_researcher")

        # Verify all tools are registered
        assert "add" in agent_tools
        assert "multiply" in agent_tools
        assert "tavily_web_search" in agent_tools
        assert "fetch_webpage_markdown" in agent_tools
        assert len(agent_tools) == 4

    def test_tool_info_for_web_tools(self) -> None:
        """Test retrieving tool info for web tools."""
        manager = ToolManager(auto_load_builtin=True)

        # Get info for tavily_web_search
        tavily_info = manager.get_tool_info("tavily_web_search")
        assert tavily_info["name"] == "tavily_web_search"
        assert tavily_info["inputs"]["query"]["type"] == "string"

        # Get info for fetch_webpage_markdown
        fetch_info = manager.get_tool_info("fetch_webpage_markdown")
        assert fetch_info["name"] == "fetch_webpage_markdown"
        assert fetch_info["inputs"]["url"]["type"] == "string"

    def test_web_tools_callable_through_smolagents_interface(self) -> None:
        """Test that web tools are properly callable (SmolAgents Tool interface)."""
        manager = ToolManager(auto_load_builtin=True)

        # Get the tools
        tavily = manager.get_tool("tavily_web_search")
        fetch = manager.get_tool("fetch_webpage_markdown")

        # Verify they have the Tool interface methods/attributes
        assert hasattr(tavily, "forward")
        assert hasattr(tavily, "name")
        assert hasattr(tavily, "description")
        assert hasattr(tavily, "inputs")
        assert hasattr(tavily, "output_type")

        assert hasattr(fetch, "forward")
        assert hasattr(fetch, "name")
        assert hasattr(fetch, "description")
        assert hasattr(fetch, "inputs")
        assert hasattr(fetch, "output_type")

    def test_web_tools_with_mocked_api_calls(self) -> None:
        """Test web tools with mocked API calls in agent context."""
        from simple_agent.tools.builtin import tavily_search, page_fetch

        config = ConfigManager.get_defaults()
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = ToolManager(auto_load_builtin=True)

        # Create agent with web tools
        agent_manager.create_agent(
            name="web_agent",
            role="Web researcher",
            tools=["tavily_web_search", "fetch_webpage_markdown"],
        )

        # Mock API call
        import os

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"}):
            with patch.object(tavily_search.requests, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"results": [{"title": "Test"}]}
                mock_post.return_value = mock_response

                # Get the tool and verify it works
                tavily_tool = agent_manager.tool_manager.get_tool("tavily_web_search")
                result = tavily_tool("test query")

                assert result["success"] is True
                assert result["data"]["results"][0]["title"] == "Test"
