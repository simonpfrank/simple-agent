"""Tests for AgentTool wrapper that exposes agents as callable tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.orchestration.agent_tool import AgentTool


class TestAgentTool:
    """AgentTool wraps agents as tools for orchestrators."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock SimpleAgent."""
        agent = MagicMock(spec=SimpleAgent)
        agent.name = "test_agent"
        agent.run = MagicMock(return_value="Test output from agent")
        return agent

    def test_agent_tool_creation(self, mock_agent):
        """AgentTool can be created from agent with name/description."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        assert tool.name == "test_tool"
        assert tool.agent == mock_agent
        assert tool.description == "Test tool description"
        assert tool.call_history == []

    def test_agent_tool_call_executes_agent(self, mock_agent):
        """Calling AgentTool's forward method executes wrapped agent."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        result = tool.forward("Test prompt")

        # Verify agent was called
        mock_agent.run.assert_called_once_with("Test prompt")

        # Verify result is a string (what forward returns)
        assert isinstance(result, str)
        assert result == "Test output from agent"

    def test_agent_tool_output_format(self, mock_agent):
        """AgentTool forward method returns string output."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        result = tool.forward("Test prompt")

        # forward() returns string, not dict
        assert isinstance(result, str)
        assert result == "Test output from agent"

    def test_agent_tool_metadata_tracking(self, mock_agent):
        """AgentTool tracks execution metadata in call_history."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        result = tool.forward("Test prompt")

        # Check call_history contains metadata
        assert len(tool.call_history) == 1
        metadata = tool.call_history[0]["metadata"]

        # Check metadata fields
        assert "agent_name" in metadata
        assert "execution_time" in metadata
        assert metadata["agent_name"] == "test_agent"
        assert metadata["execution_time"] >= 0
        assert isinstance(metadata["execution_time"], float)

    def test_agent_tool_history_tracking(self, mock_agent):
        """AgentTool maintains call history."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        # Make multiple forward calls
        result1 = tool.forward("First prompt")
        result2 = tool.forward("Second prompt")

        # Check history
        assert len(tool.call_history) == 2
        assert tool.call_history[0]["output"] == "Test output from agent"
        assert tool.call_history[1]["output"] == "Test output from agent"

    def test_agent_tool_failure_handling(self, mock_agent):
        """AgentTool handles agent failures gracefully."""
        # Make agent raise an exception
        mock_agent.run.side_effect = RuntimeError("Agent failed")

        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        result = tool.forward("Test prompt")

        # Check failure handling - forward returns error message as string
        assert isinstance(result, str)
        assert "Error" in result
        # Check call_history shows failure
        assert len(tool.call_history) == 1
        assert tool.call_history[0]["status"] == "failure"

    def test_agent_tool_repr(self, mock_agent):
        """AgentTool has readable string representation."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description"
        )

        repr_str = repr(tool)

        assert "AgentTool" in repr_str
        assert "test_tool" in repr_str
        assert "test_agent" in repr_str

    def test_agent_tool_expected_output_format(self, mock_agent):
        """AgentTool accepts expected_output_format parameter."""
        tool = AgentTool(
            name="test_tool",
            agent=mock_agent,
            description="Test tool description",
            expected_output_format="structured"
        )

        assert tool.expected_output_format == "structured"

        # Call via forward and verify it still works
        result = tool.forward("Test prompt")
        assert result == "Test output from agent"
