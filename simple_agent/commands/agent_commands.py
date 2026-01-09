"""
Agent management commands for REPL/CLI.

Provides /agent command group with create, run, list, and chat subcommands.
NO business logic - all logic delegated to AgentManager.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor

import click
from rich.console import Console
from rich.panel import Panel

from simple_agent.commands.agent_persistence import register_persistence_commands
from simple_agent.commands.agent_tools import register_tool_commands
from simple_agent.commands.agent_wizard import register_wizard_command

logger = logging.getLogger("simple_agent.commands.agent")


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


@click.group()
@click.pass_context
def agent(ctx: click.Context) -> None:
    """Agent management commands."""
    pass


# Register commands from extracted modules
register_persistence_commands(agent)
register_tool_commands(agent)
register_wizard_command(agent)


@agent.command()
@click.argument("name")
@click.option(
    "--provider", "-p", default=None, help="LLM provider (openai, ollama, etc.)"
)
@click.option("--role", "-r", default=None, help="Agent role/persona")
@click.pass_context
def create(ctx: click.Context, name: str, provider: str, role: str) -> None:
    """
    Create a new agent.

    Examples:
        /agent create my_agent
        /agent create custom --role "You are a code reviewer"
        /agent create local_agent --provider ollama
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    logger.info(f"[COMMAND] /agent create - name={name}, provider={provider}")
    logger.debug(
        f"create_agent(name={name}, provider={provider}, "
        f"role_len={len(role) if role else 0})"
    )

    try:
        agent_obj = agent_manager.create_agent(name=name, provider=provider, role=role)
        logger.info(f"[COMMAND] Agent '{name}' created successfully")
        logger.debug(f"create_agent() returned SimpleAgent instance: {agent_obj.name}")
        console.print(f"[green]✓[/green] Created agent: {agent_obj}")
    except FileNotFoundError as e:
        logger.error(
            f"[COMMAND] Create agent failed - file not found: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        logger.error(
            f"[COMMAND] Create agent failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")


