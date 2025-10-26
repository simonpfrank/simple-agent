"""Unit tests for GuardrailAgent wrapper - TDD approach."""

from unittest.mock import Mock, patch

import pytest

from simple_agent.guardrails.custom_rule import CustomRuleGuardrail
from simple_agent.guardrails.exceptions import GuardrailViolation
from simple_agent.guardrails.guardrail_agent import GuardrailAgent
from simple_agent.guardrails.input_validators import PIIDetector


class TestGuardrailAgent:
    """Test GuardrailAgent wrapper class."""

    def test_guardrail_agent_wraps_agent(self):
        """Test GuardrailAgent wraps a SimpleAgent."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        guardrail_agent = GuardrailAgent(mock_agent)
        assert guardrail_agent.agent == mock_agent

    def test_run_without_guardrails(self):
        """Test run() without guardrails passes through."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        guardrail_agent = GuardrailAgent(mock_agent)
        result = guardrail_agent.run("Test prompt")

        assert result == "Response"
        mock_agent.run.assert_called_once_with("Test prompt")

    def test_run_with_single_input_guardrail(self):
        """Test run() applies single input guardrail."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        pii_detector = PIIDetector(types=["email"], redact=True)
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[pii_detector])

        result = guardrail_agent.run("Contact john@example.com")

        # Agent should receive redacted input
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args[0][0]
        assert "john@example.com" not in call_args
        assert "[EMAIL]" in call_args

    def test_run_with_multiple_input_guardrails(self):
        """Test run() applies multiple input guardrails in order."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        pii_detector = PIIDetector(types=["email"], redact=True)
        uppercase_rule = CustomRuleGuardrail(lambda text: text.upper())

        guardrail_agent = GuardrailAgent(
            mock_agent, input_guardrails=[pii_detector, uppercase_rule]
        )

        result = guardrail_agent.run("Contact john@example.com here")

        # Both guardrails should be applied
        call_args = mock_agent.run.call_args[0][0]
        assert "[EMAIL]" in call_args  # PII redacted
        assert call_args.isupper()  # Uppercased

    def test_run_rejects_on_guardrail_violation(self):
        """Test run() rejects input with guardrail violation."""
        mock_agent = Mock()

        pii_detector = PIIDetector(types=["email"], redact=False)  # Reject mode
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[pii_detector])

        with pytest.raises(GuardrailViolation):
            guardrail_agent.run("Email: john@example.com")

        # Agent should not be called
        mock_agent.run.assert_not_called()

    def test_empty_guardrails_list(self):
        """Test run() with empty guardrails list."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[])
        result = guardrail_agent.run("Test prompt")

        assert result == "Response"

    def test_guardrail_order_matters(self):
        """Test that guardrails are applied in order."""
        mock_agent = Mock()
        mock_agent.run.return_value = "Response"

        # First guardrail: replace "bad" with "good"
        rule1 = CustomRuleGuardrail(lambda text: text.replace("bad", "good"))
        # Second guardrail: uppercase
        rule2 = CustomRuleGuardrail(lambda text: text.upper())

        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[rule1, rule2])
        guardrail_agent.run("this is bad")

        call_args = mock_agent.run.call_args[0][0]
        assert call_args == "THIS IS GOOD"

    def test_custom_rule_guardrail_in_chain(self):
        """Test custom rule as part of guardrail chain."""

        def no_urls(text: str) -> str:
            if "http" in text:
                raise GuardrailViolation("URLs not allowed", guardrail_type="custom")
            return text

        mock_agent = Mock()
        custom_rule = CustomRuleGuardrail(no_urls)
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[custom_rule])

        # Should pass
        guardrail_agent.run("Normal text")
        assert mock_agent.run.called

        # Should fail
        mock_agent.reset_mock()
        with pytest.raises(GuardrailViolation):
            guardrail_agent.run("Visit https://example.com")
        assert not mock_agent.run.called

    def test_violation_contains_guardrail_info(self):
        """Test GuardrailViolation contains info about which guardrail failed."""
        mock_agent = Mock()
        pii_detector = PIIDetector(types=["ssn"], redact=False)
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[pii_detector])

        with pytest.raises(GuardrailViolation) as exc_info:
            guardrail_agent.run("SSN: 123-45-6789")

        assert "pii_detector" in str(exc_info.value)

    def test_access_wrapped_agent_attributes(self):
        """Test accessing attributes of wrapped agent."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.memory = []

        guardrail_agent = GuardrailAgent(mock_agent)
        assert guardrail_agent.agent.name == "test_agent"
        assert guardrail_agent.agent.memory == []

    def test_guardrail_agent_preserves_agent_reference(self):
        """Test GuardrailAgent preserves reference to wrapped agent."""
        mock_agent = Mock()
        guardrail_agent = GuardrailAgent(mock_agent)

        # Modifying the wrapped agent should be visible
        mock_agent.state = "modified"
        assert guardrail_agent.agent.state == "modified"
