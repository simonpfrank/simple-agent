"""Core commands plugin for cli_repl_kit integration.

This plugin wraps all existing simple_agent commands and registers them
with the cli_repl_kit REPL. Commands are imported inside register() to
avoid circular import issues.
"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict

import click

# Add cli_repl_kit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "cli_repl_kit"))

from cli_repl_kit.plugins.base import CommandPlugin


class CoreCommandsPlugin(CommandPlugin):
    """Plugin that registers all simple_agent commands with cli_repl_kit.

    This plugin wraps the existing Click commands from simple_agent/commands/
    and makes them available in the cli_repl_kit REPL.
    """

    @property
    def name(self) -> str:
        """Return plugin name."""
        return "simple_agent_core"

    def register(
        self, cli: click.Group, context_factory: Callable[[], Dict[str, Any]]
    ) -> None:
        """Register all simple_agent commands with the CLI group.

        Commands are imported inside this method to avoid circular imports.
        The context_factory is stored so commands can access it via Click's
        context object (ctx.obj).

        Args:
            cli: Click group to register commands with
            context_factory: Function that returns context dict with managers
        """
        # Import commands here to avoid circular imports
        from simple_agent.commands.agent_commands import agent
        from simple_agent.commands.collection_commands import collection
        from simple_agent.commands.config_commands import config
        from simple_agent.commands.debug_commands import debug
        from simple_agent.commands.flow_commands_cli import flow
        from simple_agent.commands.history_commands import history
        from simple_agent.commands.inspection_commands import prompt, response
        from simple_agent.commands.llm import llm_command
        from simple_agent.commands.system_commands import (
            exit_command,
            help_command,
            quit_command,
            refresh,
        )
        from simple_agent.commands.token_stats_commands import token
        from simple_agent.commands.tool_commands import tool

        # Create a wrapper to inject context into Click commands
        # This makes ctx.obj available with the same structure as before
        def wrap_with_context(cmd: click.Command) -> click.Command:
            """Wrap command to inject context factory result into ctx.obj."""
            original_callback = cmd.callback

            @click.pass_context
            def wrapped_callback(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
                # Initialize ctx.obj from context_factory if not set
                if ctx.obj is None:
                    ctx.obj = context_factory()
                return ctx.invoke(original_callback, *args, **kwargs)

            cmd.callback = wrapped_callback
            return cmd

        # Register system commands
        cli.add_command(wrap_with_context(help_command), name="help")
        cli.add_command(wrap_with_context(quit_command), name="quit")
        cli.add_command(wrap_with_context(exit_command), name="exit")
        cli.add_command(wrap_with_context(refresh), name="refresh")

        # Register command groups (they handle their own context passing)
        cli.add_command(config, name="config")
        cli.add_command(agent, name="agent")
        cli.add_command(prompt, name="prompt")
        cli.add_command(response, name="response")
        cli.add_command(debug, name="debug")
        cli.add_command(history, name="history")
        cli.add_command(tool, name="tool")
        cli.add_command(token, name="token")
        cli.add_command(collection, name="collection")
        cli.add_command(flow, name="flow")
        cli.add_command(llm_command, name="llm")

        # Store context factory for groups to access
        # Groups use @click.pass_context and access ctx.obj
        cli.context_settings = cli.context_settings or {}
        cli.context_settings["obj"] = context_factory()
