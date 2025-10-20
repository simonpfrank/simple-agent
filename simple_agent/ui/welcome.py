"""
Welcome screen and ASCII art for REPL.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def generate_ascii_art(app_name: str = "REPL CLI") -> str:
    """
    Generate ASCII art for the application name.

    Note: This is a simple example. For custom ASCII art:
    - Use online generators like patorjk.com/software/taag
    - Choose a font style (e.g., "Standard", "Big", "Banner")
    - Replace the art below with your generated art

    Args:
        app_name: Application name (not used in this simple version)

    Returns:
        ASCII art string
    """
    # Example ASCII art - replace with your own!
    art = """
  ____  _____ ____  _       ____ _     ___
 |  _ \\| ____|  _ \\| |     / ___| |   |_ _|
 | |_) |  _| | |_) | |    | |   | |    | |
 |  _ <| |___|  __/| |___ | |___| |___ | |
 |_| \\_\\_____|_|   |_____| \\____|_____|___|
    """
    return art


def show_welcome(
    console: Console, app_name: str, version: str, config_file: str, log_file: str
) -> None:
    """
    Display welcome screen with ASCII art and status information.

    Args:
        console: Rich console instance
        app_name: Application name
        version: Application version
        config_file: Path to loaded config file
        log_file: Path to log file
    """
    # ASCII art
    art = generate_ascii_art(app_name)

    # Create welcome panel
    welcome_text = Text()
    welcome_text.append(art, style="bold cyan")
    welcome_text.append(f"\n\n  {app_name} ", style="bold white")
    welcome_text.append(f"v{version}", style="bold yellow")
    welcome_text.append("\n  Type ", style="dim")
    welcome_text.append("/help", style="bold green")
    welcome_text.append(" for available commands | ", style="dim")
    welcome_text.append("/quit", style="bold red")
    welcome_text.append(" to exit", style="dim")

    panel = Panel(welcome_text, border_style="bright_blue", padding=(1, 2))

    console.print(panel)
    console.print()

    # Status information
    console.print(f"[dim]Config loaded:[/dim] [cyan]{config_file}[/cyan]")
    console.print(f"[dim]Logging to:[/dim] [cyan]{log_file}[/cyan]")
    console.print(
        "[bold green]Ready![/bold green] [dim](/ for commands and space for sub commands)[/dim]"
    )
    console.print()


def show_goodbye(console: Console) -> None:
    """
    Display goodbye message when exiting REPL.

    Args:
        console: Rich console instance
    """
    console.print()
    console.print("[bold yellow]Goodbye![/bold yellow]")
