"""Integration tests for Phase 2.1 Guardrails - TDD approach."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from simple_agent.commands.guardrail_commands import GuardrailCommands
from simple_agent.guardrails import GuardrailAgent, GuardrailViolation, PIIDetector
from simple_agent.guardrails.custom_rule import CustomRuleGuardrail
from simple_agent.guardrails.yaml_loader import load_guardrails_from_yaml


class TestPhase21Integration:
    """Integration tests for Phase 2.1 Guardrails."""

    def test_pii_detector_detects_and_redacts_email(self):
        """Test real PII detection with email."""
        detector = PIIDetector(types=["email"], redact=True)
        text = "Please contact john@example.com for details"

        result = detector.process(text)

        assert "john@example.com" not in result
        assert "[EMAIL]" in result
        assert "Please contact" in result
        assert "for details" in result

    def test_pii_detector_rejects_on_phone(self):
        """Test PII detector rejection on phone number."""
        detector = PIIDetector(types=["phone"], redact=False)
        text = "Call me at 555-123-4567"

        with pytest.raises(GuardrailViolation) as exc_info:
            detector.process(text)

        assert "pii_detector" in str(exc_info.value)

    def test_custom_rule_with_complex_validation(self):
        """Test custom rule with complex validation logic."""

        def check_length_and_format(text: str) -> str:
            """Validate text length and format."""
            if len(text) > 100:
                raise GuardrailViolation("Text exceeds 100 characters", guardrail_type="length_check")
            if not text.strip():
                raise GuardrailViolation("Text cannot be empty", guardrail_type="length_check")
            return text

        guardrail = CustomRuleGuardrail(check_length_and_format)

        # Should pass
        result = guardrail.process("Valid text")
        assert result == "Valid text"

        # Should fail
        with pytest.raises(GuardrailViolation):
            guardrail.process("")

        with pytest.raises(GuardrailViolation):
            guardrail.process("a" * 101)

    def test_guardrail_agent_with_pii_detector(self):
        """Test GuardrailAgent with PIIDetector in real workflow."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.run = Mock(return_value="Response processed")

        # Create guardrail agent with PII detector
        pii_detector = PIIDetector(types=["email"], redact=True)
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[pii_detector])

        # Run with PII in input
        result = guardrail_agent.run("Email me at test@example.com")

        # Agent should have received redacted input
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args[0][0]
        assert "test@example.com" not in call_args
        assert "[EMAIL]" in call_args
        assert result == "Response processed"

    def test_guardrail_agent_rejects_on_violation(self):
        """Test GuardrailAgent rejects input on guardrail violation."""
        mock_agent = Mock()

        # Rejecting PII detector
        pii_detector = PIIDetector(types=["ssn"], redact=False)
        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[pii_detector])

        # Should reject
        with pytest.raises(GuardrailViolation):
            guardrail_agent.run("My SSN is 123-45-6789")

        # Agent should not be called
        mock_agent.run.assert_not_called()

    def test_guardrail_agent_with_multiple_guardrails(self):
        """Test GuardrailAgent with multiple guardrails in sequence."""
        mock_agent = Mock()
        mock_agent.run = Mock(return_value="Done")

        # First guardrail: redact emails
        email_detector = PIIDetector(types=["email"], redact=True)

        # Second guardrail: custom rule to uppercase
        uppercase_rule = CustomRuleGuardrail(lambda text: text.upper())

        guardrail_agent = GuardrailAgent(
            mock_agent, input_guardrails=[email_detector, uppercase_rule]
        )

        result = guardrail_agent.run("contact john@example.com now")

        # Both guardrails should be applied
        call_args = mock_agent.run.call_args[0][0]
        assert "[EMAIL]" in call_args  # Email redacted
        assert call_args.isupper()  # Uppercased

    def test_yaml_guardrail_configuration_loading(self):
        """Test loading guardrail configuration from YAML file."""
        yaml_content = """
name: "safe_assistant"
role: "You are a safe assistant"
guardrails:
  input:
    - type: "pii_detector"
      redact: true
      types:
        - "email"
        - "phone"
    - type: "custom"
      function: "validators.check_length"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            config = load_guardrails_from_yaml(f.name)

            assert "guardrails" in config
            assert "input" in config["guardrails"]
            assert len(config["guardrails"]["input"]) == 2
            assert config["guardrails"]["input"][0]["type"] == "pii_detector"
            assert config["guardrails"]["input"][1]["type"] == "custom"

            # Clean up
            Path(f.name).unlink()

    def test_guardrail_commands_integration(self):
        """Test GuardrailCommands with real guardrails."""
        mock_agent_manager = Mock()
        commands = GuardrailCommands(mock_agent_manager)

        # Test guardrail
        detector = PIIDetector(types=["email"], redact=True)
        result = commands.test_guardrail(detector, "My email is test@example.com")

        assert "[EMAIL]" in result
        assert "test@example.com" not in result

    def test_pii_detector_with_all_types(self):
        """Test PII detection with all supported types."""
        detector = PIIDetector(types=["email", "phone", "ssn"], redact=True)

        text = (
            "Contact john@example.com or call 555-123-4567. "
            "SSN: 123-45-6789 must be protected."
        )

        result = detector.process(text)

        # All PII should be redacted
        assert "john@example.com" not in result
        assert "555-123-4567" not in result
        assert "123-45-6789" not in result

        # Redaction tokens should be present
        assert "[EMAIL]" in result
        assert "[PHONE]" in result
        assert "[SSN]" in result

        # Rest of text should be intact
        assert "Contact" in result
        assert "or call" in result
        assert "must be protected" in result

    def test_custom_rule_chaining(self):
        """Test multiple custom rules applied in sequence."""

        def remove_profanity(text: str) -> str:
            """Simple profanity removal."""
            return text.replace("bad", "good")

        def uppercase(text: str) -> str:
            """Convert to uppercase."""
            return text.upper()

        rule1 = CustomRuleGuardrail(remove_profanity)
        rule2 = CustomRuleGuardrail(uppercase)

        mock_agent = Mock()
        mock_agent.run = Mock(return_value="OK")

        guardrail_agent = GuardrailAgent(mock_agent, input_guardrails=[rule1, rule2])

        guardrail_agent.run("this is bad")

        call_args = mock_agent.run.call_args[0][0]
        assert call_args == "THIS IS GOOD"  # Profanity removed, then uppercased

    def test_pii_detector_preserves_text_structure(self):
        """Test that PII redaction preserves text structure."""
        detector = PIIDetector(types=["email"], redact=True)

        text = "Email: john@example.com\nPhone: 555-1234\nAddress: 123 Main St"

        result = detector.process(text)

        # Structure should be preserved
        assert "Email:" in result
        assert "Phone:" in result
        assert "Address:" in result
        assert "123 Main St" in result
        assert "[EMAIL]" in result

    def test_guardrail_violation_contains_info(self):
        """Test GuardrailViolation contains meaningful error info."""

        def strict_rule(text: str) -> str:
            if len(text) < 5:
                raise GuardrailViolation("Input too short", guardrail_type="strict_check")
            return text

        guardrail = CustomRuleGuardrail(strict_rule)

        with pytest.raises(GuardrailViolation) as exc_info:
            guardrail.process("hi")

        error = exc_info.value
        assert error.guardrail_type == "strict_check"
        assert "Input too short" in error.message
        assert "strict_check" in str(error)
