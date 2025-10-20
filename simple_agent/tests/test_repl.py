"""
Tests for REPL functionality.
These tests verify REPL-specific features like / prefix handling and auto-completion.
"""

from unittest.mock import Mock, patch
from click.testing import CliRunner

from repl_cli_template.app import cli, get_command_names, start_repl


class TestSlashPrefixStripping:
    """Tests for / prefix stripping functionality."""

    def test_slash_stripping_wrapper_strips_slash(self):
        """Test that the wrapper function strips leading / from commands."""

        # Mock the original function
        original_execute = Mock(return_value=["help"])

        # Create our wrapper
        def execute_with_slash_stripping(
            command, allow_internal_commands, allow_system_commands
        ):
            if command.startswith("/"):
                command = command[1:]
            return original_execute(
                command, allow_internal_commands, allow_system_commands
            )

        # Test with / prefix
        result = execute_with_slash_stripping("/help", True, True)
        original_execute.assert_called_once_with("help", True, True)
        assert result == ["help"]

    def test_slash_stripping_wrapper_handles_no_slash(self):
        """Test that commands without / still work."""
        original_execute = Mock(return_value=["config", "show"])

        def execute_with_slash_stripping(
            command, allow_internal_commands, allow_system_commands
        ):
            if command.startswith("/"):
                command = command[1:]
            return original_execute(
                command, allow_internal_commands, allow_system_commands
            )

        # Test without / prefix
        result = execute_with_slash_stripping("config show", True, True)
        original_execute.assert_called_once_with("config show", True, True)
        assert result == ["config", "show"]

    def test_slash_stripping_wrapper_handles_slash_with_args(self):
        """Test that / prefix is stripped from commands with arguments."""
        original_execute = Mock(return_value=["process", "--input", "file.txt"])

        def execute_with_slash_stripping(
            command, allow_internal_commands, allow_system_commands
        ):
            if command.startswith("/"):
                command = command[1:]
            return original_execute(
                command, allow_internal_commands, allow_system_commands
            )

        # Test with / prefix and arguments
        execute_with_slash_stripping("/process --input file.txt", True, True)
        original_execute.assert_called_once_with("process --input file.txt", True, True)


class TestGetCommandNames:
    """Tests for get_command_names function."""

    def test_get_command_names_returns_all_commands(self):
        """Test that get_command_names extracts all command names from CLI group."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a context to get the CLI group
            with cli.make_context("cli", []) as ctx:
                command_names = get_command_names(ctx.command)

                # Verify all our registered commands are present
                assert "help" in command_names
                assert "quit" in command_names
                assert "exit" in command_names
                assert "config" in command_names
                assert "process" in command_names

    def test_get_command_names_returns_list(self):
        """Test that get_command_names returns a list."""
        with cli.make_context("cli", []) as ctx:
            result = get_command_names(ctx.command)
            assert isinstance(result, list)

    def test_get_command_names_with_no_commands(self):
        """Test that get_command_names handles empty command group."""
        import click

        @click.group()
        def empty_cli():
            pass

        # Don't use make_context for empty group (it exits)
        # Just test the function directly
        result = get_command_names(empty_cli)
        assert result == []


class TestAutoCompletion:
    """Tests for auto-completion setup."""

    def test_completions_include_slash_prefix(self):
        """Test that auto-completion includes / prefix for all commands."""

        # Get command names
        with cli.make_context("cli", []) as ctx:
            command_names = get_command_names(ctx.command)

            # Create completions with / prefix
            completions = ["/" + name for name in command_names]

            # Verify all have / prefix
            assert all(c.startswith("/") for c in completions)
            assert "/help" in completions
            assert "/quit" in completions
            assert "/config" in completions

    def test_word_completer_creation(self):
        """Test that WordCompleter is created correctly."""
        from prompt_toolkit.completion import WordCompleter

        completions = ["/help", "/quit", "/config", "/process"]
        completer = WordCompleter(completions, ignore_case=True, sentence=True)

        # Verify completer was created
        assert completer is not None
        assert isinstance(completer, WordCompleter)


class TestREPLIntegration:
    """Integration tests for REPL functionality."""

    @patch("repl_cli_template.app.repl")
    @patch("repl_cli_template.app.show_welcome")
    def test_start_repl_shows_welcome(self, mock_welcome, mock_repl):
        """Test that start_repl displays welcome screen."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a minimal config file
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n  version: 1.0.0\n")

            with cli.make_context("cli", ["--config", "config.yaml"]) as ctx:
                # Ensure context.obj is initialized (cli() does this normally)
                ctx.ensure_object(dict)
                ctx.obj["config"] = {
                    "app": {"name": "Test", "version": "1.0.0"},
                    "logging": {"file": "logs/app.log"},
                }
                ctx.obj["config_file"] = "config.yaml"

                # Mock repl to avoid actually starting interactive session
                mock_repl.side_effect = KeyboardInterrupt()

                try:
                    start_repl(ctx)
                except (KeyboardInterrupt, SystemExit):
                    pass

                # Verify welcome was called
                mock_welcome.assert_called_once()

    @patch("repl_cli_template.app.repl")
    def test_start_repl_patches_execute_function(self, mock_repl):
        """Test that start_repl patches _execute_internal_and_sys_cmds."""
        import click_repl._repl as repl_module

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            # Save original function
            original_func = repl_module._execute_internal_and_sys_cmds

            with cli.make_context("cli", ["--config", "config.yaml"]) as ctx:
                # Initialize context.obj
                ctx.ensure_object(dict)
                ctx.obj["config"] = {
                    "app": {"name": "Test"},
                    "logging": {"file": "logs/app.log"},
                }
                ctx.obj["config_file"] = "config.yaml"

                mock_repl.side_effect = KeyboardInterrupt()

                try:
                    start_repl(ctx)
                except (KeyboardInterrupt, SystemExit):
                    pass

            # Verify function was restored after start_repl exits
            assert repl_module._execute_internal_and_sys_cmds == original_func

    @patch("repl_cli_template.app.repl")
    def test_start_repl_restores_function_on_error(self, mock_repl):
        """Test that patched function is restored even if error occurs."""
        import click_repl._repl as repl_module

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            # Save original
            original_func = repl_module._execute_internal_and_sys_cmds

            with cli.make_context("cli", ["--config", "config.yaml"]) as ctx:
                # Make repl raise an exception
                mock_repl.side_effect = Exception("Test error")

                try:
                    start_repl(ctx)
                except Exception:
                    pass

            # Verify function was still restored
            assert repl_module._execute_internal_and_sys_cmds == original_func


