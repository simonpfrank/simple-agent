"""
Main entry point for REPL/CLI application.
"""

import click
import logging
import sys
from pathlib import Path

from click_repl import repl
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from repl_cli_template.core.config_manager import ConfigManager
from repl_cli_template.core.logging_setup import setup_logging
from repl_cli_template.ui.welcome import show_welcome
from repl_cli_template.ui.styles import APP_THEME
from repl_cli_template.commands.system_commands import (
    help_command,
    quit_command,
    exit_command,
)
from repl_cli_template.commands.config_commands import config
from repl_cli_template.commands.process_commands import process

# Initialize console
console = Console(theme=APP_THEME)

# Application metadata
APP_NAME = "REPL CLI Template"
APP_VERSION = "1.0.0"
DEFAULT_CONFIG = "config.yaml"

# REPL UI constants
COMPLETION_MENU_HEIGHT = 8  # Number of lines reserved for completion menu
CONSOLE_LOG_LEVEL = logging.WARNING  # Log level for console in CLI mode


@click.group(invoke_without_command=True)
@click.option("--config", "-c", default=DEFAULT_CONFIG, help="Path to config file")
@click.option("--repl-mode", is_flag=True, default=False, help="Start in REPL mode")
@click.pass_context
def cli(context, config, repl_mode):
    """
    REPL/CLI Template Application.

    Run without arguments to start REPL mode.
    Run with a command for CLI mode.
    """
    # Initialize context object
    context.ensure_object(dict)

    # Add console to context for dependency injection
    context.obj["console"] = console

    # Load configuration
    try:
        if Path(config).exists():
            config_dict = ConfigManager.load(config)
            config_dict = ConfigManager.merge_with_defaults(config_dict)
        else:
            # Use defaults if config file doesn't exist
            config_dict = ConfigManager.get_defaults()
            console.print("[dim]Config file not found, using defaults[/dim]")

        context.obj["config"] = config_dict
        context.obj["config_file"] = config

    except Exception as e:
        console.print(f"[error]Error loading config:[/error] {str(e)}")
        sys.exit(1)

    # Setup logging
    log_file = ConfigManager.get(config_dict, "logging.file", "logs/app.log")
    log_level = ConfigManager.get(config_dict, "logging.level", "INFO")

    # Enable console logging only if NOT in REPL mode
    console_enabled = context.invoked_subcommand is not None

    setup_logging(log_file, log_level, console_enabled)

    # If no subcommand provided, start REPL mode
    if context.invoked_subcommand is None or repl_mode:
        start_repl(context)


def get_command_names(cli_group: click.Group) -> list[str]:
    """
    Get all command names from the CLI group.

    Args:
        cli_group: Click group containing commands

    Returns:
        List of command names
    """
    names: list[str] = []
    if hasattr(cli_group, "commands"):
        for name in cli_group.commands.keys():
            names.append(name)
    return names


