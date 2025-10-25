"""
Tool management commands for REPL/CLI.

Provides /tool command group for managing tools.
"""

import click
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from simple_agent.ui.styles import APP_THEME

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
@click.pass_context
def tool(ctx):
    """Tool management commands."""
    pass


@tool.command("list")
@click.pass_context
def tool_list(ctx):
    """
    List all available tools.

    Shows all tools registered in the tool manager.

    Examples:
        /tool list
    """
    console = _get_console(ctx)
    tool_manager = ctx.obj.get("tool_manager")

    if not tool_manager:
        console.print("[red]Error:[/red] Tool manager not initialized\n")
        return

    # Get list of tools
    tools = tool_manager.list_tools()

    if not tools:
        console.print()
        console.print("[yellow]No tools registered.[/yellow]")
        console.print()
        return

    # Create table for tools
    table = Table(title="Available Tools")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Count", style="dim")

    for tool_name in sorted(tools):
        table.add_row(tool_name, "")

    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Total: {len(tools)} tools[/dim]")
    console.print(f"[dim]Use [cyan]/tool info --name <tool>[/cyan] for details[/dim]\n")


@tool.command("info")
@click.option("--name", "-n", required=True, help="Tool name")
@click.pass_context
def tool_info(ctx, name: str):
    """
    Display detailed information about a tool.

    Shows tool description, inputs, and output type.

    Examples:
        /tool info --name add
        /tool info -n calculator
    """
    console = _get_console(ctx)
    tool_manager = ctx.obj.get("tool_manager")

    if not tool_manager:
        console.print("[red]Error:[/red] Tool manager not initialized\n")
        return

    try:
        # Get tool information
        info = tool_manager.get_tool_info(name)

        # Build info display
        console.print()
        console.print(f"[bold cyan]Tool:[/bold cyan] {info['name']}")
        console.print()
        console.print(f"[bold]Description:[/bold]")
        console.print(f"  {info.get('description', 'No description')}")
        console.print()

        # Show inputs
        inputs = info.get("inputs", {})
        if inputs:
            console.print(f"[bold]Inputs:[/bold]")
            for param_name, param_type in inputs.items():
                console.print(f"  • {param_name}: {param_type}")
            console.print()

        # Show output type
        output_type = info.get("output_type", "unknown")
        console.print(f"[bold]Output Type:[/bold] {output_type}")
        console.print()

    except KeyError as e:
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
        console.print(f"[dim]Use [cyan]/tool list[/cyan] to see available tools[/dim]\n")
