"""Exceptions for HITL system."""


class ApprovalRejected(Exception):
    """Raised when a tool execution is rejected by user."""

    def __init__(self, tool_name: str, message: str = None):
        """Initialize ApprovalRejected.

        Args:
            tool_name: Name of the tool that was rejected
            message: Optional message describing the rejection
        """
        self.tool_name = tool_name
        self.message = message or f"Tool '{tool_name}' execution rejected by user"
        super().__init__(self.message)
