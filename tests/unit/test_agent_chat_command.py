"""
Unit tests for /agent chat command (Phase 1.1).

Tests the interactive chat mode command.
Note: Full interactive testing is in integration tests.
"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from simple_agent.commands.agent_commands import agent


class TestAgentChatCommand:
    """Test /agent chat command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        # Setup mock agent
        agent_manager.get_agent.return_value = MagicMock()
        agent_manager.run_agent.return_value = "Test response"
        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_chat_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent chat command exists."""
        result = runner.invoke(agent, ["chat", "--help"], obj=mock_context)

        assert result.exit_code == 0
        assert "chat" in result.output.lower()

    def test_chat_displays_error_for_nonexistent_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that chat displays error for non-existent agent."""
        # Setup - agent doesn't exist
        mock_context["agent_manager"].get_agent.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        result = runner.invoke(agent, ["chat", "missing"], obj=mock_context)

        assert result.exit_code == 0  # Command runs but shows error
        mock_context["console"].print.assert_called()
        # Check error message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "error" in call_args.lower() or "not found" in call_args.lower()

    def test_chat_verifies_agent_exists_before_starting(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that chat verifies agent exists."""
        # This test verifies get_agent is called
        # We can't easily test the full interactive loop without integration tests
        mock_context["agent_manager"].get_agent.return_value = MagicMock()

        # Note: Chat is interactive, so we need to provide input or it will hang
        # We'll test the verification part only
        result = runner.invoke(
            agent, ["chat", "test_agent"], obj=mock_context, input="\n"
        )

        # Verify get_agent was called (verifying agent exists)
        mock_context["agent_manager"].get_agent.assert_called_once_with("test_agent")
