"""
Integration tests for Phase 1.1 with mocked LLM (CI/CD compatible).

Tests the full flow of inspection and chat features.
Uses mocked LLM responses for reliable testing.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.agent_manager import AgentManager


class TestPhase1_1InspectionMocked:
    """Test inspection features with mocked LLM."""

    @pytest.fixture
    def test_config(self) -> dict:
        """Load test configuration."""
        config_path = Path(__file__).parent.parent / "data" / "test_config.yaml"
        config = ConfigManager.load(str(config_path))
        return config

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_prompt_response_tracking_lifecycle(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test full lifecycle: create agent - run - track prompt/response."""
        # Setup mock agent response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "The capital of France is Paris"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Verify tracking starts as None
        assert agent_manager.last_prompt is None
        assert agent_manager.last_response is None
        assert agent_manager.last_agent is None

        # Create and run agent
        agent_manager.create_agent("test_agent")
        prompt = "What is the capital of France?"
        response = agent_manager.run_agent("test_agent", prompt)

        # Verify tracking captured the interaction
        assert agent_manager.last_prompt == prompt
        assert agent_manager.last_response == "The capital of France is Paris"
        assert agent_manager.last_agent == "test_agent"
        assert (
            str(response) == "The capital of France is Paris"
        )  # AgentResult supports string conversion

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_tracking_updates_on_multiple_runs(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that tracking updates correctly on subsequent runs."""
        # Setup mock with multiple responses
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.side_effect = ["Response 1", "Response 2", "Response 3"]
        mock_tool_calling_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("agent1")

        # First run
        agent_manager.run_agent("agent1", "Prompt 1")
        assert agent_manager.last_prompt == "Prompt 1"
        assert agent_manager.last_response == "Response 1"
        assert agent_manager.last_agent == "agent1"

        # Second run
        agent_manager.run_agent("agent1", "Prompt 2")
        assert agent_manager.last_prompt == "Prompt 2"
        assert agent_manager.last_response == "Response 2"
        assert agent_manager.last_agent == "agent1"

        # Third run
        agent_manager.run_agent("agent1", "Prompt 3")
        assert agent_manager.last_prompt == "Prompt 3"
        assert agent_manager.last_response == "Response 3"
        assert agent_manager.last_agent == "agent1"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_tracking_across_multiple_agents(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that tracking works when switching between agents."""
        # Setup mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.side_effect = [
            "Response from agent1",
            "Response from agent2",
            "Another from agent1",
        ]
        mock_tool_calling_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("agent1")
        agent_manager.create_agent("agent2")

        # Run with agent1
        agent_manager.run_agent("agent1", "Prompt for agent1")
        assert agent_manager.last_agent == "agent1"
        assert agent_manager.last_prompt == "Prompt for agent1"
        assert agent_manager.last_response == "Response from agent1"

        # Run with agent2
        agent_manager.run_agent("agent2", "Prompt for agent2")
        assert agent_manager.last_agent == "agent2"
        assert agent_manager.last_prompt == "Prompt for agent2"
        assert agent_manager.last_response == "Response from agent2"

        # Run with agent1 again
        agent_manager.run_agent("agent1", "Another prompt for agent1")
        assert agent_manager.last_agent == "agent1"
        assert agent_manager.last_prompt == "Another prompt for agent1"
        assert agent_manager.last_response == "Another from agent1"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_tracking_handles_non_string_responses(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that non-string responses are converted to strings."""
        # Setup mock with various response types
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.side_effect = [
            42,  # Integer
            {"key": "value"},  # Dict
            ["item1", "item2"],  # List
        ]
        mock_tool_calling_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # Test integer response
        agent_manager.run_agent("test_agent", "What is 42?")
        assert agent_manager.last_response == "42"
        assert isinstance(agent_manager.last_response, str)

        # Test dict response
        agent_manager.run_agent("test_agent", "Give me a dict")
        assert "key" in agent_manager.last_response
        assert isinstance(agent_manager.last_response, str)

        # Test list response
        agent_manager.run_agent("test_agent", "Give me a list")
        assert "item1" in agent_manager.last_response
        assert isinstance(agent_manager.last_response, str)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_auto_loaded_agent_tracking(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that tracking works with manually created agents."""
        # Setup mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Auto-loaded response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # AgentManager needs agents to be created manually
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("default")

        # Verify 'default' was created
        assert "default" in agent_manager.list_agents()

        # Run with created agent
        response = agent_manager.run_agent("default", "Test with default agent")

        # Verify tracking works
        assert agent_manager.last_agent == "default"
        assert agent_manager.last_prompt == "Test with default agent"
        assert agent_manager.last_response == "Auto-loaded response"
        assert (
            str(response) == "Auto-loaded response"
        )  # AgentResult supports string conversion
