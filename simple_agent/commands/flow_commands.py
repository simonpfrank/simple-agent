"""REPL commands for flow management."""

from typing import Any

from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

import yaml


class FlowCommands:
    """Provides REPL commands for orchestrator flow management.

    Commands:
        /flow list - List available flows
        /flow show <name> - Display flow definition
        /flow run <name> <input> - Execute flow
        /flow delete <name> - Delete flow
    """

    def __init__(self, flow_manager: Any) -> None:
        """Initialize FlowCommands.

        Args:
            flow_manager: FlowManager instance for flow operations
        """
        self.flow_manager = flow_manager

    def list_flows(self) -> str:
        """List all available flows.

        Returns:
            Formatted table of available flows
        """
        flows = self.flow_manager.list_flows()

        if not flows:
            return "No flows available. Create one with /flow create"

        # Create rich table
        table = Table(title="Available Flows")
        table.add_column("Flow Name", style="cyan")
        table.add_column("Description", style="magenta")

        for flow_name in flows:
            flow_def = self.flow_manager.load_flow(flow_name)
            description = flow_def.get("description", "No description")
            table.add_row(flow_name, description)

        # Render to string
        from io import StringIO
        from rich.console import Console

        console_output = StringIO()
        console = Console(file=console_output)
        console.print(table)

        return console_output.getvalue()

    def show_flow(self, flow_name: str) -> str:
        """Display flow definition.

        Args:
            flow_name: Name of flow to display

        Returns:
            Formatted YAML display of flow
        """
        flow_def = self.flow_manager.load_flow(flow_name)

        # Validate flow
        is_valid, errors = self.flow_manager.validate_flow(flow_def)

        if not is_valid:
            return f"Flow validation failed: {', '.join(errors)}"

        # Convert to YAML for display
        yaml_str = yaml.dump(flow_def, default_flow_style=False, sort_keys=False)

        # Use Syntax for highlighting
        syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)

        from io import StringIO
        from rich.console import Console

        console_output = StringIO()
        console = Console(file=console_output)
        console.print(
            Panel(syntax, title=f"Flow: {flow_name}", expand=False)
        )

        return console_output.getvalue()

    def run_flow(self, flow_name: str, user_input: str) -> str:
        """Run a flow with input.

        Args:
            flow_name: Name of flow to execute
            user_input: Input for the orchestrator

        Returns:
            Output from orchestrator
        """
        # Load and validate flow
        flow_def = self.flow_manager.load_flow(flow_name)
        is_valid, errors = self.flow_manager.validate_flow(flow_def)

        if not is_valid:
            return f"Flow validation failed: {', '.join(errors)}"

        # Create and run orchestrator
        try:
            orchestrator = self.flow_manager.create_orchestrator(flow_def)
            result = orchestrator.run(user_input)

            # Format output with panel
            from io import StringIO
            from rich.console import Console

            console_output = StringIO()
            console = Console(file=console_output)
            console.print(
                Panel(result, title=f"Flow Result: {flow_name}", expand=False)
            )

            return console_output.getvalue()

        except Exception as e:
            return f"Error executing flow: {str(e)}"

    def delete_flow(self, flow_name: str) -> str:
        """Delete a flow file.

        Args:
            flow_name: Name of flow to delete

        Returns:
            Confirmation message
        """
        from pathlib import Path

        flow_path = Path(self.flow_manager.flows_dir) / f"{flow_name}.yaml"

        if not flow_path.exists():
            raise FileNotFoundError(f"Flow not found: {flow_name}")

        flow_path.unlink()

        # Remove from cache if present
        if flow_name in self.flow_manager.flows:
            del self.flow_manager.flows[flow_name]

        return f"✓ Deleted flow: {flow_name}"

    def debug_flow(self, flow_name: str, user_input: str) -> str:
        """Run flow in debug mode with detailed output.

        Args:
            flow_name: Name of flow to debug
            user_input: Input for the orchestrator

        Returns:
            Detailed execution output
        """
        flow_def = self.flow_manager.load_flow(flow_name)
        is_valid, errors = self.flow_manager.validate_flow(flow_def)

        if not is_valid:
            return f"Flow validation failed: {', '.join(errors)}"

        try:
            orchestrator = self.flow_manager.create_orchestrator(flow_def)

            # Run with verbose output
            from io import StringIO
            from rich.console import Console

            console_output = StringIO()
            console = Console(file=console_output)

            console.print(f"[bold]Flow:[/bold] {flow_name}")
            console.print(f"[bold]Input:[/bold] {user_input}")
            console.print(f"[bold]Orchestrator:[/bold] {orchestrator.name}")
            console.print(f"[bold]Sub-agents:[/bold] {', '.join(orchestrator.sub_agents.keys())}")
            console.print()

            # Run orchestrator
            result = orchestrator.run(user_input)

            console.print(f"[bold]Output:[/bold]\n{result}")

            return console_output.getvalue()

        except Exception as e:
            return f"Error debugging flow: {str(e)}"
