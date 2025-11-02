"""Unit tests for HITL approval UI."""

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from simple_agent.hitl.approval_ui import ConsoleApprovalUI, QuietApprovalUI


class TestConsoleApprovalUI:
    """Test ConsoleApprovalUI."""

    def test_create_console_ui_with_custom_console(self):
        """Test creating UI with custom console."""
        console = Console()
        ui = ConsoleApprovalUI(console=console)
        assert ui.console is console

    def test_create_console_ui_with_default_console(self):
        """Test creating UI with default console."""
        ui = ConsoleApprovalUI()
        assert ui.console is not None

    @patch("simple_agent.hitl.approval_ui.Console.input")
    def test_show_approval_approved(self, mock_input):
        """Test approval response."""
        mock_input.return_value = "y"
        ui = ConsoleApprovalUI()

        request_data = {
            "tool_name": "email_send",
            "prompt": "Send email?",
            "preview_data": {"to": "test@example.com"},
        }

        result = ui.show_approval("req-1", request_data)
        assert result is True

    @patch("simple_agent.hitl.approval_ui.Console.input")
    def test_show_approval_rejected(self, mock_input):
        """Test rejection response."""
        mock_input.return_value = "n"
        ui = ConsoleApprovalUI()

        request_data = {
            "tool_name": "delete_file",
            "prompt": "Delete?",
        }

        result = ui.show_approval("req-2", request_data)
        assert result is False

    @patch("simple_agent.hitl.approval_ui.Console.input")
    def test_show_approval_alternative_responses(self, mock_input):
        """Test alternative approval responses."""
        ui = ConsoleApprovalUI()

        request_data = {"tool_name": "test", "prompt": "Test?"}

        # Test "yes"
        mock_input.return_value = "yes"
        assert ui.show_approval("req-1", request_data) is True

        # Test "no"
        mock_input.return_value = "no"
        assert ui.show_approval("req-2", request_data) is False

        # Test "approve"
        mock_input.return_value = "approve"
        assert ui.show_approval("req-3", request_data) is True

        # Test "reject"
        mock_input.return_value = "reject"
        assert ui.show_approval("req-4", request_data) is False

    @patch("simple_agent.hitl.approval_ui.Console.input")
    def test_show_approval_invalid_response(self, mock_input):
        """Test invalid response defaults to rejection."""
        mock_input.return_value = "maybe"
        ui = ConsoleApprovalUI()

        request_data = {"tool_name": "test", "prompt": "Test?"}
        result = ui.show_approval("req-1", request_data)

        assert result is False

    @patch("simple_agent.hitl.approval_ui.Console.input")
    def test_show_approval_keyboard_interrupt(self, mock_input):
        """Test keyboard interrupt defaults to rejection."""
        mock_input.side_effect = KeyboardInterrupt()
        ui = ConsoleApprovalUI()

        request_data = {"tool_name": "test", "prompt": "Test?"}
        result = ui.show_approval("req-1", request_data)

        assert result is False

    def test_show_message_info(self):
        """Test showing info message."""
        ui = ConsoleApprovalUI()
        # Should not raise
        ui.show_message("Test message", level="info")

    def test_show_message_warning(self):
        """Test showing warning message."""
        ui = ConsoleApprovalUI()
        # Should not raise
        ui.show_message("Warning message", level="warning")

    def test_show_message_error(self):
        """Test showing error message."""
        ui = ConsoleApprovalUI()
        # Should not raise
        ui.show_message("Error message", level="error")


class TestQuietApprovalUI:
    """Test QuietApprovalUI."""

    def test_show_approval_returns_none(self):
        """Test that quiet UI returns None (no decision)."""
        ui = QuietApprovalUI()
        request_data = {"tool_name": "test", "prompt": "Test?"}

        result = ui.show_approval("req-1", request_data)
        assert result is None

    def test_show_approval_stores_request(self):
        """Test that quiet UI stores last request."""
        ui = QuietApprovalUI()
        request_data = {"tool_name": "email", "prompt": "Send?"}

        ui.show_approval("req-1", request_data)
        assert ui.last_request == request_data

    def test_show_message_logs(self):
        """Test that show_message logs without error."""
        ui = QuietApprovalUI()
        # Should not raise
        ui.show_message("Test message", level="info")

    def test_set_default_decision(self):
        """Test setting default decision."""
        ui = QuietApprovalUI()
        ui.set_default_decision(True)
        assert ui.last_decision is True

        ui.set_default_decision(False)
        assert ui.last_decision is False
