"""
System commands: help, quit, reload, etc.
"""

import logging
import click
from rich.console import Console
from rich.table import Table
from simple_agent.commands.common import APP_THEME, format_info

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


@click.command()
@click.pass_context
def help_command(context):
    """Show available commands and usage information."""
    console = _get_console(context)

    console.print()
    console.print("[bold cyan]Available Commands[/bold cyan]")
    console.print()

    # Create a table of commands
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description", style="white")

    # Get all commands from the CLI group
    if hasattr(context.parent, "command") and hasattr(
        context.parent.command, "commands"
    ):
        commands = context.parent.command.commands
        for name, cmd in sorted(commands.items()):
            if cmd.help:
                table.add_row(f"/{name}", cmd.help)
            else:
                table.add_row(f"/{name}", "No description available")

    console.print(table)
    console.print()
    console.print(format_info("For detailed help on a command: /command --help"))
    console.print()


@click.command()
@click.pass_context
def quit_command(context):
    """Exit the REPL."""
    from click_repl import ExitReplException

    console = _get_console(context)
    console.print()
    console.print("[bold yellow]Goodbye![/bold yellow]")
    raise ExitReplException()


# Alias for quit
@click.command()
@click.pass_context
def exit_command(context):
    """Exit the REPL (alias for quit)."""
    from click_repl import ExitReplException

    console = _get_console(context)
    console.print()
    console.print("[bold yellow]Goodbye![/bold yellow]")
    raise ExitReplException()


@click.command()
@click.option(
    "--model-pricing",
    "-m",
    is_flag=True,
    help="Refresh LiteLLM model pricing/context data from GitHub",
)
@click.pass_context
def refresh(context, model_pricing):
    """
    Refresh application data and caches.

    \b
    Options:
      --model-pricing (-m)  Fetch latest model pricing data from GitHub
                            (Requires internet connection)

    \b
    Examples:
      /refresh              (shows this help)
      /refresh --model-pricing  (fetch latest pricing from GitHub)
    """
    console = _get_console(context)
    logger.info("[COMMAND] /refresh - model_pricing={model_pricing}")

    if not model_pricing:
        # Show help if no option provided
        console.print()
        console.print("[bold]Refresh Options:[/bold]")
        console.print()
        console.print("  [cyan]--model-pricing[/cyan] (-m)")
        console.print("    Fetch the latest LiteLLM model pricing data from GitHub")
        console.print("    (includes model costs, context windows, etc.)")
        console.print()
        console.print("[dim]Example:[/dim] /refresh --model-pricing")
        console.print()
        return

    if model_pricing:
        logger.debug("Refreshing LiteLLM model pricing data")
        try:
            import httpx
            import json
            from pathlib import Path

            url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

            console.print(
                "\n[bold cyan]Fetching model pricing data from GitHub...[/bold cyan]"
            )
            logger.info(f"[COMMAND] Fetching model pricing from {url}")

            # Fetch from GitHub with timeout
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Find the backup file location
            import litellm

            backup_path = (
                Path(litellm.__file__).parent
                / "model_prices_and_context_window_backup.json"
            )

            # Write to backup file
            with open(backup_path, "w") as f:
                json.dump(data, f, indent=2)

            model_count = len(data)
            logger.info(
                f"[COMMAND] Successfully updated {model_count} models in pricing data"
            )

            console.print(
                f"[green]✓[/green] Updated pricing data: {model_count} models"
            )
            console.print(f"[dim]Saved to:[/dim] {backup_path}")
            console.print()

        except httpx.TimeoutException:
            logger.error(
                "[COMMAND] Model pricing refresh failed - Request timeout (10s)"
            )
            console.print("[red]✗[/red] Failed: Request timed out (10 seconds)")
            console.print("[dim]Check your internet connection[/dim]")
            console.print()
        except httpx.HTTPError as e:
            logger.error(
                f"[COMMAND] Model pricing refresh failed - HTTP error: {type(e).__name__}"
            )
            console.print(f"[red]✗[/red] Failed: {str(e)}")
            console.print("[dim]GitHub may be unavailable[/dim]")
            console.print()
        except Exception as e:
            logger.error(
                f"[COMMAND] Model pricing refresh failed - {type(e).__name__}: {str(e)}"
            )
            console.print(f"[red]✗[/red] Failed: {type(e).__name__}: {str(e)}")
            console.print()
