"""
Agent management commands for REPL/CLI.

Provides /agent command group with create, run, list, and chat subcommands.
NO business logic - all logic delegated to AgentManager.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

logger = logging.getLogger("simple_agent.commands.agent")


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


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
@click.option("--role", "-r", default=None, help="Agent role/persona")
@click.pass_context
def create(ctx, name: str, provider: str, role: str):
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
        f"create_agent(name={name}, provider={provider}, role_len={len(role) if role else 0})"
    )

    try:
        # Business logic in agent_manager, not here
        agent = agent_manager.create_agent(name=name, provider=provider, role=role)
        logger.info(f"[COMMAND] Agent '{name}' created successfully")
        logger.debug(f"create_agent() returned SimpleAgent instance: {agent.name}")
        console.print(f"[green]✓[/green] Created agent: {agent}")
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
@click.pass_context
def load(ctx, agent_name: str):
    """
    Load an agent from a YAML file.

    Intelligently resolves agent names to file paths:
    - If agent_name is a full path, uses it as-is
    - If agent_name is in config/agents/, searches there with .yaml or .yml extension
    - Otherwise, tries to find it in config/agents/ directory

    Examples:
        /agent load column_matcher          # Loads config/agents/column_matcher.yaml
        /agent load researcher              # Loads config/agents/researcher.yaml
        /agent load /path/to/custom.yaml    # Loads absolute path
        /agent load ./agents/my_agent       # Loads relative path
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    logger.info(f"[COMMAND] /agent load - name={agent_name}")

    # Check if agent is already loaded
    if agent_name in agent_manager.agents:
        existing_agent = agent_manager.agents[agent_name]
        tool_count = len(existing_agent.tools) if existing_agent.tools else 0
        logger.info(f"[COMMAND] Agent '{agent_name}' is already loaded")
        console.print(f"[yellow]ℹ[/yellow] Agent '{agent_name}' is already loaded")
        console.print(f"  Provider: {existing_agent.model_provider}")
        if existing_agent.tools:
            console.print(f"  Tools: {[t.name for t in existing_agent.tools]}")
        return

    # Resolve the actual file path
    logger.debug(f"_resolve_agent_path({agent_name})")
    yaml_path = _resolve_agent_path(agent_name)
    logger.debug(f"_resolve_agent_path() returned: {yaml_path}")

    if not yaml_path:
        logger.warning(
            f"[COMMAND] Agent '{agent_name}' not found in config/agents/ or as path"
        )
        console.print(
            f"[red]Error:[/red] Agent '{agent_name}' not found\n"
            f"  Tried:\n"
            f"    - config/agents/{agent_name}.yaml\n"
            f"    - config/agents/{agent_name}.yml\n"
            f"    - {agent_name} (as-is)"
        )
        return

    try:
        logger.debug(f"load_agent_from_yaml({yaml_path})")
        agent = agent_manager.load_agent_from_yaml(yaml_path)
        tool_count = len(agent.tools) if agent.tools else 0
        logger.info(
            f"[COMMAND] Agent '{agent.name}' loaded successfully ({tool_count} tools)"
        )
        logger.debug(
            f"load_agent_from_yaml() returned: {agent.name} with tools: {[t.name for t in (agent.tools or [])]}"
        )
        console.print(f"[green]✓[/green] Loaded agent: {agent.name}")
        if agent.tools:
            console.print(f"  Tools: {[t.name for t in agent.tools]}")
        else:
            console.print(f"  Tools: (none)")
    except FileNotFoundError as e:
        logger.error(
            f"[COMMAND] Load agent failed - file not found: {yaml_path}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] File not found: {yaml_path}")
    except Exception as e:
        logger.error(
            f"[COMMAND] Load agent failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")


