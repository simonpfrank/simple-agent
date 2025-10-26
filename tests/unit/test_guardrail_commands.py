"""Unit tests for guardrail REPL commands - TDD approach."""

from unittest.mock import Mock, patch

import pytest

from simple_agent.commands.guardrail_commands import GuardrailCommands
from simple_agent.guardrails.custom_rule import CustomRuleGuardrail
from simple_agent.guardrails.exceptions import GuardrailViolation
from simple_agent.guardrails.input_validators import PIIDetector


class TestGuardrailCommands:
    """Test guardrail REPL commands."""

    @pytest.fixture
    def guardrail_commands(self):
        """Create GuardrailCommands instance."""
        mock_agent_manager = Mock()
        return GuardrailCommands(mock_agent_manager)

    def test_test_guardrail_pii_redact(self, guardrail_commands):
        """Test /guardrail test command with PII redaction."""
        detector = PIIDetector(types=["email"], redact=True)

        result = guardrail_commands.test_guardrail(
            guardrail=detector, text="Contact john@example.com"
        )

        assert "[EMAIL]" in result
        assert "john@example.com" not in result

    def test_test_guardrail_pii_reject(self, guardrail_commands):
        """Test /guardrail test command with PII rejection."""
        detector = PIIDetector(types=["ssn"], redact=False)

        with pytest.raises(GuardrailViolation):
            guardrail_commands.test_guardrail(guardrail=detector, text="SSN: 123-45-6789")

    def test_test_guardrail_custom_rule(self, guardrail_commands):
        """Test /guardrail test command with custom rule."""
        uppercase_rule = CustomRuleGuardrail(lambda text: text.upper())

        result = guardrail_commands.test_guardrail(guardrail=uppercase_rule, text="hello")

        assert result == "HELLO"

    def test_list_guardrails_empty(self, guardrail_commands):
        """Test /guardrail list command with no guardrails."""
        guardrail_commands.agent_manager.get_agent.return_value.guardrails = []

        result = guardrail_commands.list_guardrails("test_agent")

        assert isinstance(result, list)

    def test_list_guardrails_with_items(self, guardrail_commands):
        """Test /guardrail list command with guardrails."""
        mock_agent = Mock()
        pii_detector = PIIDetector(types=["email"], redact=True)
        mock_agent.guardrails = [pii_detector]

        guardrail_commands.agent_manager.get_agent.return_value = mock_agent

        result = guardrail_commands.list_guardrails("test_agent")

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_add_guardrail_pii(self, guardrail_commands):
        """Test /guardrail add command with PII detector."""
        mock_agent = Mock()
        mock_guardrails_list = []
        mock_agent.guardrails = mock_guardrails_list
        guardrail_commands.agent_manager.get_agent.return_value = mock_agent

        result = guardrail_commands.add_guardrail(
            agent_name="test_agent",
            guardrail_type="pii_detector",
            redact=True,
            pii_types=["email"],
        )

        assert result is True
        assert len(mock_agent.guardrails) == 1
        assert isinstance(mock_agent.guardrails[0], PIIDetector)

    def test_add_guardrail_custom(self, guardrail_commands):
        """Test /guardrail add command with custom rule."""
        mock_agent = Mock()
        mock_guardrails_list = []
        mock_agent.guardrails = mock_guardrails_list
        guardrail_commands.agent_manager.get_agent.return_value = mock_agent

        result = guardrail_commands.add_guardrail(
            agent_name="test_agent", guardrail_type="custom", function="my_module.my_rule"
        )

        assert result is True
        assert len(mock_agent.guardrails) == 1
        assert isinstance(mock_agent.guardrails[0], CustomRuleGuardrail)

    def test_remove_guardrail(self, guardrail_commands):
        """Test /guardrail remove command."""
        pii_detector = PIIDetector(types=["email"], redact=True)
        mock_agent = Mock()
        mock_agent.guardrails = [pii_detector]

        guardrail_commands.agent_manager.get_agent.return_value = mock_agent

        result = guardrail_commands.remove_guardrail(agent_name="test_agent", index=0)

        # Should remove from list
        assert result is True
        assert len(mock_agent.guardrails) == 0

    def test_get_agent_not_found(self, guardrail_commands):
        """Test guardrail command when agent not found."""
        guardrail_commands.agent_manager.get_agent.return_value = None

        result = guardrail_commands.list_guardrails("nonexistent")

        assert result is None or isinstance(result, str)
