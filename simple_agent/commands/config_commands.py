"""
Configuration management commands.
"""

import click
import logging
import yaml

from rich.panel import Panel
from rich.syntax import Syntax

from simple_agent.core.config_manager import ConfigManager
from simple_agent.commands.common import get_console
from simple_agent.ui.styles import (
    format_success,
    format_error,
    format_info,
)

logger = logging.getLogger(__name__)


@click.group()
def config():
    """Configuration management commands."""
    pass


@config.command("show")
@click.option(
    "--resolve",
    "-r",
    is_flag=True,
    default=False,
    help="Resolve environment variables for display (shows actual values)",
)
@click.pass_context
def config_show(context, resolve):
    """Display current configuration."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_info("No configuration loaded"))
            return

        # If --resolve flag is set, create temporary copy with substituted values
        if resolve:
            display_config = ConfigManager.substitute_env_vars(config_dict)
            console.print(
                "[dim yellow]⚠ Showing resolved values (secrets visible)[/dim yellow]"
            )
        else:
            # Default: show placeholders (safe)
            display_config = config_dict
            console.print("[dim]Showing config with placeholders (safe)[/dim]")

        # Convert config to YAML for pretty display
        config_yaml = yaml.dump(
            display_config, default_flow_style=False, sort_keys=False
        )

        # Syntax highlighting
        syntax = Syntax(config_yaml, "yaml", theme="monokai", line_numbers=False)

        # Display in a panel
        panel = Panel(
            syntax,
            title="[bold cyan]Current Configuration[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        console.print()
        console.print(panel)
        console.print()

    except Exception as e:
        console.print(format_error(str(e)))
        logger.exception(f"Failed to display config: {str(e)}")
        raise click.Abort()


@config.command("load")
@click.option("--file", "-f", required=True, help="Path to config file")
@click.pass_context
def config_load(context, file):
    """Load configuration from YAML file."""
    console = get_console(context)

    try:
        # Load config
        config_dict = ConfigManager.load(file)

        # Merge with defaults
        config_dict = ConfigManager.merge_with_defaults(config_dict)

        # Update context
        context.obj["config"] = config_dict
        context.obj["config_file"] = file

        console.print()
        console.print(format_success(f"Configuration loaded from: {file}"))
        console.print()

    except FileNotFoundError:
        error_msg = f"Config file not found: {file}"
        console.print(format_error(error_msg))
        logger.error(error_msg)
        raise click.Abort()

    except ValueError as e:
        # Invalid YAML or wrong type
        console.print(format_error(str(e)))
        logger.exception(f"Invalid config file: {file}")
        raise click.Abort()

    except Exception as e:
        error_msg = f"Failed to load config: {str(e)}"
        console.print(format_error(error_msg))
        logger.exception(error_msg)
        raise click.Abort()


@config.command("save")
@click.option(
    "--file",
    "-f",
    default=None,
    help="Path to save config file (defaults to loaded config file)",
)
@click.pass_context
def config_save(context, file):
    """Save current configuration to YAML file."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_error("No configuration to save"))
            raise click.Abort()

        # Use default config file if not specified
        if file is None:
            file = context.obj.get("config_file", "config.yaml")

        # Save config
        ConfigManager.save(config_dict, file)

        console.print()
        console.print(format_success(f"Configuration saved to: {file}"))
        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to save config: {str(e)}"))
        logger.exception(f"Failed to save config: {str(e)}")
        raise click.Abort()


@config.command("set")
@click.option(
    "--key", "-k", required=True, help="Config key (dot notation, e.g., logging.level)"
)
@click.option("--value", "-v", required=True, help="Config value")
@click.pass_context
def config_set(context, key, value):
    """Set a configuration value."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Set the value
        ConfigManager.set(config_dict, key, value)

        console.print()
        console.print(format_success(f"Set {key} = {value}"))
        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to set config: {str(e)}"))
        logger.exception(f"Failed to set config: {str(e)}")
        raise click.Abort()


@config.command("get")
@click.option(
    "--key", "-k", required=True, help="Config key (dot notation, e.g., logging.level)"
)
@click.pass_context
def config_get(context, key):
    """Get a configuration value."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get the value
        value = ConfigManager.get(config_dict, key, default=None)

        if value is None:
            console.print()
            console.print(format_error(f"Key not found: {key}"))
            console.print()
            return

        console.print()
        console.print(f"[bold cyan]{key}[/bold cyan] = [green]{value}[/green]")
        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to get config: {str(e)}"))
        logger.exception(f"Failed to get config: {str(e)}")
        raise click.Abort()


@config.command("reset")
@click.option("--key", "-k", required=True, help="Config key to reset to default")
@click.pass_context
def config_reset(context, key):
    """Reset a configuration value to its default."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get default value
        defaults = ConfigManager.get_defaults()
        default_value = ConfigManager.get(defaults, key, default=None)

        if default_value is None:
            console.print()
            console.print(format_error(f"No default value found for: {key}"))
            console.print()
            return

        # Set to default value
        ConfigManager.set(config_dict, key, default_value)

        console.print()
        console.print(format_success(f"Reset {key} to default: {default_value}"))
        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to reset config: {str(e)}"))
        logger.exception(f"Failed to reset config: {str(e)}")
        raise click.Abort()


@config.command("set-path")
@click.option(
    "--type", "-t", required=True, help="Path type (prompts, tools, agents, logs)"
)
@click.option("--path", "-p", required=True, help="Path value")
@click.pass_context
def config_set_path(context, type, path):
    """Set a configurable path."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if config_dict is None:
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Valid path types
        valid_types = ["prompts", "tools", "agents", "logs", "data"]

        if type not in valid_types:
            console.print()
            console.print(
                format_error(
                    f"Invalid path type: {type}. Valid types: {', '.join(valid_types)}"
                )
            )
            console.print()
            return

        # Initialize paths section if it doesn't exist
        if "paths" not in config_dict:
            config_dict["paths"] = {}

        # Set the path
        config_dict["paths"][type] = path

        console.print()
        console.print(format_success(f"Set {type} path = {path}"))
        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to set path: {str(e)}"))
        logger.exception(f"Failed to set path: {str(e)}")
        raise click.Abort()


@config.command("show-paths")
@click.pass_context
def config_show_paths(context):
    """Display all configured paths."""
    console = get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if config_dict is None:
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get paths section
        paths = config_dict.get("paths", {})

        if not paths:
            # Show default paths if no paths configured
            defaults = ConfigManager.get_defaults()
            paths = defaults.get("paths", {})

            if not paths:
                console.print()
                console.print(format_info("No paths configured"))
                console.print()
                return

        console.print()
        console.print("[bold cyan]Configured Paths:[/bold cyan]")
        console.print()

        for path_type, path_value in sorted(paths.items()):
            console.print(f"  [green]{path_type}[/green]: {path_value}")

        console.print()

    except Exception as e:
        console.print(format_error(f"Failed to show paths: {str(e)}"))
        logger.exception(f"Failed to show paths: {str(e)}")
        raise click.Abort()