def _resolve_agent_path(agent_name: str) -> str:
    """
    Resolve agent name to actual file path.

    Tries multiple strategies:
    1. If it's a full/relative path, return if it exists
    2. If it's just a name, look in config/agents/ with .yaml or .yml extension
    3. Return None if not found

    Args:
        agent_name: Agent name or path

    Returns:
        Resolved file path, or None if not found
    """
    # Strategy 1: If it looks like a path (contains / or \ or file extension), try as-is
    if (
        "/" in agent_name
        or "\\" in agent_name
        or agent_name.endswith((".yaml", ".yml"))
    ):
        if os.path.exists(agent_name):
            return agent_name
        # If it doesn't exist, fall through to other strategies

    # Strategy 2: Try in config/agents/ with .yaml extension
    agents_dir = Path("config/agents")
    yaml_path = agents_dir / f"{agent_name}.yaml"
    if yaml_path.exists():
        return str(yaml_path)

    # Strategy 3: Try in config/agents/ with .yml extension
    yml_path = agents_dir / f"{agent_name}.yml"
    if yml_path.exists():
        return str(yml_path)

    # Strategy 4: If full path was provided but doesn't exist, return it anyway
    # (let agent_manager.load_agent_from_yaml handle the error)
    if (
        "/" in agent_name
        or "\\" in agent_name
        or agent_name.endswith((".yaml", ".yml"))
    ):
        return agent_name

    # Not found
    return None


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

    logger.info(f"[COMMAND] /agent run - name={name}, prompt_len={len(prompt_text)}")
    logger.debug(f"run_agent(name={name}, prompt_len={len(prompt_text)}, reset=True)")

    try:
        # Business logic in agent_manager, not here
        console.print(f"\n[dim]Running agent '{name}'...[/dim]")
        response = agent_manager.run_agent(name, prompt_text)
        # Convert response to string (could be AgentResult or string)
        response_str = str(response) if response else ""
        response_len = len(response_str)
        logger.info(
            f"[COMMAND] Agent '{name}' ran successfully (response_len={response_len})"
        )
        logger.debug(f"run_agent() returned response with {response_len} characters")
        console.print(f"\n[bold cyan]Response:[/bold cyan]\n{response_str}\n")
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
def list_agents(ctx):
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

    # Get loaded agents
    agents = agent_manager.list_agents()
    logger.debug(f"list_agents() returned {len(agents)} agents: {agents}")

    # Get available YAML files from agents directory
    agents_dir = config.get("paths", {}).get("agents", "config/agents")
    available_yamls = []
    if os.path.isdir(agents_dir):
        for filename in os.listdir(agents_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                # Get agent name from filename (without extension)
                agent_name = filename.rsplit(".", 1)[0]
                available_yamls.append(agent_name)

    logger.info(f"[COMMAND] Listed {len(agents)} loaded, {len(available_yamls)} available")

    # Show loaded agents
    if agents:
        console.print("\n[bold cyan]Loaded Agents:[/bold cyan]")
        for agent_name in agents:
            console.print(f"  [green]●[/green] {agent_name}")

    # Show available YAML files (not yet loaded)
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

    logger.info(f"[COMMAND] /agent chat - name={name}")

    # Verify agent exists
    try:
        logger.debug(f"get_agent({name})")
        agent_manager.get_agent(name)
        logger.debug(f"get_agent() verified agent exists")
    except KeyError as e:
        logger.error(
            f"[COMMAND] Chat failed - agent '{name}' not found",
            exc_info=_should_log_traceback(),
        )
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Display welcome message
    logger.info(f"[COMMAND] Entering chat mode for agent '{name}'")
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
    message_count = 0

    # Single executor for entire chat session (avoids creating/destroying threads per message)
    # Runs agent in separate thread to avoid event loop conflict with prompt_toolkit
    # (SmolAgents uses asyncio.run() which conflicts with prompt_toolkit's loop)
    with ThreadPoolExecutor(max_workers=1) as executor:
        try:
            while True:
                try:
                    # Get user input
                    user_input = session.prompt("Chat> ")

                    # Check for exit command
                    if user_input.strip().lower() == "/exit":
                        logger.debug("Chat: User issued /exit command")
                        break

                    # Skip empty input
                    if not user_input.strip():
                        continue

                    # Run through agent with reset=False to preserve memory across turns
                    try:
                        message_count += 1
                        logger.debug(
                            f"[CHAT] Message {message_count}: prompt_len={len(user_input)}"
                        )
                        future = executor.submit(
                            agent_manager.run_agent, name, user_input, reset=False
                        )
                        response = future.result()
                        # Convert response to string (could be AgentResult or string)
                        response_str = str(response) if response else ""
                        response_len = len(response_str)
                        logger.debug(
                            f"[CHAT] Message {message_count}: response_len={response_len}"
                        )
                        console.print(f"[bold green]{name}:[/bold green] {response_str}\n")
                    except Exception as e:
                        logger.error(
                            f"[CHAT] Message {message_count} failed - {type(e).__name__}: {str(e)}",
                            exc_info=_should_log_traceback(),
                        )
                        console.print(f"[red]Error:[/red] {str(e)}\n")

                except EOFError:
                    # Ctrl+D pressed
                    logger.debug("Chat: User pressed Ctrl+D (EOF)")
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    logger.debug("Chat: User pressed Ctrl+C (interrupt)")
                    console.print()
                    break

        finally:
            logger.info(
                f"[COMMAND] Exited chat mode for agent '{name}' ({message_count} messages)"
            )
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

    logger.info(f"[COMMAND] /agent tools - name={name}")
    logger.debug(f"get_agent_tools({name})")

    try:
        # Get tools from agent_manager
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

        # Display tools
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


@agent.command("add-tool")
@click.argument("name")
@click.argument("tool")
@click.pass_context
def add_tool(ctx, name: str, tool: str):
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
        # Add tool via agent_manager
        agent_manager.add_tool_to_agent(name, tool)
        logger.info(f"[COMMAND] Tool '{tool}' added to agent '{name}'")
        logger.debug(f"add_tool_to_agent() completed successfully")
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


@agent.command("remove-tool")
@click.argument("name")
@click.argument("tool")
@click.pass_context
def remove_tool(ctx, name: str, tool: str):
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
        # Remove tool via agent_manager
        agent_manager.remove_tool_from_agent(name, tool)
        logger.info(f"[COMMAND] Tool '{tool}' removed from agent '{name}'")
        logger.debug(f"remove_tool_from_agent() completed successfully")
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


@agent.command("show-prompt")
@click.argument("name")
@click.pass_context
def show_prompt(ctx, name: str):
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
        # Get agent
        agent = agent_manager.get_agent(name)
        logger.debug(f"get_agent() returned agent: {agent.name}")

        # Get system prompt from underlying SmolAgents agent
        system_prompt = agent.agent.system_prompt
        prompt_len = len(system_prompt) if system_prompt else 0
        logger.debug(f"System prompt length: {prompt_len} characters")

        # Display in a panel
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
            f"[yellow]Warning:[/yellow] Agent '{name}' does not have a system_prompt attribute"
        )
        console.print()