def start_repl(context: click.Context) -> None:
    """
    Start the REPL interface with / prefix support and auto-completion.

    Args:
        context: Click context object containing config and other shared state

    Raises:
        KeyboardInterrupt: When user presses Ctrl+C
        EOFError: When user presses Ctrl+D
        ExitReplException: When user runs /quit or /exit
    """
    # Show welcome screen
    config_dict = context.obj["config"]
    config_file = context.obj["config_file"]
    log_file = ConfigManager.get(config_dict, "logging.file", "logs/app.log")

    app_name = ConfigManager.get(config_dict, "app.name", APP_NAME)
    app_version = ConfigManager.get(config_dict, "app.version", APP_VERSION)

    show_welcome(console, app_name, app_version, config_file, log_file)

    # Build command dictionary with help text
    commands_dict = {}
    if hasattr(context.command, "commands"):
        for name, cmd in context.command.commands.items():
            commands_dict[name] = cmd.help or "No description"

    # Create custom completer with Click CLI group for subcommand support
    from repl_cli_template.ui.completion import SlashCommandCompleter

    completer = SlashCommandCompleter(commands_dict, cli_group=context.command)

    # Custom style for completion dropdown - transparent backgrounds, bright highlight
    completion_style = Style.from_dict(
        {
            "completion-menu": "",  # No background
            "completion-menu.completion": "noinherit #5fafff",  # Unhighlighted command: blue, transparent bg
            "completion-menu.completion.current": "noinherit #00ffff bold",  # Highlighted: bright cyan, bold, transparent bg
            "completion-menu.meta": "",  # No background for meta area
            "completion-menu.meta.completion": "noinherit #808080",  # Unhighlighted help: gray, transparent bg
            "completion-menu.meta.completion.current": "noinherit #ffffff",  # Highlighted help: white, transparent bg
        }
    )

    # Configure prompt_toolkit with history, auto-completion, and styling
    from prompt_toolkit.key_binding import KeyBindings

    # No custom key bindings - use prompt_toolkit defaults
    # This gives us standard, predictable completion behavior:
    # - Tab: accept completion
    # - Arrows: navigate
    # - Enter: accept completion (if showing) then submit
    # - Backspace: auto-refilters
    kb = KeyBindings()

    # Custom prompt - just "> " with separator handled separately
    prompt_kwargs = {
        "message": "> ",  # Simple prompt
        "history": FileHistory(".repl_history"),
        "completer": completer,
        "complete_while_typing": True,  # Show completions as you type (standard behavior)
        "complete_in_thread": False,  # Sync completion for faster response
        "style": completion_style,
        "key_bindings": kb,  # Empty key bindings - use defaults
        "complete_style": "COLUMN",  # Single column - one command per line
        "reserve_space_for_menu": COMPLETION_MENU_HEIGHT,
    }

    # Patch click_repl to strip leading / from commands and add separators
    import click_repl._repl as repl_module
    from click_repl import ExitReplException

    # Defensive check: verify the function we're patching exists
    if not hasattr(repl_module, "_execute_internal_and_sys_cmds"):
        raise RuntimeError(
            "click_repl API has changed. This template requires click-repl>=0.3.0,<0.4.0. "
            "Please check requirements.txt and update the monkey-patch code."
        )

    # Save original function
    original_execute = repl_module._execute_internal_and_sys_cmds

    def execute_with_slash_stripping(
        command: str, allow_internal_commands: bool, allow_system_commands: bool
    ) -> None:
        """
        Wrapper that strips leading / before processing command.

        WARNING: This is a monkey-patch of click_repl and may break with library updates.
        Pin click-repl version in requirements.txt.

        Args:
            command: Command string to execute
            allow_internal_commands: Whether to allow internal commands
            allow_system_commands: Whether to allow system commands
        """
        # Check if agent mode is enabled
        agent_enabled = ConfigManager.get(config_dict, "agent.enabled", False)

        # Strip leading / if present (Claude Code style)
        if command.startswith("/"):
            command = command[1:]
        else:
            # No / prefix - could be free text for agent
            if agent_enabled and command.strip():
                # Future: Send to agent/LLM
                console.print()
                console.print(
                    "[yellow]Agent mode:[/yellow] Would send to LLM: " + command
                )
                console.print("[dim](Agent integration not yet implemented)[/dim]")
                console.print()
                return None

        # Try to execute the command
        try:
            result = original_execute(
                command, allow_internal_commands, allow_system_commands
            )
            # Just add blank line after output for spacing
            console.print()
            return result

        except click.exceptions.ClickException as e:
            # Handle Click exceptions (missing args, bad options, etc.) gracefully
            console.print()
            error_message = e.format_message()
            console.print(f"[red]Error:[/red] {error_message}")

            # Extract option names from error message if it's a missing option error
            if "Missing option" in error_message:
                # Try to extract the option names from the error (e.g., '--file' / '-f')
                import re

                option_match = re.search(r"'([^']+)'", error_message)
                if option_match:
                    option_name = option_match.group(1)
                    console.print()
                    console.print(
                        f"[dim]Example:[/dim] [cyan]/{command} {option_name} <value>[/cyan]"
                    )

            console.print()
            console.print(
                f"[dim]For full usage:[/dim] [cyan]/{command.split()[0]} --help[/cyan]"
            )
            console.print()
            return None

        except Exception as e:
            # Handle unknown command errors gracefully
            error_msg = str(e)
            if (
                "No such command" in error_msg
                or "no command named" in error_msg.lower()
            ):
                console.print()
                console.print(f"[red]Unknown command:[/red] {command}")
                console.print()
                console.print("[dim]Commands must start with /[/dim]")
                console.print(
                    "[dim]Try:[/dim] [cyan]/help[/cyan] to see available commands"
                )
                if not agent_enabled:
                    console.print(
                        "[dim]Tip: Enable agent mode in config to send free text to LLM[/dim]"
                    )
                console.print()
                return None
            else:
                # For other exceptions, show simplified error
                console.print()
                console.print(f"[red]Error:[/red] {str(e)}")
                console.print()
                return None

    # Temporarily replace the function
    repl_module._execute_internal_and_sys_cmds = execute_with_slash_stripping

    # Start REPL
    try:
        repl(context, prompt_kwargs=prompt_kwargs)
    except (KeyboardInterrupt, EOFError):
        # Handle Ctrl+C and Ctrl+D gracefully
        from repl_cli_template.ui.welcome import show_goodbye

        console.print()
        show_goodbye(console)
        sys.exit(0)
    except ExitReplException:
        # Clean exit from /quit or /exit command
        sys.exit(0)
    finally:
        # Restore original function
        repl_module._execute_internal_and_sys_cmds = original_execute


# Register commands
cli.add_command(help_command, name="help")
cli.add_command(quit_command, name="quit")
cli.add_command(exit_command, name="exit")
cli.add_command(config, name="config")
cli.add_command(process, name="process")


def main():
    """Entry point for the application."""
    cli(obj={})


if __name__ == "__main__":
    main()
