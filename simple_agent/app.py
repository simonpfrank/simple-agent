"""New entry point using cli_repl_kit.

This is a parallel entry point that uses cli_repl_kit instead of click_repl.
The old app.py continues to work unchanged.
"""

import logging
import os
import sys
from pathlib import Path

# SECURITY: Prevent LiteLLM from making unauthorized API calls
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

# Add cli_repl_kit submodule to path
sys.path.insert(0, str(Path(__file__).parent / "lib" / "cli_repl_kit"))

import click
from rich.console import Console

from cli_repl_kit import REPL

from simple_agent.commands.common import APP_THEME
from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.logging_setup import setup_logging
from simple_agent.core.repl_context import create_context_factory
from simple_agent.core.runtime_config import set_config
from simple_agent.plugins.agent_mode import create_agent_callback
from simple_agent.plugins.core_commands import CoreCommandsPlugin


# Initialize logger
logger = logging.getLogger(__name__)

# Application metadata
APP_NAME = "Simple Agent"
APP_VERSION = "0.1.0"
DEFAULT_CONFIG = "config.yaml"


def main() -> None:
    """Entry point using cli_repl_kit."""
    # Load environment variables
    ConfigManager.load_env()

    # Load configuration
    config_file = DEFAULT_CONFIG
    if Path(config_file).exists():
        config_dict = ConfigManager.load(config_file)
        config_dict = ConfigManager.merge_with_defaults(config_dict)
    else:
        config_dict = ConfigManager.get_defaults()
        print(f"[dim]Config file {config_file} not found, using defaults[/dim]")

    # Get debug level (can be overridden via CLI later)
    debug_level = ConfigManager.get(config_dict, "debug.level", "info")

    # Setup logging
    log_file = ConfigManager.get(config_dict, "logging.file", "logs/app.log")
    log_level_map = {"off": "WARNING", "debug": "DEBUG", "info": "INFO"}
    log_level = log_level_map.get(debug_level, "INFO")

    # Only enable console logging if running a CLI command (not REPL)
    console_logging = len(sys.argv) > 1
    setup_logging(log_file, log_level, console_enabled=console_logging)

    # Set global runtime config
    set_config(config_dict)

    # Create console
    console = Console(theme=APP_THEME)

    # Create context factory for dependency injection
    context_factory = create_context_factory(
        console=console,
        config=config_dict,
        config_file=config_file,
        debug_level=debug_level,
    )

    # Create CLI group
    cli = click.Group()

    # Register commands via plugin
    plugin = CoreCommandsPlugin()
    plugin.register(cli, context_factory)

    # Get REPL config path
    repl_config_path = Path(__file__).parent / "repl_config.yaml"

    # Create agent callback for free text routing
    agent_callback = create_agent_callback(context_factory)

    # Create REPL instance
    repl = REPL(
        app_name=APP_NAME,
        context_factory=context_factory,
        cli_group=cli,
        plugin_group="simple_agent.plugins",  # Entry point group (not used yet)
        config_path=str(repl_config_path) if repl_config_path.exists() else None,
        agent_callback=agent_callback,
    )

    # Get prompt from config
    prompt_text = ConfigManager.get(config_dict, "ui.prompt", "> ")

    # Check if agent mode is enabled
    agent_enabled = ConfigManager.get(config_dict, "agent.enabled", False)

    # Start REPL or execute CLI command
    try:
        repl.start(prompt_text=prompt_text, enable_agent_mode=agent_enabled)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
