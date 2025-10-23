"""
Inspection commands for REPL/CLI.

Provides /prompt and /response command groups for debugging and inspection.
NO business logic - displays data from AgentManager.
"""

import click
from rich.console import Console
from rich.panel import Panel


@click.group()
@click.pass_context
def prompt(ctx):
    """Prompt inspection commands."""
    pass


@prompt.command()
@click.pass_context
def show(ctx):
    """
    Display the last formatted prompt sent to LLM.

    Examples:
        /prompt show
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    if not agent_manager.last_prompt:
        console.print("[yellow]No prompts yet.[/yellow] Run an agent first.\n")
        return

    console.print()
    console.print(
        Panel(
            f"[bold]Agent:[/bold] {agent_manager.last_agent}\n\n"
            f"[bold]User Prompt:[/bold]\n{agent_manager.last_prompt}",
            title="Last Prompt (Formatted)",
            border_style="cyan",
        )
    )
    console.print()


@prompt.command()
@click.pass_context
def raw(ctx):
    """
    Display the raw prompt template.

    Note: Currently shows the same as 'show' - template system is Phase 1.3.

    Examples:
        /prompt raw
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    if not agent_manager.last_prompt:
        console.print("[yellow]No prompts yet.[/yellow] Run an agent first.\n")
        return

    # For now, raw is the same as formatted (until Jinja2 templates in Phase 1.3)
    console.print()
    console.print(
        Panel(
            f"[bold]Agent:[/bold] {agent_manager.last_agent}\n\n"
            f"[bold]Raw Prompt:[/bold]\n{agent_manager.last_prompt}\n\n"
            f"[dim]Note: Template variables (Jinja2) coming in Phase 1.3[/dim]",
            title="Last Prompt (Raw)",
            border_style="yellow",
        )
    )
    console.print()


@click.group()
@click.pass_context
def response(ctx):
    """Response inspection commands."""
    pass


@response.command()
@click.pass_context
def show(ctx):
    """
    Display the last formatted agent response.

    Examples:
        /response show
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    if not agent_manager.last_response:
        console.print("[yellow]No responses yet.[/yellow] Run an agent first.\n")
        return

    console.print()
    console.print(
        Panel(
            f"[bold]Agent:[/bold] {agent_manager.last_agent}\n\n"
            f"[bold]Response:[/bold]\n{agent_manager.last_response}",
            title="Last Response (Formatted)",
            border_style="green",
        )
    )
    console.print()


@response.command()
@click.pass_context
def raw(ctx):
    """
    Display the raw agent response.

    Note: Currently shows the same as 'show' - metadata tracking is future work.

    Examples:
        /response raw
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    if not agent_manager.last_response:
        console.print("[yellow]No responses yet.[/yellow] Run an agent first.\n")
        return

    # For now, raw is the same as formatted (metadata tracking could be added later)
    console.print()
    console.print(
        Panel(
            f"[bold]Agent:[/bold] {agent_manager.last_agent}\n\n"
            f"[bold]Raw Response:[/bold]\n{agent_manager.last_response}\n\n"
            f"[dim]Note: Token usage and timing metadata could be added in future[/dim]",
            title="Last Response (Raw)",
            border_style="yellow",
        )
    )
    console.print()
