"""
Agent tool management commands for REPL/CLI.

Provides commands to list, add, and remove tools from agents.
"""

import logging

import click
from rich.console import Console

logger = logging.getLogger("simple_agent.commands.agent_tools")


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


def register_tool_commands(agent_group: click.Group) -> None:
    """Register tool management commands on the agent group."""

    @agent_group.command()
    @click.argument("name")
    @click.pass_context
    def tools(ctx: click.Context, name: str) -> None:
        """
        List all tools attached to an agent.

        Examples:
            /agent tools my_agent
            /agent tools default
        """
        console: Console = ctx.obj["console"]
        agent_manager = ctx.obj["agent_manager"]

        logger.info(f"[COMMAND] /agent tools - name={name}")
        logger.debug(f"get_agent_tools({name})")

        try:
            tool_names = agent_manager.get_agent_tools(name)
            logger.debug(
                f"get_agent_tools() returned {len(tool_names)} tools: {tool_names}"
            )
            logger.info(f"[COMMAND] Listed {len(tool_names)} tool(s) for agent '{name}'")

            if not tool_names:
                console.print()
                console.print(f"[yellow]Agent '{name}' has no tools attached.[/yellow]")
                console.print()
                return

            console.print()
            console.print(f"[bold]Tools for agent '{name}':[/bold]")
            for tool_name in sorted(tool_names):
                console.print(f"  • {tool_name}")
            console.print()
            console.print(f"[dim]Total: {len(tool_names)} tools[/dim]")
            console.print(
                "[dim]Use [cyan]/tool info --name <tool>[/cyan] for tool details[/dim]\n"
            )

        except KeyError as e:
            logger.error(
                f"[COMMAND] Tools command failed - agent '{name}' not found",
                exc_info=_should_log_traceback(),
            )
            console.print()
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print()

    @agent_group.command("add-tool")
    @click.argument("name")
    @click.argument("tool")
    @click.pass_context
    def add_tool(ctx: click.Context, name: str, tool: str) -> None:
        """
        Add a tool to an existing agent.

        Examples:
            /agent add-tool my_agent calculator
            /agent add-tool default add
        """
        console: Console = ctx.obj["console"]
        agent_manager = ctx.obj["agent_manager"]

        logger.info(f"[COMMAND] /agent add-tool - name={name}, tool={tool}")
        logger.debug(f"add_tool_to_agent({name}, {tool})")

        try:
            agent_manager.add_tool_to_agent(name, tool)
            logger.info(f"[COMMAND] Tool '{tool}' added to agent '{name}'")
            logger.debug("add_tool_to_agent() completed successfully")
            console.print()
            console.print(f"[green]✓[/green] Added tool '{tool}' to agent '{name}'")
            console.print()

        except KeyError as e:
            logger.error(
                f"[COMMAND] Add-tool failed - {type(e).__name__}: {str(e)}",
                exc_info=_should_log_traceback(),
            )
            console.print()
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print()

    @agent_group.command("remove-tool")
    @click.argument("name")
    @click.argument("tool")
    @click.pass_context
    def remove_tool(ctx: click.Context, name: str, tool: str) -> None:
        """
        Remove a tool from an existing agent.

        Examples:
            /agent remove-tool my_agent calculator
            /agent remove-tool default add
        """
        console: Console = ctx.obj["console"]
        agent_manager = ctx.obj["agent_manager"]

        logger.info(f"[COMMAND] /agent remove-tool - name={name}, tool={tool}")
        logger.debug(f"remove_tool_from_agent({name}, {tool})")

        try:
            agent_manager.remove_tool_from_agent(name, tool)
            logger.info(f"[COMMAND] Tool '{tool}' removed from agent '{name}'")
            logger.debug("remove_tool_from_agent() completed successfully")
            console.print()
            console.print(f"[green]✓[/green] Removed tool '{tool}' from agent '{name}'")
            console.print()

        except KeyError as e:
            logger.error(
                f"[COMMAND] Remove-tool failed - {type(e).__name__}: {str(e)}",
                exc_info=_should_log_traceback(),
            )
            console.print()
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print()
