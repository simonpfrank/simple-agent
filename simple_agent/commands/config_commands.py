"""
Configuration management commands.
"""

import click
import logging
import yaml

from rich.panel import Panel
from rich.syntax import Syntax

from simple_agent.core.config_manager import ConfigManager
from simple_agent.commands.common import (
    get_console,
    format_success,
    format_error,
    format_info,
)

logger = logging.getLogger(__name__)


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


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

    logger.info(f"[COMMAND] /config show - resolve={resolve}")
    logger.debug(f"config_show(resolve={resolve})")

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            logger.warning("[COMMAND] Config show: no configuration loaded")
            console.print(format_info("No configuration loaded"))
            return

        # If --resolve flag is set, create temporary copy with substituted values
        if resolve:
            display_config = ConfigManager.substitute_env_vars(config_dict)
            logger.debug("Substituting environment variables for display")
            console.print(
                "[dim yellow]⚠ Showing resolved values (secrets visible)[/dim yellow]"
            )
        else:
            # Default: show placeholders (safe)
            display_config = config_dict
            logger.debug("Displaying config with placeholders (safe)")
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

        logger.info("[COMMAND] Config displayed successfully")
        logger.debug(
            f"config_show() completed, config_lines={len(config_yaml.splitlines())}"
        )
        console.print()
        console.print(panel)
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config show failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(str(e)))
        raise click.Abort()


