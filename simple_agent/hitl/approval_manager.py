"""Approval management for human-in-the-loop tool execution.

Provides approval request/decision management with optional UI and persistence.
Issue 5-A: UI implementation (console approval dialogs)
Issue 5-B: Persistence implementation (file-based storage)
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from simple_agent.hitl.approval_persistence import ApprovalPersistence, FileApprovalPersistence
from simple_agent.hitl.approval_ui import ApprovalUIHandler, ConsoleApprovalUI, QuietApprovalUI

logger = logging.getLogger(__name__)


class ApprovalDecision(Enum):
    """Enumeration of approval decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class ApprovalManager:
    """Manage approval requests and decisions for tool execution.

    Provides interactive approval prompts via UI handler and persistent storage
    of approval decisions across sessions. Supports custom UI implementations
    (console, web, etc.) and persistence backends (file, database, etc.).

    Issues 5-A and 5-B: Adds UI (console) and persistence (file-based) support.
    """

    def __init__(
        self,
        ui_handler: Optional[ApprovalUIHandler] = None,
        persistence: Optional[ApprovalPersistence] = None,
        enable_interactive: bool = True,
    ):
        """Initialize ApprovalManager.

        Args:
            ui_handler: UI handler for displaying approval requests
                       (defaults to ConsoleApprovalUI)
            persistence: Persistence backend for saving decisions
                        (defaults to FileApprovalPersistence)
            enable_interactive: Whether to actually prompt user
                               (set False for automated/testing)
        """
        self.ui_handler = ui_handler or (ConsoleApprovalUI() if enable_interactive else QuietApprovalUI())
        self.persistence = persistence or FileApprovalPersistence()
        self.enable_interactive = enable_interactive
        self.pending_approval: Optional[Dict[str, Any]] = None
        self.pending_request_id: Optional[str] = None
        self.history: List[Dict[str, Any]] = []  # In-memory cache

    def request_approval(
        self,
        tool_name: str,
        prompt: str,
        timeout: int = 60,
        default_action: str = "reject",
        preview_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """Request user approval for a tool execution.

        Shows an interactive approval dialog (if enabled) and persists the request.

        Args:
            tool_name: Name of the tool requiring approval
            prompt: Approval prompt to display to user
            timeout: Timeout in seconds (default 60)
            default_action: Default action if timeout ("approve" or "reject")
            preview_data: Optional data to preview (e.g., email contents)
            request_id: Custom request ID (auto-generated if not provided)

        Returns:
            Request ID for tracking this approval
        """
        # Generate request ID if not provided
        if request_id is None:
            request_id = str(uuid.uuid4())

        # Store request data
        request_data = {
            "tool_name": tool_name,
            "prompt": prompt,
            "timeout": timeout,
            "default_action": default_action,
            "preview_data": preview_data,
        }

        # Persist the request
        self.persistence.save_request(request_id, request_data)
        logger.info(f"Created approval request {request_id} for tool: {tool_name}")

        # Store as pending for immediate decision if interactive
        self.pending_approval = request_data
        self.pending_request_id = request_id

        # Show UI if enabled
        if self.enable_interactive and self.ui_handler:
            decision = self.ui_handler.show_approval(request_id, request_data)
            if decision is not None:
                self._record_decision(request_id, decision)

        return request_id

    def approve(self, request_id: Optional[str] = None) -> Optional[bool]:
        """Approve a request.

        Args:
            request_id: Request to approve (uses pending if not provided)

        Returns:
            True if approval recorded, None if request not found
        """
        if request_id is None:
            request_id = self.pending_request_id

        if request_id is None:
            return None

        return self._record_decision(request_id, True)

    def reject(self, request_id: Optional[str] = None) -> Optional[bool]:
        """Reject a request.

        Args:
            request_id: Request to reject (uses pending if not provided)

        Returns:
            False if rejection recorded, None if request not found
        """
        if request_id is None:
            request_id = self.pending_request_id

        if request_id is None:
            return None

        return self._record_decision(request_id, False)

    def _record_decision(self, request_id: str, approved: bool) -> bool:
        """Record an approval decision in history and persistence.

        Args:
            request_id: Request ID
            approved: Whether approved (True) or rejected (False)

        Returns:
            Whether decision was recorded
        """
        # Get request from persistence
        request_data = self.persistence.load_request(request_id)
        if not request_data:
            logger.warning(f"Request not found: {request_id}")
            return False

        # Persist decision
        decision_str = ApprovalDecision.APPROVED.value if approved else ApprovalDecision.REJECTED.value
        self.persistence.save_decision(request_id, decision_str)

        # Update in-memory history
        entry = {
            "request_id": request_id,
            "tool_name": request_data.get("tool_name"),
            "decision": decision_str,
            "prompt": request_data.get("prompt"),
            "timestamp": datetime.now(),
        }
        self.history.append(entry)

        logger.info(f"Recorded approval decision: {request_id} -> {decision_str}")

        # Clear pending if this was the pending request
        if request_id == self.pending_request_id:
            self.pending_approval = None
            self.pending_request_id = None

        return approved

    def get_decision(self, request_id: str) -> Optional[ApprovalDecision]:
        """Get the decision for a request.

        Args:
            request_id: Request ID to check

        Returns:
            ApprovalDecision if decision exists, None if still pending
        """
        decision_str = self.persistence.load_decision(request_id)
        if decision_str is None:
            return None
        try:
            return ApprovalDecision(decision_str)
        except ValueError:
            return None

    def is_approved(self, request_id: str) -> bool:
        """Check if a request has been approved.

        Args:
            request_id: Request ID to check

        Returns:
            True if approved, False if rejected or pending
        """
        decision = self.get_decision(request_id)
        return decision == ApprovalDecision.APPROVED

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get approval history from persistence.

        Args:
            limit: Maximum number of records to return (None for all)

        Returns:
            List of approval decision records
        """
        persisted = self.persistence.load_history(limit)
        # Return persisted history (source of truth)
        return persisted

    def clear_history(self) -> None:
        """Clear approval history from persistence."""
        self.persistence.clear_history()
        self.history.clear()
        logger.info("Cleared approval history")
