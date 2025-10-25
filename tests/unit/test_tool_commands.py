"""
Unit tests for /tool commands (Phase 1.4).

Tests the tool management commands.
"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from simple_agent.commands.tool_commands import tool


class TestToolListCommand:
    """Test /tool list command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        tool_manager = MagicMock()
        tool_manager.list_tools.return_value = ["add", "subtract", "multiply"]

        return {"console": console, "tool_manager": tool_manager}

    def test_list_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /tool list command exists."""
        result = runner.invoke(tool, ["list", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_list_displays_all_tools(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that list displays all registered tools."""
        result = runner.invoke(tool, ["list"], obj=mock_context)

        assert result.exit_code == 0

        # Verify tool_manager.list_tools() was called
        mock_context["tool_manager"].list_tools.assert_called_once()

        # Verify console output was produced
        mock_context["console"].print.assert_called()

        # Verify summary line was printed
        call_args = str(mock_context["console"].print.call_args_list)
        assert "3 tools" in call_args.lower()

    def test_list_shows_message_when_no_tools(self, runner: CliRunner) -> None:
        """Test list shows message when no tools registered."""
        console = MagicMock()
        tool_manager = MagicMock()
        tool_manager.list_tools.return_value = []

        mock_context = {"console": console, "tool_manager": tool_manager}

        result = runner.invoke(tool, ["list"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "no tools" in call_args.lower() or "empty" in call_args.lower()


class TestToolInfoCommand:
    """Test /tool info command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        tool_manager = MagicMock()

        # Mock tool info
        tool_manager.get_tool_info.return_value = {
            "name": "add",
            "description": "Add two numbers",
            "inputs": {"a": "float", "b": "float"},
            "output_type": "float",
        }

        return {"console": console, "tool_manager": tool_manager}

    def test_info_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /tool info command exists."""
        result = runner.invoke(tool, ["info", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_info_displays_tool_details(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that info displays tool details."""
        result = runner.invoke(tool, ["info", "--name", "add"], obj=mock_context)

        assert result.exit_code == 0

        # Verify tool info was requested
        mock_context["tool_manager"].get_tool_info.assert_called_once_with("add")

        # Verify details were displayed
        call_args = str(mock_context["console"].print.call_args_list)
        assert "add" in call_args.lower()
        assert "description" in call_args.lower()

    def test_info_handles_missing_tool(self, runner: CliRunner) -> None:
        """Test info command with non-existent tool."""
        console = MagicMock()
        tool_manager = MagicMock()
        tool_manager.get_tool_info.side_effect = KeyError("Tool 'missing' not found")

        mock_context = {"console": console, "tool_manager": tool_manager}

        result = runner.invoke(tool, ["info", "--name", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()
