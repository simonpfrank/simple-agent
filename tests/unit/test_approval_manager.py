"""Unit tests for ApprovalManager - TDD approach."""

import tempfile
from datetime import datetime
from unittest.mock import Mock

import pytest

from simple_agent.hitl.approval_manager import ApprovalManager, ApprovalDecision
from simple_agent.hitl.approval_persistence import FileApprovalPersistence


class TestApprovalManager:
    """Test ApprovalManager class."""

    @pytest.fixture
    def approval_manager(self, tmp_path):
        """Create ApprovalManager instance."""
        # Use non-interactive mode for testing (no UI prompts)
        # Use tmp_path for persistence (pytest handles cleanup)
        persistence = FileApprovalPersistence(storage_dir=str(tmp_path))
        return ApprovalManager(
            persistence=persistence,
            enable_interactive=False,
        )

    def test_approval_manager_initialization(self, approval_manager):
        """Test ApprovalManager initializes correctly."""
        assert approval_manager.pending_approval is None
        assert approval_manager.history == []

    def test_request_approval_pending(self, approval_manager):
        """Test requesting approval creates pending request."""
        approval_manager.request_approval(
            tool_name="send_email",
            prompt="Approve sending email to john@example.com?",
            timeout=60,
            default_action="reject"
        )

        assert approval_manager.pending_approval is not None
        assert approval_manager.pending_approval["tool_name"] == "send_email"

    def test_approve_pending_request(self, approval_manager):
        """Test approving a pending request."""
        approval_manager.request_approval(
            tool_name="send_email",
            prompt="Approve?",
            timeout=60,
            default_action="reject"
        )

        result = approval_manager.approve()

        assert result is True
        assert approval_manager.pending_approval is None

    def test_reject_pending_request(self, approval_manager):
        """Test rejecting a pending request."""
        approval_manager.request_approval(
            tool_name="delete_file",
            prompt="Approve deletion?",
            timeout=60,
            default_action="reject"
        )

        result = approval_manager.reject()

        assert result is False
        assert approval_manager.pending_approval is None

    def test_no_pending_approval_to_approve(self, approval_manager):
        """Test approving when no request pending."""
        result = approval_manager.approve()
        assert result is None

    def test_no_pending_approval_to_reject(self, approval_manager):
        """Test rejecting when no request pending."""
        result = approval_manager.reject()
        assert result is None

    def test_approval_history_tracks_approval(self, approval_manager):
        """Test history tracks approved requests."""
        approval_manager.request_approval(
            tool_name="send_email",
            prompt="Approve?",
            timeout=60,
            default_action="reject"
        )
        approval_manager.approve()

        assert len(approval_manager.history) == 1
        assert approval_manager.history[0]["decision"] == "approved"
        assert approval_manager.history[0]["tool_name"] == "send_email"

    def test_approval_history_tracks_rejection(self, approval_manager):
        """Test history tracks rejected requests."""
        approval_manager.request_approval(
            tool_name="delete_file",
            prompt="Approve?",
            timeout=60,
            default_action="reject"
        )
        approval_manager.reject()

        assert len(approval_manager.history) == 1
        assert approval_manager.history[0]["decision"] == "rejected"

    def test_approval_history_has_timestamp(self, approval_manager):
        """Test history entries have timestamp."""
        approval_manager.request_approval(
            tool_name="test_tool",
            prompt="Approve?",
            timeout=60,
            default_action="reject"
        )
        before = datetime.now()
        approval_manager.approve()
        after = datetime.now()

        entry = approval_manager.history[0]
        assert "timestamp" in entry
        assert before <= entry["timestamp"] <= after

    def test_approval_history_multiple_entries(self, approval_manager):
        """Test history tracks multiple requests."""
        # First approval
        approval_manager.request_approval("tool1", "Approve?", 60, "reject")
        approval_manager.approve()

        # Second rejection
        approval_manager.request_approval("tool2", "Approve?", 60, "reject")
        approval_manager.reject()

        assert len(approval_manager.history) == 2
        assert approval_manager.history[0]["decision"] == "approved"
        assert approval_manager.history[1]["decision"] == "rejected"

    def test_get_approval_history(self, approval_manager):
        """Test retrieving approval history."""
        approval_manager.request_approval("tool1", "Approve?", 60, "reject")
        approval_manager.approve()

        history = approval_manager.get_history()

        assert len(history) == 1
        assert history[0]["tool_name"] == "tool1"

    def test_clear_approval_history(self, approval_manager):
        """Test clearing approval history."""
        approval_manager.request_approval("tool1", "Approve?", 60, "reject")
        approval_manager.approve()

        approval_manager.clear_history()

        assert len(approval_manager.history) == 0

    def test_pending_approval_stores_all_params(self, approval_manager):
        """Test pending approval stores all request parameters."""
        approval_manager.request_approval(
            tool_name="send_email",
            prompt="Send email to user?",
            timeout=45,
            default_action="reject",
            preview_data={"to": "user@example.com", "subject": "Hello"}
        )

        pending = approval_manager.pending_approval
        assert pending["tool_name"] == "send_email"
        assert pending["prompt"] == "Send email to user?"
        assert pending["timeout"] == 45
        assert pending["default_action"] == "reject"
        assert pending["preview_data"] == {"to": "user@example.com", "subject": "Hello"}

    def test_approval_decision_enum(self):
        """Test ApprovalDecision enum."""
        assert ApprovalDecision.APPROVED.value == "approved"
        assert ApprovalDecision.REJECTED.value == "rejected"

    def test_history_entry_format(self, approval_manager):
        """Test history entry has correct format."""
        approval_manager.request_approval(
            tool_name="test_tool",
            prompt="Test prompt",
            timeout=60,
            default_action="reject"
        )
        approval_manager.approve()

        entry = approval_manager.history[0]
        assert "tool_name" in entry
        assert "decision" in entry
        assert "timestamp" in entry
        assert "prompt" in entry

    def test_multiple_sequential_approvals(self, approval_manager):
        """Test multiple sequential approval requests."""
        for i in range(3):
            approval_manager.request_approval(
                tool_name=f"tool_{i}",
                prompt=f"Approve tool_{i}?",
                timeout=60,
                default_action="reject"
            )
            approval_manager.approve()

        assert len(approval_manager.history) == 3
        assert approval_manager.pending_approval is None

    def test_replacement_of_pending_approval(self, approval_manager):
        """Test that new request replaces pending approval."""
        approval_manager.request_approval("tool1", "Approve?", 60, "reject")
        approval_manager.request_approval("tool2", "Approve?", 60, "reject")

        assert approval_manager.pending_approval["tool_name"] == "tool2"
