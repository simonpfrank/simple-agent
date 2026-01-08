"""Common utilities and helpers for CLI commands.

This module consolidates shared functionality used across multiple command modules
to reduce code duplication and improve maintainability.

Includes Rich styling and themes (previously in ui/styles.py).
"""

import click
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from simple_agent.core.token_tracker_persistence import TokenTrackerManager


# Custom theme for the application (moved from ui/styles.py)
APP_THEME = Theme(
    {
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "bold blue",
        "dim": "dim",
        "highlight": "bold cyan",
        "prompt": "bold magenta",
    }
)


# Common symbols (moved from ui/styles.py)
SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "arrow": "-",
    "bullet": "•",
}


def format_success(message: str) -> str:
    """Format a success message."""
    return f"[success]{SYMBOLS['success']}[/success] {message}"


def format_error(message: str) -> str:
    """Format an error message."""
    return f"[error]{SYMBOLS['error']} Error:[/error] {message}"


def format_warning(message: str) -> str:
    """Format a warning message."""
    return f"[warning]{SYMBOLS['warning']} Warning:[/warning] {message}"


def format_info(message: str) -> str:
    """Format an info message."""
    return f"[info]{SYMBOLS['info']}[/info] {message}"


def get_console(context: click.Context, strict: bool = False) -> Console:
    """Get console from Click context with optional error checking.

    Args:
        context: Click context object
        strict: If True, raises ValueError if console not found. If False (default),
                returns new Console instance with APP_THEME as fallback.

    Returns:
        Console instance from context or newly created instance

    Raises:
        ValueError: If strict=True and console not initialized in context
    """
    try:
        console = context.obj.get("console")
        if console:
            return console
    except (TypeError, AttributeError):
        pass

    if strict:
        raise ValueError(
            "Console not initialized in context. "
            "Ensure application properly initializes console in ctx.obj"
        )

    # Fallback to new instance
    return Console(theme=APP_THEME)


def get_token_manager(context: click.Context) -> TokenTrackerManager:
    """Get TokenTrackerManager from context, creating if needed.

    Uses singleton pattern - maintains single TokenTrackerManager instance
    in context for the duration of the command.

    Args:
        context: Click context object

    Returns:
        TokenTrackerManager instance from context

    Raises:
        ValueError: If context object is not properly initialized
    """
    try:
        if "token_manager" not in context.obj:
            context.obj["token_manager"] = TokenTrackerManager()
            context.obj["token_manager"].load()

        return context.obj["token_manager"]
    except (TypeError, AttributeError) as e:
        raise ValueError(
            "Context object not properly initialized. "
            "Ensure application creates ctx.obj as a dict."
        ) from e


def create_table(title: str, *columns: tuple[str, str]) -> Table:
    """Create a Rich Table with consistent styling.

    Args:
        title: Table title
        *columns: Variable number of (column_name, style) tuples

    Returns:
        Configured Rich Table instance

    Example:
        >>> table = create_table(
        ...     "Agent Stats",
        ...     ("Agent", "cyan"),
        ...     ("Tokens", "green"),
        ...     ("Cost", "yellow")
        ... )
    """
    table = Table(title=title)

    for col_name, style in columns:
        table.add_column(col_name, style=style)

    return table


def create_metric_table(title: str = "Metrics") -> Table:
    """Create a two-column metric table (Metric, Value).

    Args:
        title: Table title

    Returns:
        Configured Rich Table with Metric and Value columns
    """
    return create_table(title, ("Metric", "cyan"), ("Value", "green"))


def create_agent_table(title: str = "Agents") -> Table:
    """Create a table for agent information.

    Args:
        title: Table title

    Returns:
        Configured Rich Table with Agent and Details columns
    """
    return create_table(title, ("Agent", "cyan"), ("Details", "white"))


def create_model_table(title: str = "Models") -> Table:
    """Create a table for model information.

    Args:
        title: Table title

    Returns:
        Configured Rich Table with Model and Cost columns
    """
    return create_table(title, ("Model", "cyan"), ("Cost (USD)", "green"))
