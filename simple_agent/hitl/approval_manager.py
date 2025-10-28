"""Approval management for human-in-the-loop tool execution."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ApprovalDecision(Enum):
    """Enumeration of approval decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalManager:
    """Manage approval requests and decisions for tool execution.

    Handles interactive approval prompts, timeout logic, and approval history tracking.
    """

    def __init__(self):
        """Initialize ApprovalManager."""
        self.pending_approval: Optional[Dict[str, Any]] = None
        self.history: List[Dict[str, Any]] = []

    def request_approval(
        self,
        tool_name: str,
        prompt: str,
        timeout: int = 60,
        default_action: str = "reject",
        preview_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Request user approval for a tool execution.

        Args:
            tool_name: Name of the tool requiring approval
            prompt: Approval prompt to display to user
            timeout: Timeout in seconds (default 60)
            default_action: Default action if timeout ("approve" or "reject")
            preview_data: Optional data to preview (e.g., email contents)
        """
        self.pending_approval = {
            "tool_name": tool_name,
            "prompt": prompt,
            "timeout": timeout,
            "default_action": default_action,
            "preview_data": preview_data,
        }

    def approve(self) -> Optional[bool]:
        """Approve the pending request.

        Returns:
            True if approval recorded, None if no pending request
        """
        if not self.pending_approval:
            return None

        self._record_decision(ApprovalDecision.APPROVED.value)
        self.pending_approval = None
        return True

    def reject(self) -> Optional[bool]:
        """Reject the pending request.

        Returns:
            False if rejection recorded, None if no pending request
        """
        if not self.pending_approval:
            return None

        self._record_decision(ApprovalDecision.REJECTED.value)
        self.pending_approval = None
        return False

    def _record_decision(self, decision: str) -> None:
        """Record an approval decision in history.

        Args:
            decision: "approved" or "rejected"
        """
        if not self.pending_approval:
            return

        entry = {
            "tool_name": self.pending_approval["tool_name"],
            "decision": decision,
            "prompt": self.pending_approval["prompt"],
            "timestamp": datetime.now(),
        }
        self.history.append(entry)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get approval history.

        Returns:
            List of approval decision records
        """
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear approval history."""
        self.history.clear()
