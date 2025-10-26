"""Unit tests for guardrail classes - TDD approach."""

import pytest

from simple_agent.guardrails.input_validators import PIIDetector
from simple_agent.guardrails.exceptions import GuardrailViolation


class TestPIIDetector:
    """Test PIIDetector class."""

    def test_detect_email_redact(self):
        """Test email detection with redaction."""
        detector = PIIDetector(types=["email"], redact=True)
        text = "Contact me at john@example.com for details."
        result = detector.process(text)
        assert "john@example.com" not in result
        assert "[EMAIL]" in result

    def test_detect_phone_redact(self):
        """Test phone number detection with redaction."""
        detector = PIIDetector(types=["phone"], redact=True)
        text = "Call me at +1-555-123-4567 anytime."
        result = detector.process(text)
        assert "555-123-4567" not in result
        assert "[PHONE]" in result

    def test_detect_ssn_redact(self):
        """Test SSN detection with redaction."""
        detector = PIIDetector(types=["ssn"], redact=True)
        text = "My SSN is 123-45-6789 please secure it."
        result = detector.process(text)
        assert "123-45-6789" not in result
        assert "[SSN]" in result

    def test_no_pii_found(self):
        """Test text with no PII returns unchanged."""
        detector = PIIDetector(types=["email", "phone"], redact=True)
        text = "This is a normal message with no sensitive data."
        result = detector.process(text)
        assert result == text

    def test_reject_on_pii_found(self):
        """Test reject mode raises GuardrailViolation."""
        detector = PIIDetector(types=["email"], redact=False)
        text = "My email is test@example.com"
        with pytest.raises(GuardrailViolation):
            detector.process(text)

    def test_multiple_pii_types(self):
        """Test detection of multiple PII types."""
        detector = PIIDetector(types=["email", "phone", "ssn"], redact=True)
        text = "Email: john@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        result = detector.process(text)
        assert "john@example.com" not in result
        assert "555-123-4567" not in result
        assert "123-45-6789" not in result
        assert result.count("[EMAIL]") == 1
        assert result.count("[PHONE]") == 1
        assert result.count("[SSN]") == 1

    def test_multiple_instances_of_same_pii(self):
        """Test multiple instances of same PII type are all redacted."""
        detector = PIIDetector(types=["email"], redact=True)
        text = "Contact john@example.com or jane@example.com"
        result = detector.process(text)
        assert "john@example.com" not in result
        assert "jane@example.com" not in result
        assert result.count("[EMAIL]") == 2

    def test_empty_text(self):
        """Test empty text returns empty."""
        detector = PIIDetector(types=["email"], redact=True)
        result = detector.process("")
        assert result == ""

    def test_phone_variations(self):
        """Test different phone number formats."""
        detector = PIIDetector(types=["phone"], redact=True)

        # Test with country code
        text1 = "+1-555-123-4567"
        result1 = detector.process(text1)
        assert "[PHONE]" in result1

        # Test without dashes
        text2 = "5551234567"
        result2 = detector.process(text2)
        assert "[PHONE]" in result2

        # Test with parentheses
        text3 = "(555) 123-4567"
        result3 = detector.process(text3)
        assert "[PHONE]" in result3

    def test_email_variations(self):
        """Test different email formats."""
        detector = PIIDetector(types=["email"], redact=True)

        # Test with subdomain
        text1 = "user@mail.example.co.uk"
        result1 = detector.process(text1)
        assert "[EMAIL]" in result1

        # Test with plus addressing
        text2 = "user+tag@example.com"
        result2 = detector.process(text2)
        assert "[EMAIL]" in result2
