"""
Token statistics and management commands for REPL/CLI.

Provides /token command group for viewing and managing token usage statistics
and budget information across agents.
"""

import click
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from simple_agent.core.token_tracker_persistence import TokenTrackerManager
from simple_agent.ui.styles import APP_THEME

logger = logging.getLogger(__name__)


def _get_console(context: click.Context) -> Console:
    """
    Get console from context with fallback.

    Args:
        context: Click context object

    Returns:
        Console instance from context, or new instance if not found
    """
    return context.obj.get("console", Console(theme=APP_THEME))


def _get_token_manager() -> TokenTrackerManager:
    """
    Get or create TokenTrackerManager instance.

    Returns:
        TokenTrackerManager instance using default path
    """
    manager = TokenTrackerManager()
    manager.load()
    return manager


@click.group()
@click.pass_context
def token(ctx):
    """Token usage statistics and budget management commands."""
    pass


@token.command("stats")
@click.option("--agent", "-a", default=None, help="Filter by agent name")
@click.option("--period", "-p", default=24, type=int, help="Time period in hours (default: 24)")
@click.pass_context
def token_stats(ctx, agent: Optional[str], period: int):
    """
    Show token usage statistics.

    Displays token usage, costs, and model information for all agents or a
    specific agent over a time period.

    Examples:
        /token stats                    # Show all stats for last 24 hours
        /token stats --agent researcher  # Show stats for specific agent
        /token stats --period 7         # Show stats for last 7 days
        /token stats -a researcher -p 24  # Researcher stats for last 24 hours
    """
    console = _get_console(ctx)
    manager = _get_token_manager()

    console.print()

    if agent:
        # Show stats for specific agent
        agent_stats = manager.get_agent_stats_for_period(agent, hours=period)

        if agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent}'[/yellow]")
            console.print()
            return

        # Create table for agent stats
        table = Table(title=f"Token Usage: {agent} (last {period} hours)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Input Tokens", str(agent_stats.get("input_tokens", 0)))
        table.add_row("Output Tokens", str(agent_stats.get("output_tokens", 0)))
        table.add_row("Total Tokens", str(agent_stats.get("total_tokens", 0)))
        cost = agent_stats.get("cost", 0.0)
        table.add_row("Cost (USD)", f"${cost:.6f}")

        console.print(table)
    else:
        # Show overall stats for all agents
        overall_stats = manager.get_stats_for_period(hours=period)

        if overall_stats is None or overall_stats.get("total_tokens", 0) == 0:
            console.print(f"[yellow]No token usage recorded for the last {period} hours[/yellow]")
            console.print()
            return

        # Create table for overall stats
        table = Table(title=f"Overall Token Usage (last {period} hours)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Input Tokens", str(overall_stats.get("input_tokens", 0)))
        table.add_row("Output Tokens", str(overall_stats.get("output_tokens", 0)))
        table.add_row("Total Tokens", str(overall_stats.get("total_tokens", 0)))
        cost = overall_stats.get("cost", 0.0)
        table.add_row("Cost (USD)", f"${cost:.6f}")

        console.print(table)

        # Show per-agent breakdown
        console.print()
        console.print("[bold]Per-Agent Breakdown:[/bold]")
        console.print()

        all_agents = manager.get_all_agent_stats()
        if all_agents:
            agent_table = Table()
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Tokens", style="green")
            agent_table.add_column("Cost (USD)", style="green")

            for agent_name, stats in sorted(all_agents.items()):
                # Get stats for period
                agent_period_stats = manager.get_agent_stats_for_period(agent_name, hours=period)
                if agent_period_stats and agent_period_stats.get("total_tokens", 0) > 0:
                    tokens = agent_period_stats.get("total_tokens", 0)
                    cost = agent_period_stats.get("cost", 0.0)
                    agent_table.add_row(agent_name, str(tokens), f"${cost:.6f}")

            if agent_table.rows:
                console.print(agent_table)
            else:
                console.print("[dim]No agents with token usage in this period[/dim]")
        else:
            console.print("[dim]No agents have recorded token usage[/dim]")

    console.print()


@token.command("export")
@click.option("--format", "-f", type=click.Choice(["json", "csv"]), default="json",
              help="Export format (json or csv)")
