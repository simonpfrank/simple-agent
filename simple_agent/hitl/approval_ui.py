"""UI handlers for HITL approval requests.

Provides console-based and programmatic interfaces for displaying and
handling approval requests. Issue 5-A: Implements UI for interactive approvals.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)


class ApprovalUIHandler(ABC):
    """Abstract base class for approval UI implementations."""

    @abstractmethod
    def show_approval(self, request_id: str, request_data: Dict[str, Any]) -> Optional[bool]:
        """Display approval request and get user decision.

        Args:
            request_id: Unique request identifier
            request_data: Request data (tool_name, prompt, preview_data, etc.)

        Returns:
            True if approved, False if rejected, None if timeout/skipped
        """
        pass

    @abstractmethod
    def show_message(self, message: str, level: str = "info") -> None:
        """Display a message to the user.

        Args:
            message: Message to display
            level: Message level ("info", "warning", "error")
        """
        pass


class ConsoleApprovalUI(ApprovalUIHandler):
    """Console-based approval UI using Rich.

    Displays approval requests in an interactive terminal interface with
    formatted prompts and decision options.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize console UI.

        Args:
            console: Rich console instance (creates default if not provided)
        """
        self.console = console or Console()

    def show_approval(self, request_id: str, request_data: Dict[str, Any]) -> Optional[bool]:
        """Display approval request in console and get user decision.

        Args:
            request_id: Unique request identifier
            request_data: Request data (tool_name, prompt, preview_data, etc.)

        Returns:
            True if approved, False if rejected, None if timeout/skipped
        """
        # Extract request details
        tool_name = request_data.get("tool_name", "Unknown")
        prompt = request_data.get("prompt", "")
        preview_data = request_data.get("preview_data")

        # Build display content
        content = f"[bold]Tool:[/bold] {tool_name}\n"
        content += f"[dim][{datetime.now().strftime('%H:%M:%S')}][/dim]\n\n"
        content += f"{prompt}"

        # Add preview data if provided
        if preview_data:
            content += self._format_preview_data(preview_data)

        # Display request panel
        panel = Panel(
            content,
            title="[bold red]APPROVAL REQUIRED[/bold red]",
            expand=False,
            border_style="red",
        )
        self.console.print(panel)

        # Get user decision
        try:
            response = self.console.input(
                "[yellow]Approve? [y]es/[n]o:[/yellow] "
            ).strip().lower()

            if response in ("y", "yes", "approve"):
                self.console.print("[green]✓ Approved[/green]")
                return True
            elif response in ("n", "no", "reject"):
                self.console.print("[red]✗ Rejected[/red]")
                return False
            else:
                self.console.print("[yellow]⊘ Invalid response, defaulting to reject[/yellow]")
                return False

        except (KeyboardInterrupt, EOFError):
            self.console.print("[yellow]⊘ Interrupted, defaulting to reject[/yellow]")
            return False

    def show_message(self, message: str, level: str = "info") -> None:
        """Display a message to the user.

        Args:
            message: Message to display
            level: Message level ("info", "warning", "error")
        """
        if level == "error":
            self.console.print(f"[red]{message}[/red]")
        elif level == "warning":
            self.console.print(f"[yellow]{message}[/yellow]")
        else:  # info
            self.console.print(f"[blue]{message}[/blue]")

    def _format_preview_data(self, data: Dict[str, Any]) -> str:
        """Format preview data for display.

        Args:
            data: Data to format

        Returns:
            Formatted string for display
        """
        if not data:
            return ""

        content = "\n\n[dim bold]Preview Data:[/dim bold]"

        # Format as key-value pairs instead of table
        for key, value in data.items():
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            content += f"\n  [cyan]{key}:[/cyan] {value_str}"

        return content


class QuietApprovalUI(ApprovalUIHandler):
    """Silent approval UI that logs but doesn't interact with user.

    Used for automated testing or when no interactive UI is available.
    """

    def __init__(self):
        """Initialize quiet UI."""
        self.last_request: Optional[Dict[str, Any]] = None
        self.last_decision: Optional[bool] = None

    def show_approval(self, request_id: str, request_data: Dict[str, Any]) -> Optional[bool]:
        """Log approval request without user interaction.

        Args:
            request_id: Unique request identifier
            request_data: Request data

        Returns:
            None (no decision made)
        """
        self.last_request = request_data
        logger.info(
            f"Approval request: {request_data.get('tool_name')} "
            f"(request_id={request_id}) - not shown (quiet mode)"
        )
        return None

    def show_message(self, message: str, level: str = "info") -> None:
        """Log a message.

        Args:
            message: Message to log
            level: Message level
        """
        logger.log(
            {
                "error": logging.ERROR,
                "warning": logging.WARNING,
                "info": logging.INFO,
            }.get(level, logging.INFO),
            message,
        )

    def set_default_decision(self, approved: bool) -> None:
        """Set default decision for all requests (for testing).

        Args:
            approved: Whether to approve or reject requests
        """
        self.last_decision = approved
