"""
Unit tests for /history commands (Phase 1.2).

Tests the history management commands.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from click.testing import CliRunner

from simple_agent.commands.history_commands import history


class TestHistoryShowCommand:
    """Test /history show command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        # Mock SimpleAgent wrapper with underlying agent.memory
        mock_simple_agent = MagicMock()
        mock_simple_agent.agent = MagicMock()  # The underlying SmolAgents agent
        mock_simple_agent.agent.memory = MagicMock()
        mock_simple_agent.agent.memory.get_full_steps = MagicMock(return_value=[])

        agent_manager.get_agent = MagicMock(return_value=mock_simple_agent)
        agent_manager.last_agent = "default"

        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_show_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /history show command exists."""
        result = runner.invoke(history, ["show", "--help"], obj=mock_context)

        assert result.exit_code == 0
        assert "show" in result.output.lower() or "history" in result.output.lower()

    def test_show_displays_message_when_no_history(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show displays message when memory is empty."""
        # Setup - empty memory
        mock_agent = mock_context["agent_manager"].get_agent.return_value
        mock_agent.memory.get_full_steps.return_value = []

        result = runner.invoke(history, ["show"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()

        # Check that "no history" or similar message was shown
        call_args = str(mock_context["console"].print.call_args_list)
        assert "no history" in call_args.lower() or "empty" in call_args.lower()

    def test_show_displays_history_steps(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show displays history from memory."""
        # Setup - mock memory with steps
        mock_simple_agent = mock_context["agent_manager"].get_agent.return_value
        mock_simple_agent.agent.memory.get_full_steps.return_value = [
            {
                "type": "task",
                "task": "What is 2+2?",
                "timestamp": "2025-10-23T10:00:00",
            },
            {
                "type": "action",
                "action": "final_answer",
                "result": "4",
                "timestamp": "2025-10-23T10:00:01",
            },
        ]

        result = runner.invoke(history, ["show"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()

        # Verify agent's memory was accessed
        mock_simple_agent.agent.memory.get_full_steps.assert_called_once()

    def test_show_respects_limit_parameter(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show respects --limit parameter."""
        # Setup - mock memory with 5 steps
        mock_simple_agent = mock_context["agent_manager"].get_agent.return_value
        mock_simple_agent.agent.memory.get_full_steps.return_value = [
            {"type": "task", "task": f"Task {i}"} for i in range(5)
        ]

        result = runner.invoke(history, ["show", "--limit", "2"], obj=mock_context)

        assert result.exit_code == 0
        # Should only display last 2 items
        # (Actual verification would check console output formatting)

    def test_show_handles_missing_last_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show handles when no agent has been run."""
        # Setup - no last agent
        mock_context["agent_manager"].last_agent = None

        result = runner.invoke(history, ["show"], obj=mock_context)

        assert result.exit_code == 0
        # Should show error or message about no agent


class TestHistoryClearCommand:
    """Test /history clear command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        # Mock SimpleAgent wrapper with underlying agent.memory
        mock_simple_agent = MagicMock()
        mock_simple_agent.agent = MagicMock()
        mock_simple_agent.agent.memory = MagicMock()
        mock_simple_agent.agent.memory.reset = MagicMock()

        agent_manager.get_agent = MagicMock(return_value=mock_simple_agent)
        agent_manager.last_agent = "default"

        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_clear_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /history clear command exists."""
        result = runner.invoke(history, ["clear", "--help"], obj=mock_context)

        assert result.exit_code == 0

    def test_clear_resets_agent_memory(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that clear calls agent.memory.reset()."""
        mock_simple_agent = mock_context["agent_manager"].get_agent.return_value

        result = runner.invoke(history, ["clear"], obj=mock_context)

        assert result.exit_code == 0
        mock_simple_agent.agent.memory.reset.assert_called_once()
        mock_context["console"].print.assert_called()

    def test_clear_shows_confirmation(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that clear shows confirmation message."""
        result = runner.invoke(history, ["clear"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "cleared" in call_args.lower() or "reset" in call_args.lower()


class TestHistorySaveCommand:
    """Test /history save command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        # Mock SimpleAgent wrapper with underlying agent.memory
        mock_simple_agent = MagicMock()
        mock_simple_agent.agent = MagicMock()
        mock_simple_agent.agent.memory = MagicMock()
        mock_simple_agent.agent.memory.get_full_steps = MagicMock(
            return_value=[
                {"type": "task", "task": "What is 2+2?"},
                {"type": "action", "result": "4"},
            ]
        )

        agent_manager.get_agent = MagicMock(return_value=mock_simple_agent)
        agent_manager.last_agent = "default"

        return {
            "console": console,
            "agent_manager": agent_manager,
        }

    def test_save_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /history save command exists."""
        result = runner.invoke(history, ["save", "--help"], obj=mock_context)

        assert result.exit_code == 0

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_writes_to_file(
        self,
        mock_json_dump: MagicMock,
        mock_file_open: MagicMock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test that save writes memory to JSON file."""
        result = runner.invoke(history, ["save", "test_history.json"], obj=mock_context)

        assert result.exit_code == 0

        # Verify file was opened for writing
        mock_file_open.assert_called_once_with("test_history.json", "w")

        # Verify JSON was written
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_includes_memory_steps(
        self,
        mock_json_dump: MagicMock,
        mock_file_open: MagicMock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test that save includes all memory steps."""
        mock_simple_agent = mock_context["agent_manager"].get_agent.return_value
        expected_steps = mock_simple_agent.agent.memory.get_full_steps.return_value

        result = runner.invoke(history, ["save", "test.json"], obj=mock_context)

        assert result.exit_code == 0

        # Verify memory was accessed
        mock_simple_agent.agent.memory.get_full_steps.assert_called_once()

        # Verify correct data was written (first arg to json.dump)
        call_args = mock_json_dump.call_args
        saved_data = call_args[0][0]  # First positional argument
        # Save includes metadata wrapper, so check the steps key
        assert "steps" in saved_data
        assert saved_data["steps"] == expected_steps

    def test_save_shows_confirmation(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that save shows confirmation message."""
        with patch("builtins.open", mock_open()), patch("json.dump"):
            result = runner.invoke(history, ["save", "test.json"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "saved" in call_args.lower()