@click.option("--agent", "-a", default=None, help="Filter by agent name")
@click.option("--period", "-p", default=24, type=int, help="Time period in hours (default: 24)")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.pass_context
def token_export(ctx, format: str, agent: Optional[str], period: int, output: Optional[str]):
    """
    Export token statistics to file.

    Exports token usage data in JSON or CSV format for analysis and reporting.

    Examples:
        /token export                                    # JSON export to stdout
        /token export --format csv                       # CSV export to stdout
        /token export -f json -o stats.json             # Save to file
        /token export -f csv -a researcher -o researcher.csv  # CSV for specific agent
    """
    console = _get_console(ctx)
    manager = _get_token_manager()

    console.print()

    # Prepare data
    if agent:
        data = {
            "agent": agent,
            "period_hours": period,
            "exported_at": datetime.now().isoformat(),
            "stats": manager.get_agent_stats_for_period(agent, hours=period) or {},
        }
    else:
        data = {
            "period_hours": period,
            "exported_at": datetime.now().isoformat(),
            "overall_stats": manager.get_stats_for_period(hours=period) or {},
            "per_agent_stats": {},
        }

        # Add per-agent stats if not filtering by agent
        for agent_name in manager.get_all_agent_stats().keys():
            agent_stats = manager.get_agent_stats_for_period(agent_name, hours=period)
            if agent_stats and agent_stats.get("total_tokens", 0) > 0:
                data["per_agent_stats"][agent_name] = agent_stats

    if format == "json":
        export_data = json.dumps(data, indent=2)
        content_type = "JSON"
    else:  # csv
        # Convert to CSV format
        rows = []
        if agent:
            stats = data.get("stats", {})
            rows.append(["Metric", "Value"])
            rows.append(["Agent", agent])
            rows.append(["Input Tokens", str(stats.get("input_tokens", 0))])
            rows.append(["Output Tokens", str(stats.get("output_tokens", 0))])
            rows.append(["Total Tokens", str(stats.get("total_tokens", 0))])
            rows.append(["Cost (USD)", str(stats.get("cost", 0.0))])
        else:
            overall = data.get("overall_stats", {})
            per_agent = data.get("per_agent_stats", {})

            # Overall stats rows
            rows.append(["Type", "Agent", "Input Tokens", "Output Tokens", "Total Tokens", "Cost (USD)"])
            rows.append(["Overall", "—", str(overall.get("input_tokens", 0)),
                        str(overall.get("output_tokens", 0)), str(overall.get("total_tokens", 0)),
                        str(overall.get("cost", 0.0))])

            # Per-agent rows
            for agent_name, stats in per_agent.items():
                rows.append(["Agent", agent_name, str(stats.get("input_tokens", 0)),
                           str(stats.get("output_tokens", 0)), str(stats.get("total_tokens", 0)),
                           str(stats.get("cost", 0.0))])

        # Convert rows to CSV
        import io
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(rows)
        export_data = csv_buffer.getvalue()
        content_type = "CSV"

    # Output or save
    if output:
        output_path = Path(output)
        output_path.write_text(export_data)
        console.print(f"[green]✓[/green] {content_type} exported to: {output_path.absolute()}")
    else:
        console.print(f"[cyan]{content_type} Export:[/cyan]")
        console.print()
        console.print(export_data)

    console.print()


