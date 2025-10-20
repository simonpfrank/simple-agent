"""
System commands: help, quit, reload, etc.
"""

import click
from rich.console import Console
from rich.table import Table
from repl_cli_template.ui.styles import APP_THEME, format_info
from repl_cli_template.ui.welcome import show_goodbye


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
    show_goodbye(console)
    raise ExitReplException()


# Alias for quit
@click.command()
@click.pass_context
def exit_command(context):
    """Exit the REPL (alias for quit)."""
    from click_repl import ExitReplException

    console = _get_console(context)
    show_goodbye(console)
    raise ExitReplException()
