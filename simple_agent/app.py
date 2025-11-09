"""
Main entry point for REPL/CLI application.
"""

import logging
import os
import sys
from pathlib import Path

# SECURITY: Prevent LiteLLM from making unauthorized API calls to fetch model pricing data
# LiteLLM fetches https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
# during import unless this env var is set. We use the bundled backup file instead.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

import click

from click_repl import repl
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.logging_setup import setup_logging
from simple_agent.core.agent_manager import AgentManager
from simple_agent.core.tool_manager import ToolManager
from simple_agent.ui.welcome import show_welcome
from simple_agent.ui.styles import APP_THEME
from simple_agent.commands.system_commands import (
    help_command,
    quit_command,
    exit_command,
    refresh,
)
from simple_agent.commands.config_commands import config
from simple_agent.commands.agent_commands import agent
from simple_agent.commands.inspection_commands import prompt, response
from simple_agent.commands.debug_commands import debug
from simple_agent.commands.history_commands import history
from simple_agent.commands.tool_commands import tool
from simple_agent.commands.token_stats_commands import token
from simple_agent.commands.collection_commands import collection
from simple_agent.commands.flow_commands_cli import flow

# Initialize console
console = Console(theme=APP_THEME)

# Initialize logger (used throughout app.py)
logger = logging.getLogger(__name__)

# Application metadata
APP_NAME = "Simple Agent"
APP_VERSION = "0.1.0"
DEFAULT_CONFIG = "config.yaml"

# REPL UI constants
COMPLETION_MENU_HEIGHT = 8  # Number of lines reserved for completion menu
CONSOLE_LOG_LEVEL = logging.WARNING  # Log level for console in CLI mode


