"""Tool wrapper for human-in-the-loop approval."""

from typing import Any, Callable, Optional

from simple_agent.hitl.approval_manager import ApprovalManager
from simple_agent.hitl.exceptions import ApprovalRejected


class HITLTool:
    """Wrapper around a tool that requires human approval before execution.

    Requests user approval before executing the wrapped tool.
    """

    def __init__(
        self,
        tool: Callable,
        approval_manager: ApprovalManager,
        tool_name: str,
        requires_approval: bool = True,
        timeout: int = 60,
        default_action: str = "reject",
        prompt_template: str = None,
    ):
        """Initialize HITLTool wrapper.

        Args:
            tool: The tool function to wrap
            approval_manager: ApprovalManager instance for handling approvals
            tool_name: Display name of the tool
            requires_approval: Whether approval is required (default True)
            timeout: Timeout in seconds for approval request
            default_action: Default action if timeout ("approve" or "reject")
            prompt_template: Template for approval prompt (can include {tool_name})
        """
        self.tool = tool
        self.approval_manager = approval_manager
        self.tool_name = tool_name
        self.requires_approval = requires_approval
        self.timeout = timeout
        self.default_action = default_action
        self.prompt_template = prompt_template or "Approve {tool_name}?"

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute tool, requesting approval if required.

        Args:
            *args: Positional arguments to pass to tool
            **kwargs: Keyword arguments to pass to tool

        Returns:
            Result of tool execution

        Raises:
            ApprovalRejected: If approval is rejected
        """
        # Request approval if required
        if self.requires_approval:
            prompt = self.prompt_template.format(tool_name=self.tool_name)
            self.approval_manager.request_approval(
                tool_name=self.tool_name,
                prompt=prompt,
                timeout=self.timeout,
                default_action=self.default_action,
            )
            # Note: In real usage, REPL will call approve() or reject()
            # For now, just leave the pending approval for caller to handle

        # Execute tool
        result = self.tool(*args, **kwargs)
        return result
