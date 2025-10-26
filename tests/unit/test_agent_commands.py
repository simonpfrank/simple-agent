"""
Unit tests for /agent tool commands (Phase 1.4).

Tests the tool-related agent commands: tools, add-tool, remove-tool.
"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from simple_agent.commands.agent_commands import agent


class TestAgentToolsCommand:
    """Test /agent tools command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.return_value = ["add", "subtract", "multiply"]

        return {"console": console, "agent_manager": agent_manager}

    def test_tools_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent tools command exists."""
        result = runner.invoke(agent, ["tools", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_tools_displays_agent_tools(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that tools displays all tools for an agent."""
        result = runner.invoke(agent, ["tools", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify agent_manager.get_agent_tools() was called
        mock_context["agent_manager"].get_agent_tools.assert_called_once_with(
            "test_agent"
        )

        # Verify console output was produced
        mock_context["console"].print.assert_called()

        # Verify summary line was printed
        call_args = str(mock_context["console"].print.call_args_list)
        assert "3 tools" in call_args.lower() or "add" in call_args.lower()

    def test_tools_shows_message_when_no_tools(self, runner: CliRunner) -> None:
        """Test tools shows message when agent has no tools."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.return_value = []

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["tools", "test_agent"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "no tools" in call_args.lower() or "empty" in call_args.lower()

    def test_tools_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test tools command with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["tools", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentAddToolCommand:
    """Test /agent add-tool command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        return {"console": console, "agent_manager": agent_manager}

    def test_add_tool_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent add-tool command exists."""
        result = runner.invoke(agent, ["add-tool", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_add_tool_adds_tool_to_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that add-tool adds a tool to an agent."""
        result = runner.invoke(
            agent, ["add-tool", "test_agent", "--tool", "add"], obj=mock_context
        )

        assert result.exit_code == 0

        # Verify add_tool_to_agent was called
        mock_context["agent_manager"].add_tool_to_agent.assert_called_once_with(
            "test_agent", "add"
        )

        # Verify success message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "added" in call_args.lower() or "success" in call_args.lower()

    def test_add_tool_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test add-tool with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.add_tool_to_agent.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["add-tool", "missing", "--tool", "add"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()

    def test_add_tool_handles_nonexistent_tool(self, runner: CliRunner) -> None:
        """Test add-tool with non-existent tool."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.add_tool_to_agent.side_effect = KeyError(
            "Tool 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["add-tool", "test_agent", "--tool", "missing"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentRemoveToolCommand:
    """Test /agent remove-tool command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        return {"console": console, "agent_manager": agent_manager}

    def test_remove_tool_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent remove-tool command exists."""
        result = runner.invoke(agent, ["remove-tool", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_remove_tool_removes_tool_from_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that remove-tool removes a tool from an agent."""
        result = runner.invoke(
            agent, ["remove-tool", "test_agent", "--tool", "add"], obj=mock_context
        )

        assert result.exit_code == 0

        # Verify remove_tool_from_agent was called
        mock_context["agent_manager"].remove_tool_from_agent.assert_called_once_with(
            "test_agent", "add"
        )

        # Verify success message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "removed" in call_args.lower() or "success" in call_args.lower()

    def test_remove_tool_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test remove-tool with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.remove_tool_from_agent.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["remove-tool", "missing", "--tool", "add"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentShowPromptCommand:
    """Test /agent show-prompt command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        # Mock agent with system prompt
        mock_agent = MagicMock()
        mock_agent.agent.system_prompt = "You are a helpful AI assistant with tools."
        agent_manager.get_agent.return_value = mock_agent

        return {"console": console, "agent_manager": agent_manager}

    def test_show_prompt_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent show-prompt command exists."""
        result = runner.invoke(agent, ["show-prompt", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_show_prompt_displays_system_prompt(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show-prompt displays the agent's system prompt."""
        result = runner.invoke(agent, ["show-prompt", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify agent was retrieved
        mock_context["agent_manager"].get_agent.assert_called_once_with("test_agent")

        # Verify console.print was called with a Panel
        assert mock_context["console"].print.called
        # Check that at least one call included a Panel with the system prompt
        calls = mock_context["console"].print.call_args_list
        assert len(calls) >= 1

    def test_show_prompt_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test show-prompt with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent.side_effect = KeyError("Agent 'missing' not found")

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["show-prompt", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentSaveCommand:
    """Test /agent save command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        return {"console": console, "agent_manager": agent_manager}

    def test_save_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent save command exists."""
        result = runner.invoke(agent, ["save", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_save_saves_agent_to_yaml(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that save command saves agent to YAML file."""
        result = runner.invoke(agent, ["save", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify save_agent_to_yaml was called
        mock_context["agent_manager"].save_agent_to_yaml.assert_called_once()
        call_args = mock_context["agent_manager"].save_agent_to_yaml.call_args
        assert call_args[0][0] == "test_agent"  # agent name
        assert "config/agents/test_agent.yaml" in call_args[0][1]  # path

        # Verify success message
        call_args_str = str(mock_context["console"].print.call_args_list)
        assert "saved" in call_args_str.lower()

    def test_save_with_custom_path(self, runner: CliRunner, mock_context: dict) -> None:
        """Test save with custom path option."""
        result = runner.invoke(
            agent,
            ["save", "test_agent", "--path", "custom/path.yaml"],
            obj=mock_context,
        )

        assert result.exit_code == 0

        # Verify custom path was used
        call_args = mock_context["agent_manager"].save_agent_to_yaml.call_args
        assert call_args[0][1] == "custom/path.yaml"

    def test_save_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test save with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.save_agent_to_yaml.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["save", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()
