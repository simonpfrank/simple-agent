"""Human-in-the-Loop approval system for controlled tool execution.

Provides interactive approval requests with UI and persistence.
Issue 5-A: UI support (console-based approval dialogs)
Issue 5-B: Persistence support (file-based approval storage)
"""

from simple_agent.hitl.approval_manager import ApprovalDecision, ApprovalManager
from simple_agent.hitl.approval_persistence import ApprovalPersistence, FileApprovalPersistence
from simple_agent.hitl.approval_ui import ApprovalUIHandler, ConsoleApprovalUI, QuietApprovalUI
from simple_agent.hitl.exceptions import ApprovalRejected
from simple_agent.hitl.tool_wrapper import HITLTool

__all__ = [
    "ApprovalManager",
    "ApprovalDecision",
    "ApprovalPersistence",
    "FileApprovalPersistence",
    "ApprovalUIHandler",
    "ConsoleApprovalUI",
    "QuietApprovalUI",
    "HITLTool",
    "ApprovalRejected",
]
