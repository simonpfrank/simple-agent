"""
Agent persistence commands for REPL/CLI.

Provides load and save functionality for agent YAML files.
"""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

logger = logging.getLogger("simple_agent.commands.agent_persistence")


def _should_log_traceback() -> bool:
    """Check if logger is in DEBUG mode to include tracebacks."""
    return logger.isEnabledFor(logging.DEBUG)


def resolve_agent_path(agent_name: str) -> Optional[str]:
    """
    Resolve agent name to actual file path with path traversal protection.

    Tries multiple strategies:
    1. If it's a full/relative path, return if it exists (with security checks)
    2. If it's just a name, look in config/agents/ with .yaml or .yml extension
    3. Return None if not found

    Args:
        agent_name: Agent name or path

    Returns:
        Resolved file path, or None if not found or path traversal detected

    Security:
        - Rejects any input containing ".." to prevent path traversal
        - Validates that resolved paths in config/agents stay within that directory
    """
    # SECURITY: Reject any path traversal attempts
    if ".." in agent_name:
        logger.warning(f"Path traversal attempt detected in agent name: {agent_name}")
        return None

    agents_dir = Path("config/agents").resolve()

    # Strategy 1: If it looks like a path, try as-is
    if (
        "/" in agent_name
        or "\\" in agent_name
        or agent_name.endswith((".yaml", ".yml"))
    ):
        candidate = Path(agent_name).resolve()
        if candidate.exists():
            # SECURITY: If within agents_dir, verify it stays there
            if str(candidate).startswith(str(agents_dir)):
                return str(candidate)
            # Allow loading from outside agents_dir for explicit full paths
            return str(candidate)

    # Strategy 2: Try in config/agents/ with .yaml extension
    yaml_path = (agents_dir / f"{agent_name}.yaml").resolve()
    if str(yaml_path).startswith(str(agents_dir)) and yaml_path.exists():
        return str(yaml_path)

    # Strategy 3: Try in config/agents/ with .yml extension
    yml_path = (agents_dir / f"{agent_name}.yml").resolve()
    if str(yml_path).startswith(str(agents_dir)) and yml_path.exists():
        return str(yml_path)

    # Strategy 4: If full path was provided but doesn't exist, return it anyway
    if (
        "/" in agent_name
        or "\\" in agent_name
        or agent_name.endswith((".yaml", ".yml"))
    ):
        return agent_name

    return None


def register_persistence_commands(agent_group: click.Group) -> None:
    """Register load and save commands on the agent group."""

    @agent_group.command()
    @click.argument("agent_name")
    @click.pass_context
    def load(ctx: click.Context, agent_name: str) -> None:
        """
        Load an agent from a YAML file.

        Intelligently resolves agent names to file paths:
        - If agent_name is a full path, uses it as-is
        - If agent_name is in config/agents/, searches there
        - Otherwise, tries to find it in config/agents/ directory

        Examples:
            /agent load column_matcher
            /agent load researcher
            /agent load /path/to/custom.yaml
        """
        console: Console = ctx.obj["console"]
        agent_manager = ctx.obj["agent_manager"]

        logger.info(f"[COMMAND] /agent load - name={agent_name}")

        # Check if agent is already loaded
        if agent_name in agent_manager.agents:
            existing_agent = agent_manager.agents[agent_name]
            logger.info(f"[COMMAND] Agent '{agent_name}' is already loaded")
            console.print(
                f"[yellow]ℹ[/yellow] Agent '{agent_name}' is already loaded"
            )
            console.print(f"  Provider: {existing_agent.model_provider}")
            if existing_agent.tools:
                console.print(f"  Tools: {[t.name for t in existing_agent.tools]}")
            agent_manager.set_active_agent(agent_name)
            return

        # Resolve the actual file path
        logger.debug(f"resolve_agent_path({agent_name})")
        yaml_path = resolve_agent_path(agent_name)
        logger.debug(f"resolve_agent_path() returned: {yaml_path}")

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
                f"load_agent_from_yaml() returned: {agent.name} with tools: "
                f"{[t.name for t in (agent.tools or [])]}"
            )
            console.print(f"[green]✓[/green] Loaded agent: {agent.name}")
            if agent.tools:
                console.print(f"  Tools: {[t.name for t in agent.tools]}")
            else:
                console.print("  Tools: (none)")
            agent_manager.set_active_agent(agent.name)
        except FileNotFoundError:
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

    @agent_group.command("save")
    @click.argument("name")
    @click.option(
        "--path",
        "-p",
        default=None,
        help="Custom save path (default: config/agents/<name>.yaml)",
    )
    @click.pass_context
    def save(ctx: click.Context, name: str, path: Optional[str]) -> None:
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
            if path is None:
                path = f"config/agents/{name}.yaml"

            logger.debug(f"save_agent_to_yaml({name}, {path})")
            agent_manager.save_agent_to_yaml(name, path)
            logger.info(f"[COMMAND] Agent '{name}' saved to: {path}")
            logger.debug("save_agent_to_yaml() completed successfully")

            console.print()
            console.print(
                f"[green]✓[/green] Saved agent '{name}' to: [cyan]{path}[/cyan]"
            )
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