@agent.command()
@click.argument("agent_name")
@click.argument("prompt", nargs=-1, required=True)
@click.option(
    "-v", "--verbose", is_flag=True, help="Enable verbose output for this run"
)
@click.pass_context
def run(ctx: click.Context, agent_name: str, prompt: tuple, verbose: bool) -> None:
    """
    Run a prompt through an agent.

    Examples:
        /agent run my_agent What is the capital of France?
        /agent run researcher Explain quantum computing
        /agent run default "tell me a joke" -v
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    prompt_text = " ".join(prompt)

    logger.info(
        f"[COMMAND] /agent run - name={agent_name}, prompt_len={len(prompt_text)}"
    )
    logger.debug(
        f"run_agent(name={agent_name}, prompt_len={len(prompt_text)}, reset=True)"
    )

    try:
        console.print(f"\n[dim]Running agent '{agent_name}'...[/dim]")

        # Run in thread to isolate SmolAgents' asyncio.run() from prompt_toolkit
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(agent_manager.run_agent, agent_name, prompt_text)
            response = future.result()

        response_str = str(response) if response else ""
        response_len = len(response_str)
        logger.info(
            f"[COMMAND] Agent '{agent_name}' ran successfully "
            f"(response_len={response_len})"
        )
        logger.debug(f"run_agent() returned response with {response_len} characters")
        console.print(f"\n[bold cyan]Response:[/bold cyan]\n{response_str}\n")

        # Display token usage if available
        if hasattr(response, "total_tokens") and response.total_tokens > 0:
            token_info = (
                f"[dim]Tokens: {response.input_tokens:,} in / "
                f"{response.output_tokens:,} out = {response.total_tokens:,} total"
            )
            if hasattr(response, "cost") and float(response.cost) > 0:
                token_info += f" | Cost: ${float(response.cost):.6f}"
            token_info += "[/dim]"
            console.print(token_info)
            console.print()

            # Persist stats to token manager if available
            token_manager = ctx.obj.get("token_manager")
            if token_manager:
                token_manager.add_execution(
                    agent_name=agent_name,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost=float(response.cost) if hasattr(response, "cost") else 0.0,
                    model=response.model if hasattr(response, "model") else "unknown",
                )
                token_manager.save()
    except KeyError as e:
        logger.error(
            f"[COMMAND] Run agent failed - agent not found: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        logger.error(
            f"[COMMAND] Run agent failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")


@agent.command(name="list")
@click.pass_context
def list_agents(ctx: click.Context) -> None:
    """
    List all registered agents and available YAML files.

    Shows:
    - Loaded agents (in memory, ready to use)
    - Available agent YAML files in config/agents/

    Examples:
        /agent list
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]
    config = ctx.obj.get("config", {})

    logger.info("[COMMAND] /agent list")
    logger.debug("list_agents()")

    agents = agent_manager.list_agents()
    logger.debug(f"list_agents() returned {len(agents)} agents: {agents}")

    # Get available YAML files from agents directory
    agents_dir = config.get("paths", {}).get("agents", "config/agents")
    available_yamls = []
    if os.path.isdir(agents_dir):
        for filename in os.listdir(agents_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                agent_name = filename.rsplit(".", 1)[0]
                available_yamls.append(agent_name)

    logger.info(
        f"[COMMAND] Listed {len(agents)} loaded, {len(available_yamls)} available"
    )

    if agents:
        console.print("\n[bold cyan]Loaded Agents:[/bold cyan]")
        for agent_name in agents:
            console.print(f"  [green]●[/green] {agent_name}")

    not_loaded = [name for name in available_yamls if name not in agents]
    if not_loaded:
        console.print("\n[bold]Available (not loaded):[/bold]")
        for agent_name in sorted(not_loaded):
            console.print(f"  [dim]○[/dim] {agent_name}")
        console.print("\n[dim]Use '/agent load <name>' to load an agent.[/dim]")

    if not agents and not not_loaded:
        console.print("[dim]No agents found.[/dim]")
        console.print("[dim]Use '/agent create <name>' to create an agent.[/dim]")

    console.print()


@agent.command()
@click.argument("name")
@click.pass_context
def chat(ctx: click.Context, name: str) -> None:
    """
    Enter interactive chat mode with an agent.

    Type your messages without the / prefix. Use /exit to exit chat mode.

    Examples:
        /agent chat default
        /agent chat researcher
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]
    repl_state = ctx.obj.get("repl_state")

    logger.info(f"[COMMAND] /agent chat - name={name}")

    try:
        logger.debug(f"get_agent({name})")
        agent_manager.get_agent(name)
        logger.debug("get_agent() verified agent exists")
    except KeyError as e:
        logger.error(
            f"[COMMAND] Chat failed - agent '{name}' not found",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    if repl_state is None:
        console.print(
            "[red]Error:[/red] Chat mode not available (REPL state not initialized)"
        )
        return

    repl_state.chat_mode_agent = name
    logger.info(f"[COMMAND] Entered chat mode for agent '{name}'")

    console.print()
    console.print(
        Panel(
            f"[bold cyan]Chat Mode:[/bold cyan] '{name}'\n"
            f"[dim]Type your messages without / prefix\n"
            f"Use /exit to return to normal mode[/dim]",
            title="Interactive Chat",
            border_style="cyan",
        )
    )


@agent.command("show-prompt")
@click.argument("name")
@click.pass_context
def show_prompt(ctx: click.Context, name: str) -> None:
    """
    Show the system prompt used by an agent.

    Displays the actual system prompt that the agent is using, including
    tool instructions and any customizations from SmolAgents.

    Examples:
        /agent show-prompt default
        /agent show-prompt my_agent
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    logger.info(f"[COMMAND] /agent show-prompt - name={name}")
    logger.debug(f"get_agent({name})")

    try:
        agent_obj = agent_manager.get_agent(name)
        logger.debug(f"get_agent() returned agent: {agent_obj.name}")

        system_prompt = agent_obj.agent.system_prompt
        prompt_len = len(system_prompt) if system_prompt else 0
        logger.debug(f"System prompt length: {prompt_len} characters")

        console.print()
        console.print(
            Panel(
                system_prompt,
                title=f"System Prompt for '{name}'",
                border_style="cyan",
            )
        )
        console.print()

    except KeyError as e:
        logger.error(
            f"[COMMAND] Show-prompt failed - agent '{name}' not found",
            exc_info=_should_log_traceback(),
        )
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
    except AttributeError:
        logger.warning(
            f"[COMMAND] Show-prompt - agent '{name}' missing system_prompt attribute"
        )
        console.print()
        console.print(
            f"[yellow]Warning:[/yellow] Agent '{name}' does not have "
            "a system_prompt attribute"
        )
        console.print()
