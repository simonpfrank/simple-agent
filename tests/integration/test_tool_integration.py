"""
Integration tests for Phase 1.4 Tool Management.

Tests the full tool management workflow with real components (no mocks).
"""

import pytest

from simple_agent.core.agent_manager import AgentManager
from simple_agent.core.tool_manager import ToolManager


class TestToolManagementIntegration:
    """Test tool management end-to-end workflow."""

    @pytest.fixture
    def config(self) -> dict:
        """Test configuration."""
        return {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

    @pytest.fixture
    def tool_manager(self) -> ToolManager:
        """Create ToolManager with built-in tools."""
        return ToolManager(auto_load_builtin=True)

    @pytest.fixture
    def agent_manager(self, config: dict, tool_manager: ToolManager) -> AgentManager:
        """Create AgentManager with ToolManager attached."""
        manager = AgentManager(config)
        manager.tool_manager = tool_manager
        return manager

    def test_tool_manager_loads_builtin_tools(self, tool_manager: ToolManager) -> None:
        """Test that ToolManager loads built-in calculator tools."""
        tools = tool_manager.list_tools()

        # Should have at least add, subtract, multiply, divide
        assert len(tools) >= 4
        assert "add" in tools
        assert "subtract" in tools
        assert "multiply" in tools
        assert "divide" in tools

    def test_create_agent_with_tools(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test creating an agent with tools attached."""
        # Create agent with specific tools
        agent = agent_manager.create_agent(name="math_agent", tools=["add", "multiply"])

        # Verify agent has tools
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "add"
        assert agent.tools[1].name == "multiply"

        # Verify tools are accessible via AgentManager
        tool_names = agent_manager.get_agent_tools("math_agent")
        assert tool_names == ["add", "multiply"]

    def test_add_tool_to_existing_agent(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test adding a tool to an existing agent."""
        # Create agent without tools
        agent = agent_manager.create_agent(name="test_agent")
        assert len(agent.tools) == 0

        # Add a tool
        agent_manager.add_tool_to_agent("test_agent", "add")

        # Verify tool was added
        agent = agent_manager.get_agent("test_agent")
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "add"

        # Add another tool
        agent_manager.add_tool_to_agent("test_agent", "subtract")
        agent = agent_manager.get_agent("test_agent")
        assert len(agent.tools) == 2

    def test_remove_tool_from_agent(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test removing a tool from an agent."""
        # Create agent with tools
        agent = agent_manager.create_agent(
            name="test_agent", tools=["add", "subtract", "multiply"]
        )
        assert len(agent.tools) == 3

        # Remove a tool
        agent_manager.remove_tool_from_agent("test_agent", "subtract")

        # Verify tool was removed
        agent = agent_manager.get_agent("test_agent")
        assert len(agent.tools) == 2
        tool_names = [t.name for t in agent.tools]
        assert "add" in tool_names
        assert "multiply" in tool_names
        assert "subtract" not in tool_names

    def test_get_agent_tools_returns_names(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test getting tool names for an agent."""
        # Create agent with tools
        agent_manager.create_agent(name="test_agent", tools=["add", "multiply"])

        # Get tool names
        tool_names = agent_manager.get_agent_tools("test_agent")

        assert isinstance(tool_names, list)
        assert len(tool_names) == 2
        assert "add" in tool_names
        assert "multiply" in tool_names

    def test_tool_persistence_across_operations(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test that tools persist correctly across multiple operations."""
        # Create agent with initial tools
        agent_manager.create_agent(name="persistent_agent", tools=["add"])

        # Add more tools
        agent_manager.add_tool_to_agent("persistent_agent", "subtract")
        agent_manager.add_tool_to_agent("persistent_agent", "multiply")

        # Verify all tools present
        tool_names = agent_manager.get_agent_tools("persistent_agent")
        assert len(tool_names) == 3

        # Remove one tool
        agent_manager.remove_tool_from_agent("persistent_agent", "subtract")

        # Verify correct tools remain
        tool_names = agent_manager.get_agent_tools("persistent_agent")
        assert len(tool_names) == 2
        assert "add" in tool_names
        assert "multiply" in tool_names
        assert "subtract" not in tool_names

    def test_multiple_agents_with_different_tools(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test that multiple agents can have different tool sets."""
        # Create agents with different tools
        agent_manager.create_agent(name="agent1", tools=["add", "subtract"])
        agent_manager.create_agent(name="agent2", tools=["multiply", "divide"])

        # Verify each agent has correct tools
        agent1_tools = agent_manager.get_agent_tools("agent1")
        agent2_tools = agent_manager.get_agent_tools("agent2")

        assert set(agent1_tools) == {"add", "subtract"}
        assert set(agent2_tools) == {"multiply", "divide"}

        # Modify one agent's tools
        agent_manager.add_tool_to_agent("agent1", "multiply")

        # Verify only agent1 was affected
        agent1_tools = agent_manager.get_agent_tools("agent1")
        agent2_tools = agent_manager.get_agent_tools("agent2")

        assert "multiply" in agent1_tools
        assert len(agent1_tools) == 3
        assert len(agent2_tools) == 2

    def test_tool_info_retrieval(self, tool_manager: ToolManager) -> None:
        """Test retrieving detailed tool information."""
        # Get info for add tool
        info = tool_manager.get_tool_info("add")

        # Verify info structure
        assert "name" in info
        assert "description" in info
        assert "inputs" in info
        assert "output_type" in info

        assert info["name"] == "add"
        assert isinstance(info["description"], str)
        assert len(info["description"]) > 0

    def test_error_handling_nonexistent_tool(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test error handling when using nonexistent tool."""
        agent_manager.create_agent(name="test_agent")

        # Try to add nonexistent tool
        with pytest.raises(KeyError, match="Tool 'nonexistent' not found"):
            agent_manager.add_tool_to_agent("test_agent", "nonexistent")

    def test_error_handling_nonexistent_agent(
        self, agent_manager: AgentManager, tool_manager: ToolManager
    ) -> None:
        """Test error handling when modifying nonexistent agent."""
        # Try to add tool to nonexistent agent
        with pytest.raises(KeyError, match="Agent 'nonexistent' not found"):
            agent_manager.add_tool_to_agent("nonexistent", "add")

        # Try to remove tool from nonexistent agent
        with pytest.raises(KeyError, match="Agent 'nonexistent' not found"):
            agent_manager.remove_tool_from_agent("nonexistent", "add")

        # Try to get tools from nonexistent agent
        with pytest.raises(KeyError, match="Agent 'nonexistent' not found"):
            agent_manager.get_agent_tools("nonexistent")
