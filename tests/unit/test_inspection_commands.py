"""
Unit tests for inspection commands (Phase 1.1).

Tests /prompt and /response command groups.
These are thin CLI wrappers - business logic is in AgentManager.
"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from simple_agent.commands.inspection_commands import prompt, response


class TestPromptCommands:
    """Test /prompt command group."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.last_prompt = None
        agent_manager.last_response = None
        agent_manager.last_agent = None
        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_prompt_show_displays_message_when_no_prompts(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /prompt show displays message when no prompts yet."""
        result = runner.invoke(prompt, ["show"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()
        # Check that it mentions "No prompts yet"
        call_args = str(mock_context["console"].print.call_args)
        assert "No prompts yet" in call_args or "no prompts" in call_args.lower()

    def test_prompt_show_displays_last_prompt(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /prompt show displays the last prompt."""
        # Setup
        mock_context["agent_manager"].last_prompt = "What is 2+2?"
        mock_context["agent_manager"].last_agent = "test_agent"

        result = runner.invoke(prompt, ["show"], obj=mock_context)

        assert result.exit_code == 0
        # Verify console.print was called (Panel will be passed)
        assert (
            mock_context["console"].print.call_count >= 2
        )  # Empty line + Panel + Empty line

    def test_prompt_raw_displays_message_when_no_prompts(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /prompt raw displays message when no prompts yet."""
        result = runner.invoke(prompt, ["raw"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()
        call_args = str(mock_context["console"].print.call_args)
        assert "No prompts yet" in call_args or "no prompts" in call_args.lower()

    def test_prompt_raw_displays_last_prompt(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /prompt raw displays the last prompt."""
        # Setup
        mock_context["agent_manager"].last_prompt = "Test prompt"
        mock_context["agent_manager"].last_agent = "my_agent"

        result = runner.invoke(prompt, ["raw"], obj=mock_context)

        assert result.exit_code == 0
        # Verify console.print was called (Panel will be passed)
        assert (
            mock_context["console"].print.call_count >= 2
        )  # Empty line + Panel + Empty line


class TestResponseCommands:
    """Test /response command group."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.last_prompt = None
        agent_manager.last_response = None
        agent_manager.last_agent = None
        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_response_show_displays_message_when_no_responses(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /response show displays message when no responses yet."""
        result = runner.invoke(response, ["show"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()
        call_args = str(mock_context["console"].print.call_args)
        assert "No responses yet" in call_args or "no responses" in call_args.lower()

    def test_response_show_displays_last_response(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /response show displays the last response."""
        # Setup
        mock_context["agent_manager"].last_response = "The answer is 4"
        mock_context["agent_manager"].last_agent = "calculator"

        result = runner.invoke(response, ["show"], obj=mock_context)

        assert result.exit_code == 0
        # Verify console.print was called (Panel will be passed)
        assert (
            mock_context["console"].print.call_count >= 2
        )  # Empty line + Panel + Empty line

    def test_response_raw_displays_message_when_no_responses(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /response raw displays message when no responses yet."""
        result = runner.invoke(response, ["raw"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()
        call_args = str(mock_context["console"].print.call_args)
        assert "No responses yet" in call_args or "no responses" in call_args.lower()

    def test_response_raw_displays_last_response(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test /response raw displays the last response."""
        # Setup
        mock_context["agent_manager"].last_response = "Test response"
        mock_context["agent_manager"].last_agent = "test_agent"

        result = runner.invoke(response, ["raw"], obj=mock_context)

        assert result.exit_code == 0
        # Verify console.print was called (Panel will be passed)
        assert (
            mock_context["console"].print.call_count >= 2
        )  # Empty line + Panel + Empty line
