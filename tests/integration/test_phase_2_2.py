"""Integration tests for Phase 2.2 Human-in-the-Loop - TDD approach."""

import tempfile
from unittest.mock import Mock

import pytest

from simple_agent.commands.approval_commands import ApprovalCommands
from simple_agent.hitl import ApprovalManager, ApprovalRejected, HITLTool
from simple_agent.hitl.approval_persistence import FileApprovalPersistence


class TestPhase22Integration:
    """Integration tests for Phase 2.2 Human-in-the-Loop."""

    @pytest.fixture
    def approval_manager(self, tmp_path):
        """Create ApprovalManager for testing."""
        persistence = FileApprovalPersistence(storage_dir=str(tmp_path))
        return ApprovalManager(
            persistence=persistence,
            enable_interactive=False,
        )

    def test_approval_workflow_approve(self, approval_manager):
        """Test complete approval workflow with approval."""

        def send_email(recipient: str, subject: str) -> str:
            return f"Email sent to {recipient} with subject {subject}"

        tool = HITLTool(
            tool=send_email,
            approval_manager=approval_manager,
            tool_name="send_email",
            requires_approval=True,
            timeout=60,
            default_action="reject",
        )

        # Tool execution (requests approval)
        result = tool("user@example.com", "Hello")

        # Verify tool still executed
        assert result == "Email sent to user@example.com with subject Hello"

        # User approves
        approval_manager.approve()

        # Verify in history
        history = approval_manager.get_history()
        assert len(history) == 1
        assert history[0]["decision"] == "approved"

    def test_approval_workflow_reject(self, approval_manager):
        """Test complete approval workflow with rejection."""

        def delete_file(path: str) -> str:
            return f"File deleted: {path}"

        tool = HITLTool(
            tool=delete_file,
            approval_manager=approval_manager,
            tool_name="delete_file",
            requires_approval=True,
            timeout=30,
            default_action="reject",
        )

        # Tool execution (requests approval)
        result = tool("important.txt")

        # Tool executed, but approval pending
        assert result == "File deleted: important.txt"

        # User rejects
        approval_manager.reject()

        # Verify rejection in history
        history = approval_manager.get_history()
        assert len(history) == 1
        assert history[0]["decision"] == "rejected"

    def test_multiple_approval_requests(self, approval_manager):
        """Test multiple sequential approval requests."""

        def log_message(msg: str) -> str:
            return f"Logged: {msg}"

        tool = HITLTool(
            tool=log_message,
            approval_manager=approval_manager,
            tool_name="log",
            requires_approval=True,
        )

        # First request
        result1 = tool("First message")
        assert "First message" in result1
        approval_manager.approve()

        # Second request
        result2 = tool("Second message")
        assert "Second message" in result2
        approval_manager.reject()

        # Verify history
        history = approval_manager.get_history()
        assert len(history) == 2
        assert history[0]["decision"] == "approved"
        assert history[1]["decision"] == "rejected"

    def test_approval_commands_integration(self, approval_manager):
        """Test ApprovalCommands with ApprovalManager."""
        console = Mock()

        commands = ApprovalCommands(approval_manager, console)

        # Request approval
        approval_manager.request_approval(
            tool_name="test_tool", prompt="Approve?", timeout=60, default_action="reject"
        )

        # Use commands
        commands.approve()
        assert approval_manager.pending_approval is None

        # Check history
        history = commands.get_history()
        assert len(history) == 1
        assert "test_tool" in history[0]
        assert "approved" in history[0]

    def test_tool_with_approval_required_false(self, approval_manager):
        """Test tool executes directly when approval not required."""

        def quick_task() -> str:
            return "Task completed"

        tool = HITLTool(
            tool=quick_task,
            approval_manager=approval_manager,
            tool_name="quick_task",
            requires_approval=False,
        )

        # Should execute directly without approval
        result = tool()
        assert result == "Task completed"

        # No approval history
        history = approval_manager.get_history()
        assert len(history) == 0

    def test_approval_prompt_customization(self, approval_manager):
        """Test custom approval prompts."""

        def send_payment(amount: float) -> str:
            return f"Payment sent: ${amount}"

        tool = HITLTool(
            tool=send_payment,
            approval_manager=approval_manager,
            tool_name="send_payment",
            requires_approval=True,
            prompt_template="Approve {tool_name}?",
        )

        result = tool(100.50)
        assert "Payment sent: $100.5" in result

        # Check pending approval has custom prompt
        pending = approval_manager.pending_approval
        assert "send_payment" in pending["prompt"]

    def test_approval_history_clearing(self, approval_manager):
        """Test clearing approval history."""

        # Make some approvals
        for i in range(3):
            approval_manager.request_approval(
                tool_name=f"tool_{i}",
                prompt="Approve?",
                timeout=60,
                default_action="reject",
            )
            approval_manager.approve()

        assert len(approval_manager.get_history()) == 3

        # Clear
        approval_manager.clear_history()
        assert len(approval_manager.get_history()) == 0

    def test_approval_manager_in_isolation(self, approval_manager):
        """Test ApprovalManager works in isolation."""
        manager = approval_manager

        # Request 1
        manager.request_approval("tool1", "Approve?", 60, "reject")
        assert manager.pending_approval["tool_name"] == "tool1"

        manager.approve()
        assert manager.pending_approval is None
        assert len(manager.get_history()) == 1

    def test_hitl_tool_preserves_return_value(self, approval_manager):
        """Test HITLTool preserves tool return value."""

        def calculate(a: int, b: int) -> int:
            return a + b

        tool = HITLTool(
            tool=calculate,
            approval_manager=approval_manager,
            tool_name="calc",
            requires_approval=False,
        )

        result = tool(5, 3)
        assert result == 8

    def test_pending_approval_timeout_parameters(self, approval_manager):
        """Test pending approval stores timeout parameters."""

        approval_manager.request_approval(
            tool_name="test",
            prompt="Approve?",
            timeout=120,
            default_action="approve",
        )

        pending = approval_manager.pending_approval
        assert pending["timeout"] == 120
        assert pending["default_action"] == "approve"