@click.group(invoke_without_command=True)
@click.option("--config", "-c", default=DEFAULT_CONFIG, help="Path to config file")
@click.option("--repl-mode", is_flag=True, default=False, help="Start in REPL mode")
@click.option(
    "--debug",
    "-d",
    type=click.Choice(["off", "info", "debug"], case_sensitive=False),
    default=None,
    help="Debug level: off (minimal), info (normal), debug (verbose). Overrides config setting.",
)
@click.pass_context
def cli(context, config, repl_mode, debug):
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
        # Load .env file first to populate environment variables
        ConfigManager.load_env()

        if Path(config).exists():
            config_dict = ConfigManager.load(config)
            config_dict = ConfigManager.merge_with_defaults(config_dict)
        else:
            # Use defaults if config file doesn't exist
            config_dict = ConfigManager.get_defaults()
            console.print("[dim]Config file not found, using defaults[/dim]")

        # CLI debug flag overrides config setting
        if debug is not None:
            if "debug" not in config_dict:
                config_dict["debug"] = {}
            config_dict["debug"]["level"] = debug

        # Get debug level (from CLI flag or config)
        debug_level = config_dict.get("debug", {}).get("level", "info")
        context.obj["debug_level"] = debug_level

        # NOTE: We do NOT substitute env vars here globally
        # Config dict keeps placeholders (${VAR}) to avoid storing secrets
        # Substitution happens at point-of-use (e.g., when creating models)

        context.obj["config"] = config_dict
        context.obj["config_file"] = config

    except Exception as e:
        console.print(f"[error]Error loading config:[/error] {str(e)}")
        sys.exit(1)

    # Setup logging
    log_file = ConfigManager.get(config_dict, "logging.file", "logs/app.log")

    # Set log level based on debug level
    if debug_level == "off":
        log_level = "WARNING"  # Minimal output
    elif debug_level == "debug":
        log_level = "DEBUG"  # Full debug mode
    else:  # "info" is default
        log_level = ConfigManager.get(config_dict, "logging.level", "INFO")

    # Enable console logging only if NOT in REPL mode
    console_enabled = context.invoked_subcommand is not None

    setup_logging(log_file, log_level, console_enabled)

    # Control LiteLLM logging based on debug level
    import logging as std_logging

    if debug_level == "off":
        # Suppress LiteLLM INFO logs
        std_logging.getLogger("litellm").setLevel(std_logging.WARNING)
        std_logging.getLogger("LiteLLM").setLevel(std_logging.WARNING)
    elif debug_level == "debug":
        # Enable LiteLLM debug mode
        os.environ["LITELLM_LOG"] = "DEBUG"
    # For "info" level, use default LiteLLM logging (INFO)

    # Set runtime config for tools and components to access
    from simple_agent.core.runtime_config import set_config

    # Only log first-time initialization (not on every command re-invocation in REPL mode)
    is_first_run = "agent_manager" not in context.obj
    if is_first_run:
        logger.debug("→ First-time initialization")
        logger.info("Setting configuration")
    set_config(config_dict)

    # Initialize ToolManager
    # IMPORTANT: Only create ToolManager once in REPL mode
    if "tool_manager" not in context.obj:
        if is_first_run:
            logger.info("Loading tool manager")
        tool_manager = ToolManager(auto_load_builtin=True)
        context.obj["tool_manager"] = tool_manager

    # Initialize AgentManager (business logic)
    # IMPORTANT: Only create AgentManager once in REPL mode
    # click-repl may re-invoke cli() for each command, so check if it exists
    if "agent_manager" not in context.obj:
        if is_first_run:
            logger.info("Loading Agent manager")
        agent_manager = AgentManager(config_dict)
        agent_manager.tool_manager = context.obj["tool_manager"]
        context.obj["agent_manager"] = agent_manager

        # Load agents from config (NOW that tool_manager is set)
        logger.info("Loading agents")
        agent_manager._load_agents_from_config()

        # Auto-load agents from config/agents/ directory (if enabled in config)
        auto_load_agents = ConfigManager.get(
            config_dict, "agents.auto_load_from_directory", True
        )
        if auto_load_agents:
            agents_dir = "config/agents"
            if os.path.exists(agents_dir):
                count = agent_manager.load_agents_from_directory(agents_dir)
                if count > 0:
                    logger.info(f"Auto-loaded {count} agents from {agents_dir}")
            else:
                logger.debug(f"Agents directory not found: {agents_dir}")

    # Initialize CollectionManager (RAG)
    if "collection_manager" not in context.obj:
        if is_first_run:
            logger.info("Loading rag")
        from simple_agent.rag.collection_manager import CollectionManager

        collections_dir = ConfigManager.get(
            config_dict, "rag.collections_dir", "./chroma_db"
        )
        collection_manager = CollectionManager(collections_dir)
        context.obj["collection_manager"] = collection_manager

    # Initialize FlowManager (Multi-Agent Orchestration)
    if "flow_manager" not in context.obj:
        if is_first_run:
            logger.info("Loading flow")
        from simple_agent.orchestration.flow_manager import FlowManager

        flows_dir = ConfigManager.get(
            config_dict, "orchestration.flows_dir", "config/flows"
        )
        flow_manager = FlowManager(
            agent_manager=context.obj["agent_manager"], flows_dir=flows_dir
        )
        context.obj["flow_manager"] = flow_manager

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
    logger.info("Loading REPL UI")
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
    from simple_agent.ui.completion import SlashCommandCompleter

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
            logger.error(error_msg)
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
        from simple_agent.ui.welcome import show_goodbye

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
cli.add_command(refresh, name="refresh")
cli.add_command(config, name="config")
cli.add_command(agent, name="agent")
cli.add_command(prompt, name="prompt")
cli.add_command(response, name="response")
cli.add_command(debug, name="debug")
cli.add_command(history, name="history")
cli.add_command(tool, name="tool")
cli.add_command(token, name="token")
cli.add_command(collection, name="collection")
cli.add_command(flow, name="flow")


def main():
    """Entry point for the application."""
    cli(obj={})


if __name__ == "__main__":
    logger = logging.getLogger("simple_agent.app")
    main()
