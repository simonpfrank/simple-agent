"""
Unit tests for AgentManager inspection features (Phase 1.1).

Tests prompt/response tracking for inspection commands.
"""

from unittest.mock import MagicMock, patch

import pytest

from simple_agent.core.agent_manager import AgentManager


class TestAgentManagerInspection:
    """Test AgentManager prompt/response tracking."""

    @pytest.fixture
    def test_config(self) -> dict:
        """Minimal test configuration."""
        return {
            "llm": {"provider": "openai", "openai": {"model": "gpt-4o-mini"}},
            "agents": {"default": {"role": "Test assistant"}},
            "debug": {"enabled": False},
        }

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_last_prompt_initialized_to_none(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that last_prompt is initialized to None."""
        agent_manager = AgentManager(test_config)
        assert agent_manager.last_prompt is None

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_last_response_initialized_to_none(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that last_response is initialized to None."""
        agent_manager = AgentManager(test_config)
        assert agent_manager.last_response is None

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_last_agent_initialized_to_none(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that last_agent is initialized to None."""
        agent_manager = AgentManager(test_config)
        assert agent_manager.last_agent is None

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_stores_prompt(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that run_agent stores the prompt."""
        # Setup mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Test response"
        mock_simple_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # Run agent
        prompt = "What is 2+2?"
        agent_manager.run_agent("test_agent", prompt)

        # Verify prompt stored
        assert agent_manager.last_prompt == prompt

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_stores_response(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that run_agent stores the response."""
        # Setup mock
        mock_agent_instance = MagicMock()
        expected_response = "The answer is 4"
        mock_agent_instance.run.return_value = expected_response
        mock_simple_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # Run agent
        agent_manager.run_agent("test_agent", "What is 2+2?")

        # Verify response stored
        assert agent_manager.last_response == expected_response

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_stores_agent_name(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that run_agent stores the agent name."""
        # Setup mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Response"
        mock_simple_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("my_agent")

        # Run agent
        agent_manager.run_agent("my_agent", "Test prompt")

        # Verify agent name stored
        assert agent_manager.last_agent == "my_agent"

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_updates_tracking_on_multiple_calls(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that tracking updates on subsequent runs."""
        # Setup mock
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.side_effect = ["First response", "Second response"]
        mock_simple_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # First run
        agent_manager.run_agent("test_agent", "First prompt")
        assert agent_manager.last_prompt == "First prompt"
        assert agent_manager.last_response == "First response"

        # Second run
        agent_manager.run_agent("test_agent", "Second prompt")
        assert agent_manager.last_prompt == "Second prompt"
        assert agent_manager.last_response == "Second response"

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_converts_response_to_string(
        self, mock_simple_agent: MagicMock, test_config: dict
    ) -> None:
        """Test that non-string responses are converted to strings."""
        # Setup mock with non-string response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = 42  # Integer response
        mock_simple_agent.return_value = mock_agent_instance

        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # Run agent
        agent_manager.run_agent("test_agent", "Test")

        # Verify response converted to string
        assert agent_manager.last_response == "42"
        assert isinstance(agent_manager.last_response, str)
