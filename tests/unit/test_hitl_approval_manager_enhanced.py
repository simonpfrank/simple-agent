"""Unit tests for enhanced HITL ApprovalManager with UI and persistence."""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from simple_agent.hitl.approval_manager import ApprovalDecision, ApprovalManager
from simple_agent.hitl.approval_persistence import FileApprovalPersistence
from simple_agent.hitl.approval_ui import QuietApprovalUI


class TestApprovalManagerInitialization:
    """Test ApprovalManager initialization."""

    def test_create_with_defaults(self):
        """Test creating manager with default UI and persistence."""
        manager = ApprovalManager(enable_interactive=False)
        assert manager.ui_handler is not None
        assert manager.persistence is not None
        assert manager.pending_approval is None
        assert manager.pending_request_id is None

    def test_create_with_custom_ui_and_persistence(self):
        """Test creating manager with custom components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ui = QuietApprovalUI()
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            manager = ApprovalManager(ui_handler=ui, persistence=persistence)
            assert manager.ui_handler is ui
            assert manager.persistence is persistence

    def test_create_non_interactive(self):
        """Test creating non-interactive manager."""
        manager = ApprovalManager(enable_interactive=False)
        assert isinstance(manager.ui_handler, QuietApprovalUI)


class TestApprovalManagerRequestApproval:
    """Test request_approval method."""

    def test_request_approval_generates_id(self):
        """Test that request_approval generates UUID if not provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApprovalManager(
                persistence=FileApprovalPersistence(storage_dir=tmpdir),
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test_tool",
                prompt="Test?",
            )

            assert request_id is not None
            assert isinstance(request_id, str)
            assert len(request_id) > 0

    def test_request_approval_uses_custom_id(self):
        """Test that request_approval uses provided request ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApprovalManager(
                persistence=FileApprovalPersistence(storage_dir=tmpdir),
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test_tool",
                prompt="Test?",
                request_id="custom-id-123",
            )

            assert request_id == "custom-id-123"

    def test_request_approval_persists(self):
        """Test that request_approval persists the request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="email_send",
                prompt="Send email?",
                preview_data={"to": "test@example.com"},
            )

            # Verify persisted
            loaded = persistence.load_request(request_id)
            assert loaded is not None
            assert loaded["tool_name"] == "email_send"

    def test_request_approval_stores_pending(self):
        """Test that request_approval stores as pending."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApprovalManager(
                persistence=FileApprovalPersistence(storage_dir=tmpdir),
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )

            assert manager.pending_request_id == request_id
            assert manager.pending_approval is not None


class TestApprovalManagerDecisions:
    """Test approval/rejection decisions."""

    def test_approve_pending(self):
        """Test approving a pending request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )

            result = manager.approve()
            assert result is True

            # Verify decision was recorded
            history = persistence.load_history()
            assert len(history) == 1
            assert history[0]["decision"] == ApprovalDecision.APPROVED.value

    def test_reject_pending(self):
        """Test rejecting a pending request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )

            result = manager.reject()
            assert result is False

            # Verify decision was recorded
            history = persistence.load_history()
            assert history[0]["decision"] == ApprovalDecision.REJECTED.value

    def test_approve_with_explicit_id(self):
        """Test approving request by explicit ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            request_id = manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )

            # Clear pending
            manager.pending_request_id = None

            # Approve by explicit ID
            result = manager.approve(request_id=request_id)
            assert result is True

    def test_approve_no_pending(self):
        """Test approving when no pending request."""
        manager = ApprovalManager(enable_interactive=False)
        result = manager.approve()
        assert result is None

    def test_clears_pending_after_decision(self):
        """Test that pending is cleared after decision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApprovalManager(
                persistence=FileApprovalPersistence(storage_dir=tmpdir),
                enable_interactive=False,
            )

            manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )

            assert manager.pending_request_id is not None
            manager.approve()
            assert manager.pending_request_id is None


class TestApprovalManagerHistory:
    """Test history management."""

    def test_get_history(self):
        """Test getting approval history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            # Create and approve request
            manager.request_approval(
                tool_name="test1",
                prompt="Test?",
            )
            manager.approve()

            history = manager.get_history()
            assert len(history) == 1
            assert history[0]["decision"] == "approved"

    def test_get_history_with_limit(self):
        """Test getting history with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            # Create multiple requests
            for i in range(5):
                manager.request_approval(
                    tool_name=f"tool_{i}",
                    prompt="Test?",
                )
                manager.approve()

            history = manager.get_history(limit=2)
            assert len(history) == 2

    def test_clear_history(self):
        """Test clearing history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            # Create request and approve
            manager.request_approval(
                tool_name="test",
                prompt="Test?",
            )
            manager.approve()

            assert len(manager.get_history()) == 1

            # Clear
            manager.clear_history()
            assert len(manager.get_history()) == 0


class TestApprovalManagerIntegration:
    """Integration tests for ApprovalManager."""

    def test_multiple_requests_workflow(self):
        """Test handling multiple requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            manager = ApprovalManager(
                persistence=persistence,
                enable_interactive=False,
            )

            # Request 1: approve
            req1 = manager.request_approval(
                tool_name="email",
                prompt="Send email?",
            )
            manager.approve()

            # Request 2: reject
            req2 = manager.request_approval(
                tool_name="delete",
                prompt="Delete file?",
            )
            manager.reject()

            # Verify both recorded
            history = manager.get_history()
            assert len(history) == 2
            assert history[0]["tool_name"] == "email"
            assert history[0]["decision"] == "approved"
            assert history[1]["tool_name"] == "delete"
            assert history[1]["decision"] == "rejected"

    def test_persistence_survives_restart(self):
        """Test that history persists across manager restarts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first manager and make approval
            persistence1 = FileApprovalPersistence(storage_dir=tmpdir)
            manager1 = ApprovalManager(persistence=persistence1, enable_interactive=False)
            manager1.request_approval(tool_name="test", prompt="Test?")
            manager1.approve()

            # Create second manager and verify history
            persistence2 = FileApprovalPersistence(storage_dir=tmpdir)
            manager2 = ApprovalManager(persistence=persistence2, enable_interactive=False)
            history = manager2.get_history()

            assert len(history) == 1
            assert history[0]["decision"] == "approved"
