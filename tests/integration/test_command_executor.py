"""
Integration tests for CommandExecutor with group commands.

Tests that group commands (like /agent) correctly show subcommands
when executed without a subcommand argument.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add cli_repl_kit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simple_agent" / "lib" / "cli_repl_kit"))

import click
from cli_repl_kit.core.config import Config
from cli_repl_kit.core.command_executor import CommandExecutor
from cli_repl_kit.core.formatting import formatted_text_to_ansi_string
from cli_repl_kit.plugins.base import ValidationResult


class TestGroupCommandExecution:
    """Test execution of group commands without subcommands."""

    @pytest.fixture
    def config(self) -> Config:
        """Load REPL config."""
        config_path = Path(__file__).parent.parent.parent / "simple_agent" / "repl_config.yaml"
        return Config.load(str(config_path), app_name="simple-agent")

    @pytest.fixture
    def cli_with_agent(self) -> click.Group:
        """Create CLI with agent group command."""
        cli = click.Group()

        @cli.group()
        def agent():
            """Agent management commands."""
            pass

        @agent.command()
        def list():
            """List all agents."""
            print("Agent list")

        @agent.command()
        def create():
            """Create a new agent."""
            print("Create agent")

        @agent.command()
        def load():
            """Load an agent."""
            print("Load agent")

        return cli

    @pytest.fixture
    def output_lines(self) -> list:
        """Capture output lines."""
        return []

    @pytest.fixture
    def executor(
        self, config: Config, cli_with_agent: click.Group, output_lines: list
    ) -> CommandExecutor:
        """Create CommandExecutor."""
        def append_output(line):
            if isinstance(line, list):
                text = formatted_text_to_ansi_string(line, config)
            else:
                text = str(line)
            output_lines.append(text)

        def validate_callback(cmd_name, cmd_args):
            return ValidationResult(status="valid"), None

        return CommandExecutor(
            config=config,
            cli=cli_with_agent,
            validate_callback=validate_callback,
            append_output_callback=append_output,
        )

    @pytest.fixture
    def mock_event(self) -> Mock:
        """Create mock event."""
        event = Mock()
        event.app = Mock()
        event.app.invalidate = Mock()
        return event

    @pytest.fixture
    def mock_buffer(self) -> Mock:
        """Create mock input buffer."""
        buffer = Mock()
        buffer.append_to_history = Mock()
        return buffer

    def test_group_command_shows_subcommands(
        self,
        executor: CommandExecutor,
        output_lines: list,
        mock_event: Mock,
        mock_buffer: Mock,
    ) -> None:
        """Test that /agent without subcommand shows available subcommands."""
        # Execute /agent
        executor.execute_command("/agent", mock_buffer, False, mock_event)

        # Clean ANSI codes for easier assertion
        def clean(text: str) -> str:
            import re
            return re.sub(r'\x1b\[[0-9;]*m', '', text)

        clean_output = [clean(line) for line in output_lines]
        full_output = "\n".join(clean_output)

        # Should show the command formatted
        assert any("/agent" in line for line in clean_output), \
            f"Command display not found in output: {full_output}"

        # Should show group description
        assert any("Agent management commands" in line for line in clean_output), \
            f"Group description not found in output: {full_output}"

        # Should show "Available subcommands" header
        assert any("Available subcommands" in line for line in clean_output), \
            f"Subcommands header not found in output: {full_output}"

        # Should list the subcommands
        assert any("list" in line for line in clean_output), \
            f"'list' subcommand not found in output: {full_output}"
        assert any("create" in line for line in clean_output), \
            f"'create' subcommand not found in output: {full_output}"
        assert any("load" in line for line in clean_output), \
            f"'load' subcommand not found in output: {full_output}"

    def test_group_command_with_subcommand_executes(
        self,
        executor: CommandExecutor,
        output_lines: list,
        mock_event: Mock,
        mock_buffer: Mock,
    ) -> None:
        """Test that /agent list executes the list subcommand."""
        # Execute /agent list
        executor.execute_command("/agent list", mock_buffer, False, mock_event)

        # Clean ANSI codes
        def clean(text: str) -> str:
            import re
            return re.sub(r'\x1b\[[0-9;]*m', '', text)

        clean_output = [clean(line) for line in output_lines]
        full_output = "\n".join(clean_output)

        # Should show the command formatted
        assert any("agent" in line for line in clean_output), \
            f"Command display not found in output: {full_output}"

        # Should show output from list command
        assert any("Agent list" in line for line in clean_output), \
            f"List command output not found in output: {full_output}"


class TestGroupCommandWithActualCommands:
    """Test with actual simple_agent commands."""

    @pytest.fixture
    def config(self) -> Config:
        """Load REPL config."""
        config_path = Path(__file__).parent.parent.parent / "simple_agent" / "repl_config.yaml"
        return Config.load(str(config_path), app_name="simple-agent")

    @pytest.fixture
    def cli_with_actual_agent(self) -> click.Group:
        """Create CLI with actual agent command."""
        from simple_agent.commands.agent_commands import agent

        cli = click.Group()
        cli.add_command(agent, name="agent")
        return cli

    @pytest.fixture
    def output_lines(self) -> list:
        """Capture output lines."""
        return []

    @pytest.fixture
    def executor(
        self, config: Config, cli_with_actual_agent: click.Group, output_lines: list
    ) -> CommandExecutor:
        """Create CommandExecutor."""
        def append_output(line):
            if isinstance(line, list):
                text = formatted_text_to_ansi_string(line, config)
            else:
                text = str(line)
            output_lines.append(text)

        def validate_callback(cmd_name, cmd_args):
            return ValidationResult(status="valid"), None

        return CommandExecutor(
            config=config,
            cli=cli_with_actual_agent,
            validate_callback=validate_callback,
            append_output_callback=append_output,
        )

    @pytest.fixture
    def mock_event(self) -> Mock:
        """Create mock event."""
        event = Mock()
        event.app = Mock()
        event.app.invalidate = Mock()
        return event

    @pytest.fixture
    def mock_buffer(self) -> Mock:
        """Create mock input buffer."""
        buffer = Mock()
        buffer.append_to_history = Mock()
        return buffer

    def test_actual_agent_command_shows_subcommands(
        self,
        executor: CommandExecutor,
        output_lines: list,
        mock_event: Mock,
        mock_buffer: Mock,
    ) -> None:
        """Test that actual /agent command shows its subcommands."""
        # Execute /agent
        executor.execute_command("/agent", mock_buffer, False, mock_event)

        # Clean ANSI codes
        def clean(text: str) -> str:
            import re
            return re.sub(r'\x1b\[[0-9;]*m', '', text)

        clean_output = [clean(line) for line in output_lines]
        full_output = "\n".join(clean_output)

        # Should show "Available subcommands" header
        assert any("Available subcommands" in line for line in clean_output), \
            f"Subcommands header not found in output:\n{full_output}"

        # Should list actual agent subcommands
        expected_subcommands = ["list", "create", "load", "run", "chat", "tools"]
        for subcmd in expected_subcommands:
            assert any(subcmd in line for line in clean_output), \
                f"'{subcmd}' subcommand not found in output:\n{full_output}"
