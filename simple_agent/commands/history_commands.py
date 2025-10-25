"""
History management commands for REPL/CLI.

Provides /history command group for viewing and managing conversation history.
Leverages SmolAgents' built-in memory system.
"""

import json
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table


@click.group()
@click.pass_context
def history(ctx):
    """History management commands."""
    pass


@history.command()
@click.option("--limit", "-n", default=10, help="Number of recent exchanges to show")
@click.pass_context
def show(ctx, limit: int):
    """
    Display conversation history.

    Shows the last N exchanges from the current agent's memory.
    Uses SmolAgents' built-in memory system.

    Examples:
        /history show           # Show last 10 exchanges
        /history show --limit 5 # Show last 5 exchanges
        /history show -n 20     # Show last 20 exchanges
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    # Check if an agent has been run
    if not agent_manager.last_agent:
        console.print(
            "[yellow]No agent history yet.[/yellow] Run an agent first with [cyan]/agent run[/cyan]\n"
        )
        return

    # Get the agent
    try:
        agent_wrapper = agent_manager.get_agent(agent_manager.last_agent)
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}\n")
        return

    # Access SmolAgents memory (through SimpleAgent wrapper)
    memory_steps = agent_wrapper.agent.memory.get_full_steps()

    if not memory_steps:
        console.print(
            f"[yellow]No history for agent '{agent_manager.last_agent}'.[/yellow]\n"
        )
        console.print(
            "[dim]History will appear here after running prompts through the agent.[/dim]\n"
        )
        return

    # Display last N steps
    display_steps = memory_steps[-limit:] if limit > 0 else memory_steps

    # Create a table for better formatting
    table = Table(title=f"History for '{agent_manager.last_agent}' (last {len(display_steps)} steps)")
    table.add_column("#", style="dim", width=4)
    table.add_column("Type", style="cyan")
    table.add_column("Content", style="white")

    for i, step in enumerate(display_steps, 1):
        # SmolAgents memory structure detection
        if "task" in step:
            # This is a user task/question
            content = step.get("task", "")
            table.add_row(str(i), "Task", f"[bold]{content}[/bold]")
        elif "step_number" in step:
            # This is an agent execution step
            step_num = step.get("step_number", "?")

            # Check for tool calls
            if "tool_calls" in step:
                tool_calls = step.get("tool_calls", [])
                if tool_calls and len(tool_calls) > 0:
                    tool_name = tool_calls[0].get("name", "unknown")
                    tool_args = tool_calls[0].get("arguments", {})

                    # Show tool call info
                    if tool_name == "final_answer":
                        answer = tool_args.get("answer", "")
                        content = f"Answer: {answer}"
                    else:
                        content = f"Tool: {tool_name}({tool_args})"
                else:
                    content = "Thinking..."
            else:
                # No tool calls, show observations if available
                observations = step.get("observations", "")
                if observations:
                    content = f"Observation: {observations}"
                else:
                    content = "Processing..."

            # Truncate long content
            if isinstance(content, str) and len(content) > 100:
                content = content[:100] + "..."

            table.add_row(str(i), f"Step {step_num}", content)
        else:
            # Unknown step format - show raw (for debugging)
            content = str(step)[:100]
            table.add_row(str(i), "unknown", content)

    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Total steps in memory: {len(memory_steps)}[/dim]")
    console.print("[dim]Use [cyan]/history clear[/cyan] to reset history[/dim]\n")


@history.command()
@click.pass_context
def clear(ctx):
    """
    Clear conversation history.

    Resets the agent's memory using SmolAgents' built-in reset() method.

    Examples:
        /history clear
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    # Check if an agent has been run
    if not agent_manager.last_agent:
        console.print(
            "[yellow]No agent to clear history for.[/yellow] Run an agent first.\n"
        )
        return

    # Get the agent
    try:
        agent_wrapper = agent_manager.get_agent(agent_manager.last_agent)
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}\n")
        return

    # Clear memory using SmolAgents' built-in method
    agent_wrapper.agent.memory.reset()

    console.print()
    console.print(
        f"[green]✓[/green] Cleared history for agent '[bold]{agent_manager.last_agent}[/bold]'"
    )
    console.print()


@history.command()
@click.argument("file", type=click.Path())
@click.pass_context
def save(ctx, file: str):
    """
    Save conversation history to a file.

    Exports the agent's memory to a JSON file for later review or backup.

    Examples:
        /history save history.json
        /history save data/conversations/session_20251023.json
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    # Check if an agent has been run
    if not agent_manager.last_agent:
        console.print("[yellow]No history to save.[/yellow] Run an agent first.\n")
        return

    # Get the agent
    try:
        agent_wrapper = agent_manager.get_agent(agent_manager.last_agent)
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}\n")
        return

    # Get memory steps from SmolAgents memory
    memory_steps = agent_wrapper.agent.memory.get_full_steps()

    if not memory_steps:
        console.print(
            "[yellow]No history to save.[/yellow] Memory is empty.\n"
        )
        return

    # Save to JSON file
    try:
        with open(file, "w") as f:
            # Add metadata
            export_data = {
                "agent_name": agent_manager.last_agent,
                "exported_at": datetime.now().isoformat(),
                "steps": memory_steps,
                "total_steps": len(memory_steps),
            }
            json.dump(export_data, f, indent=2, default=str)

        console.print()
        console.print(
            f"[green]✓[/green] Saved {len(memory_steps)} history steps to [bold]{file}[/bold]"
        )
        console.print()
    except Exception as e:
        console.print(f"[red]Error saving history:[/red] {str(e)}\n")
