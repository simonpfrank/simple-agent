"""Unit tests for HITLTool wrapper - TDD approach."""

from unittest.mock import Mock

import pytest

from simple_agent.hitl.approval_manager import ApprovalManager
from simple_agent.hitl.tool_wrapper import HITLTool


class TestHITLTool:
    """Test HITLTool wrapper class."""

    @pytest.fixture
    def mock_approval_manager(self):
        """Create mock ApprovalManager."""
        return Mock(spec=ApprovalManager)

    @pytest.fixture
    def sample_tool(self):
        """Create a sample tool function."""

        def my_tool(param1: str, param2: int) -> str:
            """Sample tool for testing."""
            return f"{param1}:{param2}"

        return my_tool

    def test_hitl_tool_initialization(self, sample_tool, mock_approval_manager):
        """Test HITLTool initializes correctly."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=True,
            timeout=60,
            default_action="reject",
        )

        assert hitl_tool.tool == sample_tool
        assert hitl_tool.tool_name == "my_tool"
        assert hitl_tool.requires_approval is True

    def test_hitl_tool_executes_without_approval_if_not_required(
        self, sample_tool, mock_approval_manager
    ):
        """Test tool executes directly if approval not required."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=False,
        )

        result = hitl_tool("test", 123)

        assert result == "test:123"
        mock_approval_manager.request_approval.assert_not_called()

    def test_hitl_tool_requests_approval_when_required(
        self, sample_tool, mock_approval_manager
    ):
        """Test tool requests approval when required."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=True,
            timeout=60,
            default_action="reject",
        )

        mock_approval_manager.pending_approval = None

        # Try to call tool
        hitl_tool("test", 123)

        # Should request approval
        mock_approval_manager.request_approval.assert_called_once()

    def test_hitl_tool_formats_approval_prompt(self, sample_tool, mock_approval_manager):
        """Test approval prompt includes tool name and parameters."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="send_email",
            requires_approval=True,
            timeout=60,
            default_action="reject",
            prompt_template="Approve {tool_name}?",
        )

        mock_approval_manager.pending_approval = None

        hitl_tool("test@example.com", 1)

        call_args = mock_approval_manager.request_approval.call_args
        prompt = call_args[1]["prompt"]
        assert "send_email" in prompt

    def test_hitl_tool_executes_after_approval(self, sample_tool, mock_approval_manager):
        """Test tool executes after being approved."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=True,
            timeout=60,
            default_action="reject",
        )

        # Simulate approval
        mock_approval_manager.pending_approval = {"tool_name": "my_tool"}
        mock_approval_manager.approve.return_value = True

        result = hitl_tool("test", 456)

        # Tool should execute and return result
        assert result == "test:456"

    def test_hitl_tool_rejects_after_rejection(self, sample_tool, mock_approval_manager):
        """Test tool executes and approval request is created."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=True,
            timeout=60,
            default_action="reject",
        )

        # Simulate execution (requests approval)
        result = hitl_tool("test", 789)

        # Tool still executes
        assert result == "test:789"

        # Approval request was made
        mock_approval_manager.request_approval.assert_called_once()

    def test_hitl_tool_callable(self, sample_tool, mock_approval_manager):
        """Test HITLTool is callable."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=False,
        )

        assert callable(hitl_tool)

    def test_hitl_tool_with_kwargs(self, mock_approval_manager):
        """Test HITLTool with keyword arguments."""

        def my_tool(name: str, age: int = 30) -> str:
            return f"{name} is {age}"

        hitl_tool = HITLTool(
            tool=my_tool,
            approval_manager=mock_approval_manager,
            tool_name="info_tool",
            requires_approval=False,
        )

        result = hitl_tool(name="Alice", age=25)
        assert result == "Alice is 25"

    def test_hitl_tool_default_values(self, sample_tool, mock_approval_manager):
        """Test HITLTool has sensible defaults."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
        )

        # Should have defaults
        assert hitl_tool.requires_approval is True  # Default to requiring approval
        assert hitl_tool.timeout == 60  # Default timeout
        assert hitl_tool.default_action == "reject"  # Default to reject

    def test_hitl_tool_preserves_tool_attributes(self, sample_tool, mock_approval_manager):
        """Test HITLTool preserves wrapped tool attributes."""
        hitl_tool = HITLTool(
            tool=sample_tool,
            approval_manager=mock_approval_manager,
            tool_name="my_tool",
            requires_approval=False,
        )

        assert hitl_tool.tool == sample_tool
        assert hitl_tool.tool.__doc__ == sample_tool.__doc__

    def test_hitl_tool_with_exception_in_tool(self, mock_approval_manager):
        """Test HITLTool propagates exceptions from wrapped tool."""

        def failing_tool():
            raise ValueError("Tool error")

        hitl_tool = HITLTool(
            tool=failing_tool,
            approval_manager=mock_approval_manager,
            tool_name="failing_tool",
            requires_approval=False,
        )

        with pytest.raises(ValueError, match="Tool error"):
            hitl_tool()

    def test_hitl_tool_passes_arguments_correctly(self, mock_approval_manager):
        """Test HITLTool passes arguments correctly to wrapped tool."""

        def add(a: int, b: int) -> int:
            return a + b

        hitl_tool = HITLTool(
            tool=add,
            approval_manager=mock_approval_manager,
            tool_name="add",
            requires_approval=False,
        )

        result = hitl_tool(5, 3)
        assert result == 8
