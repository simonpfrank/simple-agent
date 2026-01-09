"""Tool wrapper for human-in-the-loop approval."""

import logging
from typing import Any, Callable, Optional

from simple_agent.hitl.approval_manager import ApprovalManager
from simple_agent.hitl.exceptions import ApprovalRejected

logger = logging.getLogger(__name__)


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
        prompt_template: Optional[str] = None,
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
            ApprovalRejected: If approval is rejected or not granted
        """
        logger.debug(f"[TOOL] HITLTool({self.tool_name}) - requires_approval={self.requires_approval}, args_count={len(args)}, kwargs_count={len(kwargs)}")

        # Request approval if required
        if self.requires_approval:
            prompt = self.prompt_template.format(tool_name=self.tool_name)
            logger.info(f"[APPROVAL] Requesting approval for tool: {self.tool_name}")
            request_id = self.approval_manager.request_approval(
                tool_name=self.tool_name,
                prompt=prompt,
                timeout=self.timeout,
                default_action=self.default_action,
            )

            # SECURITY FIX: Check if approval was granted before execution
            if not self.approval_manager.is_approved(request_id):
                logger.warning(f"[APPROVAL] Tool {self.tool_name} was not approved")
                raise ApprovalRejected(f"Tool '{self.tool_name}' was not approved for execution")

            logger.info(f"[APPROVAL] Tool {self.tool_name} approved, proceeding with execution")

        # Execute tool only if approved or no approval required
        try:
            logger.debug(f"[TOOL] Executing {self.tool_name}")
            result = self.tool(*args, **kwargs)
            logger.info(f"[TOOL] {self.tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"[TOOL] {self.tool_name} failed - {type(e).__name__}: {str(e)}")
            raise
