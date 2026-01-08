"""Unit tests for OutputCapture handling of newlines."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add cli_repl_kit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simple_agent" / "lib" / "cli_repl_kit"))

from cli_repl_kit.core.output_capture import OutputCapture


class TestOutputCaptureNewlines:
    """Test that OutputCapture correctly strips trailing newlines."""

    @pytest.fixture
    def config(self) -> Mock:
        """Create mock config."""
        config = Mock()
        config.colors = Mock()
        config.colors.error = "red"
        return config

    @pytest.fixture
    def captured_lines(self) -> list:
        """Collect captured output."""
        return []

    @pytest.fixture
    def capture(self, config: Mock, captured_lines: list) -> OutputCapture:
        """Create OutputCapture with mock callback."""
        def callback(formatted_text):
            captured_lines.append(formatted_text)
        return OutputCapture("stdout", callback, config)

    def test_write_strips_trailing_newline(
        self, capture: OutputCapture, captured_lines: list
    ) -> None:
        """Text with trailing newline should have it stripped."""
        capture.write("Hello world\n")

        assert len(captured_lines) == 1
        # The text should NOT have trailing newline - callback should receive clean text
        assert captured_lines[0] == [("", "Hello world")]

    def test_write_preserves_text_without_newline(
        self, capture: OutputCapture, captured_lines: list
    ) -> None:
        """Text without trailing newline should be preserved as-is."""
        capture.write("Hello world")

        assert len(captured_lines) == 1
        assert captured_lines[0] == [("", "Hello world")]

    def test_write_skips_empty_text(
        self, capture: OutputCapture, captured_lines: list
    ) -> None:
        """Empty text should not trigger callback."""
        result = capture.write("")

        assert result == 0
        assert len(captured_lines) == 0

    def test_write_skips_lone_newline(
        self, capture: OutputCapture, captured_lines: list
    ) -> None:
        """Single newline should not trigger callback."""
        result = capture.write("\n")

        assert result == 0
        assert len(captured_lines) == 0

    def test_write_multiline_text(
        self, capture: OutputCapture, captured_lines: list
    ) -> None:
        """Multiline text should be split and each line captured separately."""
        capture.write("line1\nline2\nline3\n")

        # Should produce 3 lines
        assert len(captured_lines) == 3
        assert captured_lines[0] == [("", "line1")]
        assert captured_lines[1] == [("", "line2")]
        assert captured_lines[2] == [("", "line3")]

    def test_stderr_uses_error_color(
        self, config: Mock, captured_lines: list
    ) -> None:
        """Stderr output should use error color from config."""
        def callback(formatted_text):
            captured_lines.append(formatted_text)

        capture = OutputCapture("stderr", callback, config)
        capture.write("Error message\n")

        assert len(captured_lines) == 1
        assert captured_lines[0] == [("red", "Error message")]
