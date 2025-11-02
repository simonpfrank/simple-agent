"""Unit tests for HITL approval persistence."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from simple_agent.hitl.approval_persistence import FileApprovalPersistence


class TestFileApprovalPersistenceCreation:
    """Test FileApprovalPersistence initialization."""

    def test_create_persistence_with_default_dir(self):
        """Test creating persistence with default directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            assert persistence.storage_dir == Path(tmpdir)
            assert persistence.requests_file.exists()
            assert persistence.history_file.exists()

    def test_create_persistence_creates_directory(self):
        """Test that persistence creates storage directory if not exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "hitl_data"
            persistence = FileApprovalPersistence(storage_dir=str(storage_path))
            assert storage_path.exists()

    def test_initialization_creates_empty_files(self):
        """Test that initialization creates empty JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            # Verify files exist and are valid JSON
            requests_data = json.loads(persistence.requests_file.read_text())
            history_data = json.loads(persistence.history_file.read_text())

            assert requests_data == {}
            assert history_data == []


class TestFileApprovalPersistenceSaveLoad:
    """Test saving and loading approval requests."""

    def test_save_and_load_request(self):
        """Test saving and loading a single request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            request_data = {
                "tool_name": "email_send",
                "prompt": "Send email to user@example.com?",
                "preview_data": {"to": "user@example.com", "subject": "Test"},
            }

            persistence.save_request("req-123", request_data)
            loaded = persistence.load_request("req-123")

            assert loaded is not None
            assert loaded["tool_name"] == "email_send"
            assert loaded["prompt"] == "Send email to user@example.com?"
            assert "created_at" in loaded

    def test_load_nonexistent_request(self):
        """Test loading a request that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            loaded = persistence.load_request("nonexistent")
            assert loaded is None

    def test_save_multiple_requests(self):
        """Test saving multiple requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            for i in range(3):
                persistence.save_request(f"req-{i}", {"tool_name": f"tool_{i}"})

            # Verify all saved
            assert persistence.load_request("req-0") is not None
            assert persistence.load_request("req-1") is not None
            assert persistence.load_request("req-2") is not None


class TestFileApprovalPersistenceDecisions:
    """Test saving and loading approval decisions."""

    def test_save_and_load_approval_decision(self):
        """Test saving and loading an approval decision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            # Save request first
            persistence.save_request("req-123", {
                "tool_name": "email_send",
                "prompt": "Send?",
            })

            # Save decision
            persistence.save_decision("req-123", "approved")

            # Load and verify
            history = persistence.load_history()
            assert len(history) == 1
            assert history[0]["request_id"] == "req-123"
            assert history[0]["decision"] == "approved"

    def test_save_rejection_decision(self):
        """Test saving a rejection decision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            persistence.save_request("req-456", {
                "tool_name": "delete_file",
                "prompt": "Delete?",
            })

            persistence.save_decision("req-456", "rejected")

            history = persistence.load_history()
            assert history[0]["decision"] == "rejected"

    def test_load_history_with_limit(self):
        """Test loading history with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            # Create 5 requests
            for i in range(5):
                persistence.save_request(f"req-{i}", {"tool_name": f"tool_{i}"})
                persistence.save_decision(f"req-{i}", "approved")

            # Load with limit
            history = persistence.load_history(limit=2)
            assert len(history) == 2
            assert history[-1]["request_id"] == "req-4"


class TestFileApprovalPersistenceDelete:
    """Test deleting approval requests."""

    def test_delete_request(self):
        """Test deleting a request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            persistence.save_request("req-to-delete", {"tool_name": "test"})
            assert persistence.load_request("req-to-delete") is not None

            persistence.delete_request("req-to-delete")
            assert persistence.load_request("req-to-delete") is None

    def test_delete_nonexistent_request(self):
        """Test deleting a request that doesn't exist (should not error)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)
            # Should not raise
            persistence.delete_request("nonexistent")


class TestFileApprovalPersistenceClear:
    """Test clearing approval history."""

    def test_clear_history(self):
        """Test clearing all history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            # Add some history
            persistence.save_request("req-1", {"tool_name": "tool_1"})
            persistence.save_decision("req-1", "approved")

            assert len(persistence.load_history()) == 1

            # Clear
            persistence.clear_history()
            assert len(persistence.load_history()) == 0

    def test_clear_history_does_not_affect_requests(self):
        """Test that clearing history doesn't delete requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = FileApprovalPersistence(storage_dir=tmpdir)

            persistence.save_request("req-1", {"tool_name": "tool_1"})
            persistence.clear_history()

            # Request should still exist
            assert persistence.load_request("req-1") is not None
