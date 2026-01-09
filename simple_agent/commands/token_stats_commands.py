"""
Token statistics and management commands for REPL/CLI.

Provides /token command group for viewing and managing token usage statistics
and budget information across agents.
"""

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table

from simple_agent.core.token_tracker_persistence import TokenTrackerManager

logger = logging.getLogger(__name__)

# Constants for formatting and defaults
CURRENCY_DECIMAL_PLACES = 6
DEFAULT_TOKEN_STATS = {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "cost": 0.0,
    "executions": [],
}


def _get_console(context: click.Context) -> Console:
    """
    Get console from context, fails if not found.

    Args:
        context: Click context object

    Returns:
        Console instance from context

    Raises:
        ValueError: If console not initialized in context
    """
    try:
        return context.obj["console"]
    except (KeyError, TypeError) as e:
        raise ValueError(
            "Console not initialized in context. "
            "Ensure application properly initializes console in ctx.obj"
        ) from e


def _get_token_manager(context: click.Context) -> TokenTrackerManager:
    """
    Get TokenTrackerManager from context.

    Args:
        context: Click context object

    Returns:
        TokenTrackerManager instance from context
    """
    # Use singleton pattern - fetch from context instead of creating new instance
    if "token_manager" not in context.obj:
        context.obj["token_manager"] = TokenTrackerManager()
        context.obj["token_manager"].load()

    return context.obj["token_manager"]


def _has_stats(stats_dict: Optional[Dict]) -> bool:
    """Check if stats dict has recorded activity.

    Args:
        stats_dict: Stats dictionary to check

    Returns:
        True if stats exist and have data
    """
    return (
        stats_dict is not None and stats_dict.get("total_tokens", 0) > 0
    )


def _has_agents(agents_dict: Dict) -> bool:
    """Check if agents dict is non-empty.

    Args:
        agents_dict: Dictionary of agents

    Returns:
        True if agents exist
    """
    return bool(agents_dict)


def _get_stat(stats_dict: Dict, key: str, default: Any = None) -> Any:
    """Safely get stat with proper default.

    Args:
        stats_dict: Stats dictionary
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value from stats or default
    """
    if default is None:
        default = DEFAULT_TOKEN_STATS.get(key, 0)
    return stats_dict.get(key, default)


def _create_stat_table(title: str, stats_dict: Dict[str, Any]) -> Table:
    """Create a metric/value table from stats dictionary.

    Args:
        title: Table title
        stats_dict: Dict with input_tokens, output_tokens, total_tokens, cost

    Returns:
        Formatted Rich Table with consistent styling
    """
    table = Table(title=title, style="blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green", justify="right")

    table.add_row("Input Tokens", str(_get_stat(stats_dict, "input_tokens")))
    table.add_row("Output Tokens", str(_get_stat(stats_dict, "output_tokens")))
    table.add_row("Total Tokens", str(_get_stat(stats_dict, "total_tokens")))

    cost = _get_stat(stats_dict, "cost", 0.0)
    table.add_row("Cost (USD)", f"${cost:.{CURRENCY_DECIMAL_PLACES}f}")

    return table