@agent.command("save")
@click.argument("name")
@click.option(
    "--path",
    "-p",
    default=None,
    help="Custom save path (default: config/agents/<name>.yaml)",
)
@click.pass_context
def save(ctx, name: str, path: str):
    """
    Save agent configuration to YAML file.

    Saves the agent's configuration (role, tools, settings) to a YAML file
    in the config/agents/ directory, or to a custom path.

    Examples:
        /agent save my_agent
        /agent save researcher --path custom/researcher.yaml
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    logger.info(f"[COMMAND] /agent save - name={name}, path={path}")

    try:
        # Determine save path
        if path is None:
            path = f"config/agents/{name}.yaml"

        logger.debug(f"save_agent_to_yaml({name}, {path})")
        # Save agent
        agent_manager.save_agent_to_yaml(name, path)
        logger.info(f"[COMMAND] Agent '{name}' saved to: {path}")
        logger.debug(f"save_agent_to_yaml() completed successfully")

        console.print()
        console.print(f"[green]✓[/green] Saved agent '{name}' to: [cyan]{path}[/cyan]")
        console.print()

    except KeyError as e:
        logger.error(
            f"[COMMAND] Save failed - agent '{name}' not found",
            exc_info=_should_log_traceback(),
        )
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
    except Exception as e:
        logger.error(
            f"[COMMAND] Save failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print()
        console.print(f"[red]Error:[/red] Failed to save agent: {str(e)}")
        console.print()


@agent.command("create-wizard")
@click.pass_context
def create_wizard(ctx):
    """
    Create an agent interactively using a step-by-step wizard.

    Walks you through all agent configuration options with prompts
    and defaults. Optionally saves the agent to a YAML file.

    Example:
        /agent create-wizard
    """
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]
    tool_manager = ctx.obj.get("tool_manager")
    config = ctx.obj["config"]

    logger.info("[COMMAND] /agent create-wizard - started")

    console.print()
    console.print(
        Panel(
            "[bold cyan]Interactive Agent Creation Wizard[/bold cyan]\n"
            "[dim]Follow the prompts to create a new agent[/dim]",
            title="Agent Wizard",
            border_style="cyan",
        )
    )
    console.print()

    try:
        # Step 1: Agent name
        logger.debug("Wizard step 1: agent name")
        name = click.prompt("Agent name", type=str)
        logger.debug(f"Wizard input: name={name}")

        # Step 2: Agent role/persona
        console.print()
        console.print("[bold]Agent role/persona:[/bold]")
        console.print(
            "[dim]Enter the agent's system prompt or press Enter for default[/dim]"
        )
        logger.debug("Wizard step 2: agent role")
        role = click.prompt(
            "Role", default="You are a helpful AI assistant.", show_default=True
        )
        logger.debug(f"Wizard input: role_len={len(role)}")

        # Step 3: LLM provider
        console.print()
        console.print("[bold]Select LLM provider:[/bold]")

        # Get providers from config (Issue #14: use dynamic provider list)
        llm_config = config.get("llm", {})
        # Filter out non-provider keys (keys with dict values that have config like model, api_key, etc.)
        providers = [
            key
            for key in llm_config.keys()
            if isinstance(llm_config[key], dict)
            and any(
                k in llm_config[key]
                for k in ["model", "api_key", "base_url", "azure_endpoint"]
            )
        ]
        # Sort for consistent ordering, with default first
        default_provider = llm_config.get("provider", "openai")
        if default_provider in providers:
            providers.remove(default_provider)
            providers.insert(0, default_provider)

        logger.debug(f"Wizard step 3: LLM provider - available={providers}")
        for i, provider in enumerate(providers, 1):
            console.print(f"  {i}. {provider}")

        provider_idx = click.prompt(
            "Provider choice",
            type=click.IntRange(1, len(providers)),
            default=1,
            show_default=True,
        )
        provider = providers[provider_idx - 1]
        logger.debug(f"Wizard input: provider={provider}")

        # Step 4: Tools (if tool_manager available)
        tools = []
        if tool_manager:
            console.print()
            logger.debug("Wizard step 4: tools selection")
            add_tools = click.confirm("Add tools to this agent?", default=False)

            if add_tools:
                available_tools = tool_manager.list_tools()
                logger.debug(f"Available tools: {available_tools}")
                if available_tools:
                    console.print("[bold]Available tools:[/bold]")
                    for i, tool_name in enumerate(available_tools, 1):
                        console.print(f"  {i}. {tool_name}")

                    console.print()
                    console.print(
                        "[dim]Enter tool numbers separated by commas (e.g., 1,3,4)[/dim]"
                    )
                    tool_selection = click.prompt(
                        "Tool selection", default="", show_default=False
                    )

                    if tool_selection:
                        tool_indices = [
                            int(idx.strip()) - 1 for idx in tool_selection.split(",")
                        ]
                        tools = [
                            available_tools[idx]
                            for idx in tool_indices
                            if 0 <= idx < len(available_tools)
                        ]
            logger.debug(f"Wizard step 4: selected {len(tools)} tools: {tools}")

        # Step 5: Save to YAML
        console.print()
        logger.debug("Wizard step 5: save to YAML")
        save_yaml = click.confirm("Save agent configuration to YAML?", default=True)
        logger.debug(f"Wizard input: save_yaml={save_yaml}")

        # Create the agent
        console.print()
        console.print("[dim]Creating agent...[/dim]")
        logger.debug(
            f"create_agent(name={name}, provider={provider}, role_len={len(role)}, tools={tools})"
        )
        agent_manager.create_agent(
            name=name,
            provider=provider,
            role=role,
            tools=tools if tools else None,
        )
        logger.info(
            f"[COMMAND] Wizard: Agent '{name}' created (provider={provider}, tools={len(tools)})"
        )
        logger.debug(f"create_agent() completed successfully")

        console.print()
        console.print(f"[green]✓[/green] Created agent: [bold]{name}[/bold]")

        if tools:
            console.print(f"  Tools: {', '.join(tools)}")

        # Save to YAML if requested
        if save_yaml:
            yaml_path = f"config/agents/{name}.yaml"
            logger.debug(f"save_agent_to_yaml({name}, {yaml_path})")
            agent_manager.save_agent_to_yaml(name, yaml_path)
            logger.info(f"[COMMAND] Wizard: Agent '{name}' saved to {yaml_path}")
            logger.debug(f"save_agent_to_yaml() completed successfully")
            console.print(f"  Saved to: [cyan]{yaml_path}[/cyan]")

        console.print()

    except click.Abort:
        logger.info("[COMMAND] Wizard: User cancelled")
        console.print()
        console.print("[yellow]Wizard cancelled[/yellow]")
        console.print()
    except Exception as e:
        logger.error(
            f"[COMMAND] Wizard failed - {type(e).__name__}: {str(e)}",
            exc_info=_should_log_traceback(),
        )
        console.print()
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print()
