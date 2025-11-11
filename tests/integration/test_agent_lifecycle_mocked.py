"""
Integration test for agent lifecycle with mocked LLM.

Tests the full flow: load config - create agent - run prompt
Uses mocked LLM responses for CI/CD compatibility.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.agent_manager import AgentManager


class TestAgentLifecycleMocked:
    """Test full agent lifecycle with mocked LLM."""

    @pytest.fixture
    def test_config(self) -> dict:
        """Load test configuration."""
        config_path = Path(__file__).parent.parent / "data" / "test_config.yaml"
        config = ConfigManager.load(str(config_path))
        return config

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_full_lifecycle_default_agent(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test creating and running agent with default configuration."""
        # Setup mock agent response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "The answer is 4"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Create agent
        agent = agent_manager.create_agent("calculator")

        # Verify agent was created
        assert agent is not None
        assert agent.name == "calculator"
        assert "calculator" in agent_manager.list_agents()

        # Run prompt through agent
        response = agent_manager.run_agent("calculator", "What is 2+2?")

        # Verify response (AgentResult supports string conversion for backward compatibility)
        assert str(response) == "The answer is 4"
        mock_agent_instance.run.assert_called_once_with("What is 2+2?", reset=True)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_multiple_agents(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test managing multiple agents."""
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Create multiple agents
        agent1 = agent_manager.create_agent("agent1")
        agent2 = agent_manager.create_agent("agent2")
        agent3 = agent_manager.create_agent("agent3")

        # Verify all registered
        agents = agent_manager.list_agents()
        assert (
            len(agents) == 3
        )  # Only manually created agents (not auto-loaded from config)
        assert "agent1" in agents
        assert "agent2" in agents
        assert "agent3" in agents

        # Verify can retrieve each
        assert agent_manager.get_agent("agent1") == agent1
        assert agent_manager.get_agent("agent2") == agent2
        assert agent_manager.get_agent("agent3") == agent3

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_config_loading_and_defaults(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that configuration loads correctly and defaults are applied."""
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Create agent with defaults
        agent_manager.create_agent("default_agent")

        # Verify defaults were applied from config
        # Note: call_args gets the LAST call, which is for 'default_agent'
        # The first call was for auto-loaded 'default' agent
        call_kwargs = mock_tool_calling_agent.call_args.kwargs
        assert (
            call_kwargs["instructions"] == "You are a helpful AI assistant for testing."
        )
        # ToolCallingAgent doesn't have verbosity_level parameter
        assert call_kwargs["max_steps"] == 10

    def test_error_handling_nonexistent_agent(self, test_config: dict) -> None:
        """Test error handling when accessing non-existent agent."""
        agent_manager = AgentManager(test_config)

        # Try to get non-existent agent
        with pytest.raises(KeyError, match="Agent 'missing' not found"):
            agent_manager.get_agent("missing")

        # Try to run non-existent agent
        with pytest.raises(KeyError, match="Agent 'missing' not found"):
            agent_manager.run_agent("missing", "test")

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_user_prompt_template_integration(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test user_prompt_template end-to-end (create, run, save, load)."""
        # Setup mock agent response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "The answer is 4"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Create agent with user_prompt_template
        template = "{user_input}\n\nPlease be concise."
        agent = agent_manager.create_agent(
            "template_agent", user_prompt_template=template
        )

        # Verify agent was created with template
        assert agent is not None
        assert agent.user_prompt_template == template

        # Run prompt through agent
        agent_manager.run_agent("template_agent", "What is 2+2?")

        # Verify the template was applied to the input
        mock_agent_instance.run.assert_called_once_with(
            "What is 2+2?\n\nPlease be concise.", reset=True
        )
