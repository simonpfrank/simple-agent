"""
Business logic commands - example processing command.
"""

import click
import logging

from rich.console import Console
from rich.table import Table

from repl_cli_template.core.processor import process_data
from repl_cli_template.ui.styles import APP_THEME, format_success, format_error

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


@click.command()
@click.option("--input", "-i", "input_file", required=True, help="Input file path")
@click.option("--output", "-o", default=None, help="Output file path (optional)")
@click.pass_context
def process(context, input_file, output):
    """Process data from input file (example command)."""
    console = _get_console(context)

    try:
        # Get config from context
        config = context.obj.get("config", {})

        # Override output path if specified (CLI arg overrides config)
        if output:
            if "paths" not in config:
                config["paths"] = {}
            config["paths"]["output_dir"] = output

        # Call core business logic (handles file validation, etc.)
        result = process_data(input_file, config)

        # Rich formatted output
        console.print()
        if result["status"] == "success":
            console.print(format_success(result["message"]))

            # Display results in a table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Rows Processed", str(result["rows"]))
            table.add_row("Output File", result["output"])

            console.print(table)
        else:
            console.print(format_error("Processing completed with errors"))
            if "errors" in result:
                for error in result["errors"]:
                    console.print(f"  [yellow]•[/yellow] {error}")

        console.print()

    except Exception as e:
        # Catchall exception handler - core has already logged details
        console.print()
        console.print(format_error(str(e)))
        logger.exception(f"Command failed: {str(e)}")
        console.print()
        raise click.Abort()