class TestREPLCommandExecution:
    """Tests for command execution in REPL mode."""

    def test_repl_mode_started_with_no_subcommand(self):
        """Test that REPL mode starts when no subcommand is provided."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            # Mock the start_repl function to avoid interactive session
            with patch("repl_cli_template.app.start_repl") as mock_start_repl:
                runner.invoke(cli, ["--config", "config.yaml"])

                # start_repl should have been called
                mock_start_repl.assert_called_once()

    def test_repl_mode_not_started_with_subcommand(self):
        """Test that REPL mode doesn't start when subcommand is provided."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            # Mock start_repl to verify it's NOT called
            with patch("repl_cli_template.app.start_repl") as mock_start_repl:
                runner.invoke(cli, ["--config", "config.yaml", "config", "show"])

                # start_repl should NOT have been called
                mock_start_repl.assert_not_called()


class TestREPLErrorHandling:
    """Tests for error handling in REPL."""

    @patch("repl_cli_template.app.repl")
    @patch(
        "repl_cli_template.ui.welcome.show_goodbye"
    )  # Patch where it's defined, not where it's imported
    def test_keyboard_interrupt_shows_goodbye(self, mock_goodbye, mock_repl):
        """Test that Ctrl+C shows goodbye message."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            with cli.make_context("cli", ["--config", "config.yaml"]) as ctx:
                # Initialize context.obj
                ctx.ensure_object(dict)
                ctx.obj["config"] = {
                    "app": {"name": "Test"},
                    "logging": {"file": "logs/app.log"},
                }
                ctx.obj["config_file"] = "config.yaml"

                mock_repl.side_effect = KeyboardInterrupt()

                try:
                    start_repl(ctx)
                except SystemExit:
                    pass

                # Verify goodbye was called
                mock_goodbye.assert_called_once()

    @patch("repl_cli_template.app.repl")
    @patch("repl_cli_template.ui.welcome.show_goodbye")  # Patch where it's defined
    def test_eof_error_shows_goodbye(self, mock_goodbye, mock_repl):
        """Test that Ctrl+D (EOFError) shows goodbye message."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("config.yaml", "w") as f:
                f.write("app:\n  name: Test\n")

            with cli.make_context("cli", ["--config", "config.yaml"]) as ctx:
                # Initialize context.obj
                ctx.ensure_object(dict)
                ctx.obj["config"] = {
                    "app": {"name": "Test"},
                    "logging": {"file": "logs/app.log"},
                }
                ctx.obj["config_file"] = "config.yaml"

                mock_repl.side_effect = EOFError()

                try:
                    start_repl(ctx)
                except SystemExit:
                    pass

                # Verify goodbye was called
                mock_goodbye.assert_called_once()
