"""
Agent creation wizard for REPL/CLI.

Provides interactive agent creation with step-by-step prompts.
"""

import logging

import click
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger("simple_agent.commands.agent_wizard")


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


def prompt_with_default(message: str, default: str = "") -> str:
    """Prompt with optional default value using click.prompt."""
    try:
        result = click.prompt(message, default=default, show_default=bool(default))
        return result.strip() if result else default
    except (EOFError, KeyboardInterrupt, click.Abort):
        raise click.Abort()


def register_wizard_command(agent_group: click.Group) -> None:
    """Register the create-wizard command on the agent group."""

    @agent_group.command("create-wizard")
    @click.pass_context
    def create_wizard(ctx: click.Context) -> None:
        """
        Create an agent interactively using a step-by-step wizard.

        Walks you through all agent configuration options with prompts
        and defaults. Optionally saves the agent to a YAML file.

        NOTE: This command only works in CLI mode, not in the REPL.
        In the REPL, use: /agent create <name> --provider <provider> --role "role"

        Example (CLI only):
            simple-agent agent create-wizard
        """
        console: Console = ctx.obj["console"]
        agent_manager = ctx.obj["agent_manager"]
        tool_manager = ctx.obj.get("tool_manager")
        config = ctx.obj["config"]
        repl_state = ctx.obj.get("repl_state")

        logger.info("[COMMAND] /agent create-wizard - started")

        # Check if running in REPL mode - interactive prompts don't work there
        if repl_state is not None:
            console.print()
            console.print(
                Panel(
                    "[yellow]The wizard requires interactive input which doesn't work in the REPL.[/yellow]\n\n"
                    "[bold]Use instead:[/bold]\n"
                    "  /agent create <name> --provider <provider> --role \"Your role\"\n\n"
                    "[bold]Examples:[/bold]\n"
                    "  /agent create my_agent\n"
                    "  /agent create coder --role \"You are a Python expert\"\n"
                    "  /agent create local --provider ollama",
                    title="Wizard Not Available in REPL",
                    border_style="yellow",
                )
            )
            return

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
            name = prompt_with_default("Agent name")
            if not name:
                console.print("[red]Error:[/red] Agent name is required")
                return
            logger.debug(f"Wizard input: name={name}")

            # Step 2: Agent role/persona
            console.print()
            console.print("[bold]Agent role/persona:[/bold]")
            console.print(
                "[dim]Enter the agent's system prompt or press Enter for default[/dim]"
            )
            logger.debug("Wizard step 2: agent role")
            role = prompt_with_default("Role", "You are a helpful AI assistant.")
            logger.debug(f"Wizard input: role_len={len(role)}")

            # Step 3: LLM provider
            console.print()
            console.print("[bold]Select LLM provider:[/bold]")

            # Get providers from config
            llm_config = config.get("llm", {})
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

            provider_choice = prompt_with_default("Provider choice (number)", "1")
            try:
                provider_idx = int(provider_choice)
                if provider_idx < 1 or provider_idx > len(providers):
                    provider_idx = 1
            except ValueError:
                provider_idx = 1
            provider = providers[provider_idx - 1]
            logger.debug(f"Wizard input: provider={provider}")

            # Step 4: Tools (if tool_manager available)
            tools = _select_tools(console, tool_manager)
            logger.debug(f"Wizard step 4: selected {len(tools)} tools: {tools}")

            # Step 5: Save to YAML
            console.print()
            logger.debug("Wizard step 5: save to YAML")
            save_yaml_choice = prompt_with_default(
                "Save agent configuration to YAML? (y/n)", "y"
            )
            save_yaml = save_yaml_choice.lower() in ("y", "yes")
            logger.debug(f"Wizard input: save_yaml={save_yaml}")

            # Create the agent
            console.print()
            console.print("[dim]Creating agent...[/dim]")
            logger.debug(
                f"create_agent(name={name}, provider={provider}, "
                f"role_len={len(role)}, tools={tools})"
            )
            agent_manager.create_agent(
                name=name,
                provider=provider,
                role=role,
                tools=tools if tools else None,
            )
            logger.info(
                f"[COMMAND] Wizard: Agent '{name}' created "
                f"(provider={provider}, tools={len(tools)})"
            )
            logger.debug("create_agent() completed successfully")

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
                logger.debug("save_agent_to_yaml() completed successfully")
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


def _select_tools(console: Console, tool_manager) -> list:
    """Prompt user to select tools for the agent."""
    tools: list[str] = []
    if not tool_manager:
        return tools

    console.print()
    logger.debug("Wizard step 4: tools selection")
    add_tools_choice = prompt_with_default("Add tools to this agent? (y/n)", "n")
    add_tools = add_tools_choice.lower() in ("y", "yes")

    if not add_tools:
        return tools

    available_tools = tool_manager.list_tools()
    logger.debug(f"Available tools: {available_tools}")
    if not available_tools:
        return tools

    console.print("[bold]Available tools:[/bold]")
    for i, tool_name in enumerate(available_tools, 1):
        console.print(f"  {i}. {tool_name}")

    console.print()
    console.print("[dim]Enter tool numbers separated by commas (e.g., 1,3,4)[/dim]")
    tool_selection = prompt_with_default("Tool selection", "")

    if tool_selection:
        try:
            tool_indices = [
                int(idx.strip()) - 1 for idx in tool_selection.split(",")
            ]
            tools = [
                available_tools[idx]
                for idx in tool_indices
                if 0 <= idx < len(available_tools)
            ]
        except ValueError:
            console.print("[yellow]Invalid selection, skipping tools[/yellow]")

    return tools
