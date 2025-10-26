"""
Unit tests for agent tool management (Phase 1.4).

Tests agent tool support in SimpleAgent and AgentManager.
"""

from unittest.mock import MagicMock, patch

import pytest

from simple_agent.core.agent_manager import AgentManager


class TestAgentManagerToolSupport:
    """Test AgentManager tool management."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_with_tools(self, mock_simple_agent: MagicMock) -> None:
        """Test creating agent with tools specified."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent instance
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        # Create tool manager with mock tools
        tool_manager = MagicMock()
        mock_tool1 = MagicMock()
        mock_tool1.name = "add"
        mock_tool2 = MagicMock()
        mock_tool2.name = "multiply"

        tool_manager.get_tool.side_effect = lambda name: {
            "add": mock_tool1,
            "multiply": mock_tool2,
        }[name]

        manager = AgentManager(config)
        manager.tool_manager = tool_manager

        # Create agent with tools
        manager.create_agent("test_agent", tools=["add", "multiply"])

        # Verify SimpleAgent was called with the correct tools
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert "tools" in call_kwargs
        assert call_kwargs["tools"] == [mock_tool1, mock_tool2]

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_add_tool_to_agent(self, mock_simple_agent: MagicMock) -> None:
        """Test adding a tool to an existing agent."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        # Setup tool manager
        tool_manager = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = "add"
        tool_manager.get_tool.return_value = mock_tool

        manager = AgentManager(config)
        manager.tool_manager = tool_manager
        manager.create_agent("test_agent")

        # Add tool to agent
        manager.add_tool_to_agent("test_agent", "add")

        # Verify tool was added
        agent = manager.get_agent("test_agent")
        assert mock_tool in agent.tools

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_remove_tool_from_agent(self, mock_simple_agent: MagicMock) -> None:
        """Test removing a tool from an agent."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent with tool
        mock_agent_instance = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = "add"
        mock_agent_instance.tools = [mock_tool]
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        # Remove tool
        manager.remove_tool_from_agent("test_agent", "add")

        # Verify tool was removed
        agent = manager.get_agent("test_agent")
        assert mock_tool not in agent.tools

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_get_agent_tools(self, mock_simple_agent: MagicMock) -> None:
        """Test getting list of tools for an agent."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent with tools
        mock_agent_instance = MagicMock()
        tool1 = MagicMock()
        tool1.name = "add"
        tool2 = MagicMock()
        tool2.name = "multiply"
        mock_agent_instance.tools = [tool1, tool2]
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        # Get tools
        tools = manager.get_agent_tools("test_agent")

        assert len(tools) == 2
        assert "add" in tools
        assert "multiply" in tools

    def test_add_tool_to_nonexistent_agent(self) -> None:
        """Test adding tool to non-existent agent raises error."""
        config = {}
        manager = AgentManager(config)

        with pytest.raises(KeyError, match="Agent 'missing' not found"):
            manager.add_tool_to_agent("missing", "add")

    def test_remove_tool_from_nonexistent_agent(self) -> None:
        """Test removing tool from non-existent agent raises error."""
        config = {}
        manager = AgentManager(config)

        with pytest.raises(KeyError, match="Agent 'missing' not found"):
            manager.remove_tool_from_agent("missing", "add")

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_add_tool_preserves_builtin_tools(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test that adding a tool preserves SmolAgents built-in tools like final_answer."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent with underlying SmolAgents agent that has final_answer
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []

        # Mock the underlying SmolAgents agent with final_answer tool
        mock_final_answer = MagicMock()
        mock_final_answer.name = "final_answer"
        mock_agent_instance.agent.tools = {"final_answer": mock_final_answer}

        mock_simple_agent.return_value = mock_agent_instance

        # Setup tool manager
        tool_manager = MagicMock()
        mock_add_tool = MagicMock()
        mock_add_tool.name = "add"
        tool_manager.get_tool.return_value = mock_add_tool

        manager = AgentManager(config)
        manager.tool_manager = tool_manager
        manager.create_agent("test_agent")

        # Add tool to agent
        manager.add_tool_to_agent("test_agent", "add")

        # Verify final_answer is still present in agent.agent.tools
        agent = manager.get_agent("test_agent")
        assert "final_answer" in agent.agent.tools
        assert "add" in agent.agent.tools

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_remove_tool_preserves_builtin_tools(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test that removing a tool preserves SmolAgents built-in tools like final_answer."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent with tools
        mock_agent_instance = MagicMock()
        mock_add_tool = MagicMock()
        mock_add_tool.name = "add"
        mock_agent_instance.tools = [mock_add_tool]

        # Mock the underlying SmolAgents agent with final_answer and add
        mock_final_answer = MagicMock()
        mock_final_answer.name = "final_answer"
        mock_agent_instance.agent.tools = {
            "final_answer": mock_final_answer,
            "add": mock_add_tool,
        }

        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        # Remove add tool
        manager.remove_tool_from_agent("test_agent", "add")

        # Verify final_answer is still present, add is removed
        agent = manager.get_agent("test_agent")
        assert "final_answer" in agent.agent.tools
        assert "add" not in agent.agent.tools

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_add_duplicate_tool_prevented(self, mock_simple_agent: MagicMock) -> None:
        """Test that adding a duplicate tool is prevented."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent with a tool already added
        mock_agent_instance = MagicMock()
        mock_add_tool = MagicMock()
        mock_add_tool.name = "add"
        mock_agent_instance.tools = [mock_add_tool]
        mock_agent_instance.agent.tools = {"add": mock_add_tool}

        mock_simple_agent.return_value = mock_agent_instance

        # Setup tool manager
        tool_manager = MagicMock()
        tool_manager.get_tool.return_value = mock_add_tool

        manager = AgentManager(config)
        manager.tool_manager = tool_manager
        manager.create_agent("test_agent")

        # Try to add same tool again - should not add duplicate
        manager.add_tool_to_agent("test_agent", "add")

        # Verify tool list still has only one "add"
        agent = manager.get_agent("test_agent")
        add_count = sum(1 for t in agent.tools if t.name == "add")
        assert add_count == 1
