"""
Agent management commands for REPL/CLI.

Provides /agent command group with create, run, list, and chat subcommands.
NO business logic - all logic delegated to AgentManager.
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


@click.group()
@click.pass_context
def agent(ctx):
    """Agent management commands."""
    pass


@agent.command()
@click.argument("name")
@click.option(
    "--provider", "-p", default=None, help="LLM provider (openai, ollama, etc.)"
)
@click.option(
    "--template", "-t", default=None, help="Prompt template name (default, researcher)"
)
@click.option(
    "--role", "-r", default=None, help="Agent role/persona (overrides template)"
)
@click.pass_context
def create(ctx, name: str, provider: str, template: str, role: str):
    """
    Create a new agent.

    Examples:
        /agent create my_agent
        /agent create researcher --template researcher
        /agent create custom --role "You are a code reviewer"
        /agent create local_agent --provider ollama
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Business logic in agent_manager, not here
        agent = agent_manager.create_agent(
            name=name, provider=provider, role=role, template=template
        )
        console.print(f"[green]✓[/green] Created agent: {agent}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@agent.command()
@click.argument("name")
@click.argument("prompt", nargs=-1, required=True)
@click.pass_context
def run(ctx, name: str, prompt: tuple):
    """
    Run a prompt through an agent.

    Examples:
        /agent run my_agent What is the capital of France?
        /agent run researcher Explain quantum computing
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    # Join prompt parts into single string
    prompt_text = " ".join(prompt)

    try:
        # Business logic in agent_manager, not here
        console.print(f"\n[dim]Running agent '{name}'...[/dim]")
        response = agent_manager.run_agent(name, prompt_text)
        console.print(f"\n[bold cyan]Response:[/bold cyan]\n{response}\n")
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@agent.command(name="list")
@click.pass_context
def list_agents(ctx):
    """
    List all registered agents.

    Examples:
        /agent list
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    agents = agent_manager.list_agents()
    if agents:
        console.print("\n[bold]Registered Agents:[/bold]")
        for agent_name in agents:
            console.print(f"  • {agent_name}")
        console.print()
    else:
        console.print("[dim]No agents registered yet.[/dim]")
        console.print("[dim]Use '/agent create <name>' to create an agent.[/dim]\n")


@agent.command()
@click.argument("name")
@click.pass_context
def chat(ctx, name: str):
    """
    Enter interactive chat mode with an agent.

    Type your messages without the / prefix. Use /exit or Ctrl+D to exit.

    Examples:
        /agent chat default
        /agent chat researcher
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    # Verify agent exists
    try:
        agent_manager.get_agent(name)
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Display welcome message
    console.print()
    console.print(
        Panel(
            f"[bold cyan]Chat Mode:[/bold cyan] '{name}'\n"
            f"[dim]Type your messages without / prefix\n"
            f"Commands: /exit to exit, Ctrl+D or Ctrl+C to quit[/dim]",
            title="Interactive Chat",
            border_style="cyan",
        )
    )
    console.print()

    # Create chat session with history
    session = PromptSession(history=InMemoryHistory())

    try:
        while True:
            try:
                # Get user input
                user_input = session.prompt(f"Chat> ")

                # Check for exit command
                if user_input.strip().lower() == "/exit":
                    break

                # Skip empty input
                if not user_input.strip():
                    continue

                # Run through agent with reset=False to preserve memory across turns
                try:
                    response = agent_manager.run_agent(name, user_input, reset=False)
                    console.print(f"[bold green]{name}:[/bold green] {response}\n")
                except Exception as e:
                    console.print(f"[red]Error:[/red] {str(e)}\n")

            except EOFError:
                # Ctrl+D pressed
                break
            except KeyboardInterrupt:
                # Ctrl+C pressed
                console.print()
                break

    finally:
        console.print()
        console.print("[dim]Exited chat mode.[/dim]\n")


@agent.command()
@click.argument("name")
@click.pass_context
def tools(ctx, name: str):
    """
    List all tools attached to an agent.

    Examples:
        /agent tools my_agent
        /agent tools default
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Get tools from agent_manager
        tool_names = agent_manager.get_agent_tools(name)

        if not tool_names:
            console.print()
            console.print(f"[yellow]Agent '{name}' has no tools attached.[/yellow]")
            console.print()
            return

        # Display tools
        console.print()
        console.print(f"[bold]Tools for agent '{name}':[/bold]")
        for tool_name in sorted(tool_names):
            console.print(f"  • {tool_name}")
        console.print()
        console.print(f"[dim]Total: {len(tool_names)} tools[/dim]")
        console.print(
            f"[dim]Use [cyan]/tool info --name <tool>[/cyan] for tool details[/dim]\n"
        )

    except KeyError as e:
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()


@agent.command("add-tool")
@click.argument("name")
@click.option("--tool", "-t", required=True, help="Tool name to add")
@click.pass_context
def add_tool(ctx, name: str, tool: str):
    """
    Add a tool to an existing agent.

    Examples:
        /agent add-tool my_agent --tool calculator
        /agent add-tool default -t add
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Add tool via agent_manager
        agent_manager.add_tool_to_agent(name, tool)
        console.print()
        console.print(f"[green]✓[/green] Added tool '{tool}' to agent '{name}'")
        console.print()

    except KeyError as e:
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()


@agent.command("remove-tool")
@click.argument("name")
@click.option("--tool", "-t", required=True, help="Tool name to remove")
@click.pass_context
def remove_tool(ctx, name: str, tool: str):
    """
    Remove a tool from an existing agent.

    Examples:
        /agent remove-tool my_agent --tool calculator
        /agent remove-tool default -t add
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Remove tool via agent_manager
        agent_manager.remove_tool_from_agent(name, tool)
        console.print()
        console.print(f"[green]✓[/green] Removed tool '{tool}' from agent '{name}'")
        console.print()

    except KeyError as e:
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