def _validate_budget_input(budget: int) -> Optional[str]:
    """Validate budget input comprehensively.

    Args:
        budget: Budget value to validate

    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(budget, int):
        return "Budget must be an integer"

    if budget <= 0:
        return "Budget must be greater than 0"

    if budget > 1_000_000_000:
        return "Budget cannot exceed 1 billion tokens"

    return None


def _calculate_budget_percentage(used: int, budget: int) -> float:
    """Calculate percentage of budget used with safe division.

    Args:
        used: Tokens used
        budget: Token budget

    Returns:
        Percentage as float (0-100+)
    """
    if budget <= 0:
        return 0.0

    return (used / budget) * 100


def _calculate_remaining_budget(used: int, budget: int) -> int:
    """Calculate remaining budget tokens.

    Args:
        used: Tokens used
        budget: Token budget

    Returns:
        Remaining tokens (0 if over budget)
    """
    return max(0, budget - used)


def _collect_stats_data(
    manager: TokenTrackerManager,
    agent: Optional[str] = None,
    period: int = 24,
) -> Dict[str, Any]:
    """Collect stats data for export or display.

    Args:
        manager: TokenTrackerManager instance
        agent: Optional agent filter
        period: Time period in hours

    Returns:
        Dict with formatted stats data
    """
    if agent:
        return {
            "agent": agent,
            "period_hours": period,
            "exported_at": datetime.now().isoformat(),
            "stats": manager.get_agent_stats_for_period(agent, hours=period) or {},
        }

    # Get all agent stats with period filtering
    all_agent_stats = manager.get_all_agent_stats()
    per_agent_stats = {}

    for agent_name in all_agent_stats.keys():
        agent_stats = manager.get_agent_stats_for_period(agent_name, hours=period)
        if agent_stats and agent_stats.get("total_tokens", 0) > 0:
            per_agent_stats[agent_name] = agent_stats

    return {
        "period_hours": period,
        "exported_at": datetime.now().isoformat(),
        "overall_stats": manager.get_stats_for_period(hours=period) or {},
        "per_agent_stats": per_agent_stats,
    }


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
    manager = _get_token_manager(ctx)

    console.print()

    if agent:
        # Show stats for specific agent
        agent_stats = manager.get_agent_stats_for_period(agent, hours=period)

        if not _has_stats(agent_stats) or agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent}'[/yellow]")
            console.print()
            return

        table = _create_stat_table(
            f"Token Usage: {agent} (last {period} hours)", agent_stats
        )
        console.print(table)
    else:
        # Show overall stats for all agents
        overall_stats = manager.get_stats_for_period(hours=period)

        if not _has_stats(overall_stats):
            console.print(f"[yellow]No token usage recorded for the last {period} hours[/yellow]")
            console.print()
            return

        table = _create_stat_table(
            f"Overall Token Usage (last {period} hours)", overall_stats
        )
        console.print(table)

        # Show per-agent breakdown
        console.print()
        console.print("[bold]Per-Agent Breakdown:[/bold]")
        console.print()

        # Collect stats once to avoid redundant manager calls in loop
        agent_period_stats = _collect_stats_data(manager, period=period)
        per_agent = agent_period_stats.get("per_agent_stats", {})

        if per_agent:
            agent_table = Table(style="blue")
            agent_table.add_column("Agent", style="cyan", no_wrap=True)
            agent_table.add_column("Tokens", style="green", justify="right")
            agent_table.add_column("Cost (USD)", style="green", justify="right")

            for agent_name in sorted(per_agent.keys()):
                stats = per_agent[agent_name]
                tokens = _get_stat(stats, "total_tokens")
                cost = _get_stat(stats, "cost", 0.0)
                agent_table.add_row(agent_name, str(tokens), f"${cost:.{CURRENCY_DECIMAL_PLACES}f}")

            console.print(agent_table)
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
    manager = _get_token_manager(ctx)

    console.print()

    # Collect data once, reuse for both formats
    data = _collect_stats_data(manager, agent, period)

    if format == "json":
        export_data = json.dumps(data, indent=2)
        content_type = "JSON"
    else:  # csv
        export_data = _convert_to_csv(data, agent)
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


def _convert_to_csv(data: Dict[str, Any], agent: Optional[str]) -> str:
    """Convert stats data to CSV format.

    Args:
        data: Stats data dictionary
        agent: Agent filter (if any)

    Returns:
        CSV formatted string
    """
    rows: List[List[str]] = []

    if agent:
        stats = data.get("stats", {})
        rows.append(["Metric", "Value"])
        rows.append(["Agent", agent])
        rows.append(["Input Tokens", str(_get_stat(stats, "input_tokens"))])
        rows.append(["Output Tokens", str(_get_stat(stats, "output_tokens"))])
        rows.append(["Total Tokens", str(_get_stat(stats, "total_tokens"))])
        rows.append(["Cost (USD)", str(_get_stat(stats, "cost", 0.0))])
    else:
        overall = data.get("overall_stats", {})
        per_agent = data.get("per_agent_stats", {})

        # Overall stats rows
        rows.append(["Type", "Agent", "Input Tokens", "Output Tokens", "Total Tokens", "Cost (USD)"])
        rows.append([
            "Overall",
            "—",
            str(_get_stat(overall, "input_tokens")),
            str(_get_stat(overall, "output_tokens")),
            str(_get_stat(overall, "total_tokens")),
            str(_get_stat(overall, "cost", 0.0)),
        ])

        # Per-agent rows
        for agent_name, stats in per_agent.items():
            rows.append([
                "Agent",
                agent_name,
                str(_get_stat(stats, "input_tokens")),
                str(_get_stat(stats, "output_tokens")),
                str(_get_stat(stats, "total_tokens")),
                str(_get_stat(stats, "cost", 0.0)),
            ])

    # Convert rows to CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(rows)
    return csv_buffer.getvalue()


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

    # Comprehensive input validation for agent_name
    if not isinstance(agent_name, str) or not agent_name.strip():
        console.print()
        console.print("[red]Error:[/red] Agent name must be a non-empty string")
        console.print()
        return

    manager = _get_token_manager(ctx)

    console.print()

    if set is not None:
        # Comprehensive budget validation
        validation_error = _validate_budget_input(set)
        if validation_error:
            console.print(f"[red]Error:[/red] {validation_error}")
            console.print()
            return

        # Set new budget with validation
        try:
            manager.set_token_budget(agent_name, set)
            manager.save()
            console.print(f"[green]✓[/green] Token budget for '{agent_name}' set to {set:,} tokens")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        # Show budget info
        agent_stats = manager.get_agent_stats(agent_name)

        if agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent_name}'[/yellow]")
            console.print()
            return

        table = Table(title=f"Token Budget: {agent_name}", style="blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")

        total_tokens = _get_stat(agent_stats, "total_tokens")
        cost = _get_stat(agent_stats, "cost", 0.0)
        token_budget = agent_stats.get("token_budget")

        table.add_row("Total Tokens Used", f"{total_tokens:,}")
        table.add_row("Total Cost (USD)", f"${cost:.{CURRENCY_DECIMAL_PLACES}f}")

        if token_budget and token_budget > 0:
            # Improved budget calculation with safe division
            percentage = _calculate_budget_percentage(total_tokens, token_budget)
            remaining = _calculate_remaining_budget(total_tokens, token_budget)
            table.add_row("Token Budget", f"{token_budget:,}")
            table.add_row("Tokens Remaining", f"{remaining:,}")

            # Flag if over-budget or approaching limit
            if percentage > 100:
                table.add_row("Status", "[red]Over Budget[/red]")
            elif percentage >= 90:
                table.add_row("Status", "[yellow]Approaching Limit[/yellow]")
                table.add_row("Usage (%)", f"{percentage:.1f}%")
            else:
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
    manager = _get_token_manager(ctx)

    console.print()

    if agent:
        # Show costs for specific agent
        agent_stats = manager.get_agent_stats(agent)

        if agent_stats is None:
            console.print(f"[yellow]No stats found for agent '{agent}'[/yellow]")
            console.print()
            return

        table = Table(title=f"Cost Breakdown: {agent}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        total_cost = _get_stat(agent_stats, "cost", 0.0)
        executions = agent_stats.get("executions", [])

        table.add_row("Total Cost (USD)", f"${total_cost:.{CURRENCY_DECIMAL_PLACES}f}")
        table.add_row("Number of Executions", str(len(executions)))

        if executions:
            avg_cost = total_cost / len(executions)
            table.add_row("Average Cost per Execution", f"${avg_cost:.{CURRENCY_DECIMAL_PLACES}f}")

        console.print(table)

        # Show execution history if not too large
        if executions and len(executions) <= 10:
            console.print()
            console.print("[bold]Recent Executions:[/bold]")
            console.print()

            exec_table = Table(style="blue")
            exec_table.add_column("Model", style="cyan", no_wrap=True)
            exec_table.add_column("Tokens", style="green", justify="right")
            exec_table.add_column("Cost (USD)", style="green", justify="right")
            exec_table.add_column("Time", style="dim", justify="right")

            for execution in executions[-10:]:
                tokens = _format_execution_tokens(execution)
                cost = execution.get("cost", 0.0)
                time_str = _format_execution_time(execution.get("timestamp", ""))

                exec_table.add_row(
                    execution.get("model", "unknown"),
                    str(tokens),
                    f"${cost:.{CURRENCY_DECIMAL_PLACES}f}",
                    time_str,
                )

            console.print(exec_table)

    else:
        # Show overall cost breakdown
        if by == "agent":
            _show_cost_by_agent(console, manager)
        else:
            _show_cost_by_model(console, manager)

    console.print()


def _format_execution_tokens(execution: Dict[str, Any]) -> int:
    """Format execution tokens for display.

    Args:
        execution: Execution record

    Returns:
        Total tokens (input + output)
    """
    return execution.get("input_tokens", 0) + execution.get("output_tokens", 0)


def _format_execution_time(timestamp: str) -> str:
    """Format timestamp for display.

    Args:
        timestamp: ISO format timestamp

    Returns:
        Formatted time string (HH:MM:SS) or fallback
    """
    if not timestamp:
        return "—"

    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%H:%M:%S")
    except (ValueError, AttributeError, TypeError):
        return timestamp[-8:] if len(timestamp) >= 8 else "—"


def _show_cost_by_agent(console: Console, manager: TokenTrackerManager) -> None:
    """Show cost breakdown by agent.

    Args:
        console: Rich console for output
        manager: TokenTrackerManager instance
    """
    console.print("[bold]Cost Breakdown by Agent:[/bold]")
    console.print()

    table = Table(style="blue")
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Total Cost (USD)", style="green", justify="right")
    table.add_column("Executions", style="dim", justify="right")

    all_agents = manager.get_all_agent_stats()
    total_overall = 0.0

    for agent_name in sorted(all_agents.keys()):
        stats = all_agents[agent_name]
        cost = _get_stat(stats, "cost", 0.0)
        executions = len(stats.get("executions", []))
        total_overall += cost

        if cost > 0 or executions > 0:
            table.add_row(
                agent_name,
                f"${cost:.{CURRENCY_DECIMAL_PLACES}f}",
                str(executions),
            )

    if table.rows:
        console.print(table)
        console.print()
        console.print(f"[bold]Total Cost (All Agents):[/bold] ${total_overall:.{CURRENCY_DECIMAL_PLACES}f}")
    else:
        console.print("[dim]No cost data recorded[/dim]")


def _show_cost_by_model(console: Console, manager: TokenTrackerManager) -> None:
    """Show cost breakdown by model.

    Args:
        console: Rich console for output
        manager: TokenTrackerManager instance
    """
    console.print("[bold]Cost Breakdown by Model:[/bold]")
    console.print()

    model_costs: Dict[str, float] = {}
    model_executions: Dict[str, int] = {}

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
        table = Table(style="blue")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Total Cost (USD)", style="green", justify="right")
        table.add_column("Executions", style="dim", justify="right")

        total_overall = 0.0
        for model_name in sorted(model_costs.keys()):
            cost = model_costs[model_name]
            executions = model_executions[model_name]
            total_overall += cost

            table.add_row(
                model_name,
                f"${cost:.{CURRENCY_DECIMAL_PLACES}f}",
                str(executions),
            )

        console.print(table)
        console.print()
        console.print(f"[bold]Total Cost (All Models):[/bold] ${total_overall:.{CURRENCY_DECIMAL_PLACES}f}")
    else:
        console.print("[dim]No cost data recorded[/dim]")
