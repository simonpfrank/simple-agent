"""REPL commands for approval management."""

from typing import Any, List, Optional

from rich.console import Console

from simple_agent.hitl.approval_manager import ApprovalManager


class ApprovalCommands:
    """Commands for managing approvals in REPL."""

    def __init__(self, approval_manager: ApprovalManager, console: Console):
        """Initialize ApprovalCommands.

        Args:
            approval_manager: ApprovalManager instance
            console: Rich Console for output
        """
        self.approval_manager = approval_manager
        self.console = console

    def approve(self) -> bool:
        """Approve the pending request.

        Returns:
            True if approved, False/None otherwise
        """
        result = self.approval_manager.approve()
        if result is True:
            self.console.print("[green]✓[/green] Request approved")
            return True
        else:
            self.console.print("[yellow]No pending approval to approve[/yellow]")
            return False

    def reject(self) -> bool:
        """Reject the pending request.

        Returns:
            False if rejected, True/None otherwise
        """
        result = self.approval_manager.reject()
        if result is False:
            self.console.print("[red]✗[/red] Request rejected")
            return False
        else:
            self.console.print("[yellow]No pending approval to reject[/yellow]")
            return True

    def get_history(self, limit: int = 10) -> List[str]:
        """Get approval history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of formatted history entries
        """
        history = self.approval_manager.get_history()
        if not history:
            return ["No approval history"]

        formatted = []
        for entry in history[-limit:]:
            tool = entry.get("tool_name", "unknown")
            decision = entry.get("decision", "unknown")

            # Handle both old format (timestamp) and new format (decided_at)
            timestamp = entry.get("timestamp") or entry.get("decided_at")
            if isinstance(timestamp, str):
                # Already formatted as string
                timestamp_str = timestamp
            else:
                # datetime object
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "unknown"

            formatted.append(f"[{timestamp_str}] {tool}: {decision}")

        return formatted

    def clear_history(self) -> None:
        """Clear approval history."""
        self.approval_manager.clear_history()
        self.console.print("[green]✓[/green] Approval history cleared")

    def show_pending(self) -> Optional[str]:
        """Show pending approval request.

        Returns:
            Formatted pending approval or None
        """
        pending = self.approval_manager.pending_approval
        if not pending:
            return None

        return f"Tool: {pending['tool_name']}\nPrompt: {pending['prompt']}"
