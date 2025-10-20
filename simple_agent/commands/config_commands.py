"""
Configuration management commands.
"""

import click
import logging
import yaml

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from repl_cli_template.core.config_manager import ConfigManager
from repl_cli_template.ui.styles import (
    APP_THEME,
    format_success,
    format_error,
    format_info,
)

logger = logging.getLogger(__name__)


def _get_console(context: click.Context) -> Console:
    """
    Get console from context with fallback.

    Args:
        context: Click context object

    Returns:
        Console instance from context, or new instance if not found
    """
    return context.obj.get("console", Console(theme=APP_THEME))


@click.group()
def config():
    """Configuration management commands."""
    pass


@config.command("show")
@click.pass_context
def config_show(context):
    """Display current configuration."""
    console = _get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_info("No configuration loaded"))
            return

        # Convert config to YAML for pretty display
        config_yaml = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)

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
    console = _get_console(context)

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
@click.option("--file", "-f", required=True, help="Path to save config file")
@click.pass_context
def config_save(context, file):
    """Save current configuration to YAML file."""
    console = _get_console(context)

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            console.print(format_error("No configuration to save"))
            raise click.Abort()

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
    console = _get_console(context)

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
