"""Unit tests for CustomRuleGuardrail - TDD approach."""

import pytest

from simple_agent.guardrails.custom_rule import CustomRuleGuardrail
from simple_agent.guardrails.exceptions import GuardrailViolation


class TestCustomRuleGuardrail:
    """Test CustomRuleGuardrail class."""

    def test_simple_validation_pass(self):
        """Test custom rule that passes."""

        def no_sql_injection(text: str) -> str:
            """Reject text containing SQL keywords."""
            if "DROP TABLE" in text.upper():
                raise GuardrailViolation("SQL injection detected", guardrail_type="custom_rule")
            return text

        guardrail = CustomRuleGuardrail(no_sql_injection)
        text = "Please retrieve all user records"
        result = guardrail.process(text)
        assert result == text

    def test_custom_rule_rejection(self):
        """Test custom rule that rejects input."""

        def no_sql_injection(text: str) -> str:
            """Reject text containing SQL keywords."""
            if "DROP TABLE" in text.upper():
                raise GuardrailViolation("SQL injection detected", guardrail_type="custom_rule")
            return text

        guardrail = CustomRuleGuardrail(no_sql_injection)
        text = "DROP TABLE users"
        with pytest.raises(GuardrailViolation):
            guardrail.process(text)

    def test_custom_rule_modification(self):
        """Test custom rule that modifies text."""

        def uppercase_rule(text: str) -> str:
            """Convert text to uppercase."""
            return text.upper()

        guardrail = CustomRuleGuardrail(uppercase_rule)
        text = "hello world"
        result = guardrail.process(text)
        assert result == "HELLO WORLD"

    def test_lambda_rule(self):
        """Test custom rule using lambda."""
        guardrail = CustomRuleGuardrail(lambda text: text.replace("bad", "good"))
        text = "This is bad content"
        result = guardrail.process(text)
        assert result == "This is good content"

    def test_guardrail_with_name(self):
        """Test CustomRuleGuardrail stores function name."""

        def validate_length(text: str) -> str:
            if len(text) > 100:
                raise GuardrailViolation("Text too long", guardrail_type="validate_length")
            return text

        guardrail = CustomRuleGuardrail(validate_length)
        assert guardrail.name == "validate_length"

    def test_guardrail_with_lambda_name(self):
        """Test CustomRuleGuardrail with lambda has generic name."""
        guardrail = CustomRuleGuardrail(lambda text: text)
        assert guardrail.name == "<lambda>"

    def test_empty_text(self):
        """Test custom rule with empty text."""

        def any_rule(text: str) -> str:
            return text

        guardrail = CustomRuleGuardrail(any_rule)
        result = guardrail.process("")
        assert result == ""

    def test_rule_with_complex_logic(self):
        """Test custom rule with complex validation."""

        def complex_rule(text: str) -> str:
            """Check multiple conditions."""
            if len(text) < 5:
                raise GuardrailViolation("Text too short", guardrail_type="complex")
            if "forbidden" in text.lower():
                raise GuardrailViolation("Forbidden word found", guardrail_type="complex")
            if not any(c.isdigit() for c in text):
                raise GuardrailViolation("No digits found", guardrail_type="complex")
            return text

        guardrail = CustomRuleGuardrail(complex_rule)

        # Should pass
        result = guardrail.process("Test123")
        assert result == "Test123"

        # Should fail - too short
        with pytest.raises(GuardrailViolation):
            guardrail.process("hi")

        # Should fail - forbidden word
        with pytest.raises(GuardrailViolation):
            guardrail.process("test forbidden 123")

        # Should fail - no digits
        with pytest.raises(GuardrailViolation):
            guardrail.process("Testword")