@config.command("load")
@click.option("--file", "-f", required=True, help="Path to config file")
@click.pass_context
def config_load(context, file):
    """Load configuration from YAML file."""
    console = get_console(context)

    logger.info(f"[COMMAND] /config load - file={file}")
    logger.debug(f"ConfigManager.load({file})")

    try:
        # Load config
        config_dict = ConfigManager.load(file)
        logger.debug(
            f"ConfigManager.load() returned config with {len(config_dict)} top-level keys"
        )

        # Merge with defaults
        logger.debug("merge_with_defaults()")
        config_dict = ConfigManager.merge_with_defaults(config_dict)
        logger.debug(f"merge_with_defaults() completed")

        # Update context
        context.obj["config"] = config_dict
        context.obj["config_file"] = file

        logger.info(f"[COMMAND] Configuration loaded from: {file}")
        console.print()
        console.print(format_success(f"Configuration loaded from: {file}"))
        console.print()

    except FileNotFoundError:
        error_msg = f"Config file not found: {file}"
        logger.error(
            f"[COMMAND] Config load failed - file not found: {file}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(error_msg))
        raise click.Abort()

    except ValueError as e:
        # Invalid YAML or wrong type
        logger.error(
            f"[COMMAND] Config load failed - invalid config file: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(str(e)))
        raise click.Abort()

    except Exception as e:
        error_msg = f"Failed to load config: {str(e)}"
        logger.error(
            f"[COMMAND] Config load failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(error_msg))
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

    logger.info(f"[COMMAND] /config save - file={file}")

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            logger.warning("[COMMAND] Config save: no configuration to save")
            console.print(format_error("No configuration to save"))
            raise click.Abort()

        # Use default config file if not specified
        if file is None:
            file = context.obj.get("config_file", "config.yaml")
            logger.debug(f"Using default config file: {file}")

        logger.debug(f"ConfigManager.save(config, {file})")
        # Save config
        ConfigManager.save(config_dict, file)
        logger.info(f"[COMMAND] Configuration saved to: {file}")
        logger.debug(f"ConfigManager.save() completed successfully")

        console.print()
        console.print(format_success(f"Configuration saved to: {file}"))
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config save failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to save config: {str(e)}"))
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

    logger.info(f"[COMMAND] /config set - key={key}, value={value}")
    logger.debug(f"ConfigManager.set({key}, {value})")

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            logger.warning("[COMMAND] Config set: no configuration loaded")
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Set the value
        ConfigManager.set(config_dict, key, value)
        logger.info(f"[COMMAND] Config value set: {key}={value}")
        logger.debug(f"ConfigManager.set() completed successfully")

        console.print()
        console.print(format_success(f"Set {key} = {value}"))
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config set failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to set config: {str(e)}"))
        raise click.Abort()


@config.command("get")
@click.option(
    "--key", "-k", required=True, help="Config key (dot notation, e.g., logging.level)"
)
@click.pass_context
def config_get(context, key):
    """Get a configuration value."""
    console = get_console(context)

    logger.info(f"[COMMAND] /config get - key={key}")
    logger.debug(f"ConfigManager.get({key})")

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            logger.warning("[COMMAND] Config get: no configuration loaded")
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get the value
        value = ConfigManager.get(config_dict, key, default=None)
        logger.debug(f"ConfigManager.get() returned: {value}")

        if value is None:
            logger.warning(f"[COMMAND] Config key not found: {key}")
            console.print()
            console.print(format_error(f"Key not found: {key}"))
            console.print()
            return

        logger.info(f"[COMMAND] Config value retrieved: {key}")
        console.print()
        console.print(f"[bold cyan]{key}[/bold cyan] = [green]{value}[/green]")
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config get failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to get config: {str(e)}"))
        raise click.Abort()


@config.command("reset")
@click.option("--key", "-k", required=True, help="Config key to reset to default")
@click.pass_context
def config_reset(context, key):
    """Reset a configuration value to its default."""
    console = get_console(context)

    logger.info(f"[COMMAND] /config reset - key={key}")

    try:
        config_dict = context.obj.get("config", {})

        if not config_dict:
            logger.warning("[COMMAND] Config reset: no configuration loaded")
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get default value
        logger.debug(f"ConfigManager.get_defaults()")
        defaults = ConfigManager.get_defaults()
        default_value = ConfigManager.get(defaults, key, default=None)
        logger.debug(f"get_defaults() returned default: {default_value}")

        if default_value is None:
            logger.warning(f"[COMMAND] No default value found for key: {key}")
            console.print()
            console.print(format_error(f"No default value found for: {key}"))
            console.print()
            return

        # Set to default value
        logger.debug(f"ConfigManager.set({key}, {default_value})")
        ConfigManager.set(config_dict, key, default_value)
        logger.info(f"[COMMAND] Config reset: {key} = {default_value}")
        logger.debug(f"ConfigManager.set() completed successfully")

        console.print()
        console.print(format_success(f"Reset {key} to default: {default_value}"))
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config reset failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to reset config: {str(e)}"))
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

    logger.info(f"[COMMAND] /config set-path - type={type}, path={path}")

    try:
        config_dict = context.obj.get("config", {})

        if config_dict is None:
            logger.warning("[COMMAND] Config set-path: no configuration loaded")
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Valid path types
        valid_types = ["prompts", "tools", "agents", "logs", "data"]

        if type not in valid_types:
            logger.warning(f"[COMMAND] Config set-path: invalid type '{type}'")
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
            logger.debug("Created 'paths' section in config")

        # Set the path
        config_dict["paths"][type] = path
        logger.info(f"[COMMAND] Path set: {type}={path}")

        console.print()
        console.print(format_success(f"Set {type} path = {path}"))
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config set-path failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to set path: {str(e)}"))
        raise click.Abort()


@config.command("show-paths")
@click.pass_context
def config_show_paths(context):
    """Display all configured paths."""
    console = get_console(context)

    logger.info("[COMMAND] /config show-paths")
    logger.debug("config_show_paths()")

    try:
        config_dict = context.obj.get("config", {})

        if config_dict is None:
            logger.warning("[COMMAND] Config show-paths: no configuration loaded")
            console.print(format_error("No configuration loaded"))
            raise click.Abort()

        # Get paths section
        paths = config_dict.get("paths", {})

        if not paths:
            # Show default paths if no paths configured
            logger.debug("get_defaults() to retrieve default paths")
            defaults = ConfigManager.get_defaults()
            paths = defaults.get("paths", {})
            logger.debug(f"get_defaults() returned {len(paths)} default paths")

            if not paths:
                logger.warning("[COMMAND] No paths configured (using defaults)")
                console.print()
                console.print(format_info("No paths configured"))
                console.print()
                return

        logger.info(f"[COMMAND] Displaying {len(paths)} configured path(s)")
        console.print()
        console.print("[bold cyan]Configured Paths:[/bold cyan]")
        console.print()

        for path_type, path_value in sorted(paths.items()):
            console.print(f"  [green]{path_type}[/green]: {path_value}")

        logger.debug(f"config_show_paths() completed")
        console.print()

    except Exception as e:
        logger.error(
            f"[COMMAND] Config show-paths failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(format_error(f"Failed to show paths: {str(e)}"))
        raise click.Abort()
