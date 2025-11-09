"""
Debug level control commands for REPL/CLI.

Provides /debug command to view and change debug level at runtime.
NO business logic - just updates config and logging.
"""

import logging
import click
from rich.console import Console

logger = logging.getLogger(__name__)


@click.command()
@click.argument(
    "level",
    type=click.Choice(["off", "info", "debug", "status"], case_sensitive=False),
    required=False,
)
@click.pass_context
def debug(ctx, level: str | None):
    """
    View or change debug level.

    \b
    Levels:
      off    - Minimal output (suppress LiteLLM INFO logs)
      info   - Normal output (show LiteLLM INFO logs)
      debug  - Full debug mode (verbose + LiteLLM debug)
      status - Show current debug level (default if no argument)

    \b
    Examples:
      /debug status  (or just: /debug)
      /debug off
      /debug info
      /debug debug
    """
    console: Console = ctx.obj["console"]
    config_dict = ctx.obj["config"]

    # Default to "status" if no level provided
    if level is None:
        level = "status"

    if level == "status":
        # Show current debug level
        current_level = ctx.obj.get("debug_level", "info")
        console.print(f"\n[bold]Current debug level:[/bold] {current_level}")
        console.print()
        console.print("[dim]Levels:[/dim]")
        console.print("  [cyan]off[/cyan]   - Minimal output (suppress LiteLLM INFO)")
        console.print(
            "  [cyan]info[/cyan]  - Normal output (show LiteLLM INFO) [default]"
        )
        console.print(
            "  [cyan]debug[/cyan] - Full debug mode (verbose + LiteLLM debug)"
        )
        console.print()
        console.print("[dim]Change level:[/dim] [cyan]/debug [off|info|debug][/cyan]")
        console.print()
        return

    # Set new debug level
    old_level = ctx.obj.get("debug_level", "info")
    logger.debug(f"[COMMAND] /debug {level} - old_level={old_level}")
    ctx.obj["debug_level"] = level

    # Update config dict (in-memory only, not saved to file)
    if "debug" not in config_dict:
        config_dict["debug"] = {}
    config_dict["debug"]["level"] = level

    # Update logging based on new level
    if level == "off":
        log_level = logging.WARNING
        # Suppress LiteLLM INFO logs
        logging.getLogger("litellm").setLevel(logging.WARNING)
        logging.getLogger("LiteLLM").setLevel(logging.WARNING)
        console.print(
            "\n[green]✓[/green] Debug level set to [bold]off[/bold] (minimal output)"
        )
    elif level == "info":
        log_level = logging.INFO
        # Reset LiteLLM to INFO
        logging.getLogger("litellm").setLevel(logging.INFO)
        logging.getLogger("LiteLLM").setLevel(logging.INFO)
        # Disable LiteLLM verbose mode
        try:
            import litellm

            litellm.set_verbose = False
        except ImportError:
            pass
        console.print(
            "\n[green]✓[/green] Debug level set to [bold]info[/bold] (normal output)"
        )
    elif level == "debug":
        log_level = logging.DEBUG
        # Enable LiteLLM debug mode
        try:
            import litellm

            litellm.set_verbose = True
        except ImportError:
            pass
        logging.getLogger("litellm").setLevel(logging.DEBUG)
        logging.getLogger("LiteLLM").setLevel(logging.DEBUG)
        console.print(
            "\n[green]✓[/green] Debug level set to [bold]debug[/bold] (full debug mode)"
        )

    # Update root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # IMPORTANT: Also update all existing handlers' levels (Issue #15)
    # Handlers have their own level setting that can filter messages
    # even if the logger's level allows them through
    logger.debug(f"→ updating root logger and all handlers to {logging.getLevelName(log_level)}")
    for handler in root_logger.handlers:
        handler.setLevel(log_level)
        logger.debug(f"  Updated {handler.__class__.__name__} to {logging.getLevelName(log_level)}")

    logger.info(f"[COMMAND] Debug level changed: {old_level} → {level}")
    console.print(f"[dim]Changed from:[/dim] {old_level} [dim]→[/dim] {level}\n")
