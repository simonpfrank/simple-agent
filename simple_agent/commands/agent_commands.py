"""
Agent management commands for REPL/CLI.

Provides /agent command group with create, run, and list subcommands.
NO business logic - all logic delegated to AgentManager.
"""

import click
from rich.console import Console


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