@token.command("budget")
@click.argument("agent_name", required=False)
@click.option("--set", "-s", type=int, default=None, help="Set new budget for agent")
@click.pass_context
def token_budget(ctx, agent_name: Optional[str], set: Optional[int]):
    """
    Show or set token budget for an agent.

    Displays current token budget and usage, or sets a new budget for runtime
    override.

    Examples:
        /token budget researcher           # Show budget for agent
        /token budget researcher --set 15000  # Set new budget
        /token budget researcher -s 25000    # Set budget for orchestration
    """
    console = _get_console(ctx)

    if not agent_name:
        console.print()
        console.print("[yellow]Error:[/yellow] Agent name required")
        console.print()
        console.print("[dim]Usage: /token budget <agent_name> [--set <budget>][/dim]")
        console.print()
        return

    manager = _get_token_manager()
    agent_stats = manager.get_agent_stats(agent_name)

    console.print()

    if set is not None:
        # Set new budget
        if set <= 0:
            console.print("[red]Error:[/red] Budget must be greater than 0")
            console.print()
            return

        # Store budget in a simple way (in agent stats)
        if agent_name not in manager._agent_stats:
            manager._agent_stats[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "executions": [],
                "token_budget": set,
            }
        else:
            manager._agent_stats[agent_name]["token_budget"] = set

        manager.save()
        console.print(f"[green]✓[/green] Token budget for '{agent_name}' set to {set:,} tokens")
    else:
        # Show budget info
        if agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent_name}'[/yellow]")
            console.print()
            return

        # Create table for budget info
        table = Table(title=f"Token Budget: {agent_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        total_tokens = agent_stats.get("total_tokens", 0)
        cost = agent_stats.get("cost", 0.0)
        token_budget = agent_stats.get("token_budget", None)

        table.add_row("Total Tokens Used", f"{total_tokens:,}")
        table.add_row("Total Cost (USD)", f"${cost:.6f}")

        if token_budget:
            percentage = (total_tokens / token_budget * 100) if token_budget > 0 else 0
            remaining = token_budget - total_tokens
            table.add_row("Token Budget", f"{token_budget:,}")
            table.add_row("Tokens Remaining", f"{remaining:,}")
            table.add_row("Usage (%)", f"{percentage:.1f}%")

        console.print(table)

    console.print()


@token.command("cost")
@click.option("--agent", "-a", default=None, help="Filter by agent name")
@click.option("--by", type=click.Choice(["agent", "model"]), default="agent",
              help="Group cost by agent (default) or model")
@click.pass_context
def token_cost(ctx, agent: Optional[str], by: str):
    """
    Show cost breakdown by agent or model.

    Displays cumulative cost and per-execution costs for all agents or a
    specific agent.

    Examples:
        /token cost                    # Show cost breakdown by agent
        /token cost --by model         # Show cost breakdown by model
        /token cost --agent researcher  # Show costs for specific agent
    """
    console = _get_console(ctx)
    manager = _get_token_manager()

    console.print()

    if agent:
        # Show costs for specific agent
        agent_stats = manager.get_agent_stats(agent)

        if agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent}'[/yellow]")
            console.print()
            return

        # Create table for agent costs
        table = Table(title=f"Cost Breakdown: {agent}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        total_cost = agent_stats.get("cost", 0.0)
        executions = agent_stats.get("executions", [])

        table.add_row("Total Cost (USD)", f"${total_cost:.6f}")
        table.add_row("Number of Executions", str(len(executions)))

        if executions:
            avg_cost = total_cost / len(executions)
            table.add_row("Average Cost per Execution", f"${avg_cost:.6f}")

        console.print(table)

        # Show execution history if requested
        if executions and len(executions) <= 10:
            console.print()
            console.print("[bold]Recent Executions:[/bold]")
            console.print()

            exec_table = Table()
            exec_table.add_column("Model", style="cyan")
            exec_table.add_column("Tokens", style="green")
            exec_table.add_column("Cost (USD)", style="green")
            exec_table.add_column("Time", style="dim")

            for execution in executions[-10:]:
                tokens = execution.get("input_tokens", 0) + execution.get("output_tokens", 0)
                cost = execution.get("cost", 0.0)
                timestamp = execution.get("timestamp", "")
                # Format timestamp to show only time
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M:%S")
                    except:
                        time_str = timestamp[-8:]
                else:
                    time_str = "—"

                exec_table.add_row(execution.get("model", "unknown"), str(tokens), f"${cost:.6f}", time_str)

            console.print(exec_table)

    else:
        # Show overall cost breakdown
        if by == "agent":
            # Group by agent
            console.print("[bold]Cost Breakdown by Agent:[/bold]")
            console.print()

            table = Table()
            table.add_column("Agent", style="cyan")
            table.add_column("Total Cost (USD)", style="green")
            table.add_column("Executions", style="dim")

            all_agents = manager.get_all_agent_stats()
            total_overall = 0.0

            for agent_name in sorted(all_agents.keys()):
                stats = all_agents[agent_name]
                cost = stats.get("cost", 0.0)
                executions = len(stats.get("executions", []))
                total_overall += cost

                if cost > 0 or executions > 0:
                    table.add_row(agent_name, f"${cost:.6f}", str(executions))

            if table.rows:
                console.print(table)
                console.print()
                console.print(f"[bold]Total Cost (All Agents):[/bold] ${total_overall:.6f}")
            else:
                console.print("[dim]No cost data recorded[/dim]")

        else:
            # Group by model
            console.print("[bold]Cost Breakdown by Model:[/bold]")
            console.print()

            model_costs = {}
            model_executions = {}

            all_agents = manager.get_all_agent_stats()
            for agent_stats in all_agents.values():
                for execution in agent_stats.get("executions", []):
                    model = execution.get("model", "unknown")
                    cost = execution.get("cost", 0.0)

                    if model not in model_costs:
                        model_costs[model] = 0.0
                        model_executions[model] = 0

                    model_costs[model] += cost
                    model_executions[model] += 1

            if model_costs:
                table = Table()
                table.add_column("Model", style="cyan")
                table.add_column("Total Cost (USD)", style="green")
                table.add_column("Executions", style="dim")

                total_overall = 0.0
                for model_name in sorted(model_costs.keys()):
                    cost = model_costs[model_name]
                    executions = model_executions[model_name]
                    total_overall += cost

                    table.add_row(model_name, f"${cost:.6f}", str(executions))

                console.print(table)
                console.print()
                console.print(f"[bold]Total Cost (All Models):[/bold] ${total_overall:.6f}")
            else:
                console.print("[dim]No cost data recorded[/dim]")

    console.print()
