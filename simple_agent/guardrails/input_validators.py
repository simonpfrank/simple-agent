"""Input validators for guardrails."""

import re
from typing import List, Literal, Optional

from simple_agent.guardrails.exceptions import GuardrailViolation

PIIType = Literal["email", "phone", "ssn"]


class PIIDetector:
    """Detect and redact Personally Identifiable Information in text."""

    # Regex patterns for different PII types
    PATTERNS = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "phone": r"\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})",
        "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
    }

    REDACTION_TOKENS = {
        "email": "[EMAIL]",
        "phone": "[PHONE]",
        "ssn": "[SSN]",
    }

    def __init__(self, types: Optional[List[PIIType]] = None, redact: bool = True):
        """Initialize PIIDetector.

        Args:
            types: List of PII types to detect (email, phone, ssn)
            redact: If True, redact PII; if False, reject input with GuardrailViolation
        """
        self.types = types or ["email", "phone", "ssn"]
        self.redact = redact

    def process(self, text: str) -> str:
        """Process text to detect and handle PII.

        Args:
            text: Input text to process

        Returns:
            Redacted text if redact=True

        Raises:
            GuardrailViolation: If PII found and redact=False
        """
        if not text:
            return text

        result = text
        found_pii = False

        for pii_type in self.types:
            if pii_type not in self.PATTERNS:
                continue

            pattern = self.PATTERNS[pii_type]
            matches = list(re.finditer(pattern, text))

            if matches:
                found_pii = True
                if self.redact:
                    # Redact by replacing with token
                    token = self.REDACTION_TOKENS[pii_type]
                    result = re.sub(pattern, token, result)
                else:
                    # Reject
                    pii_found = matches[0].group(0)
                    raise GuardrailViolation(
                        f"Found {pii_type}: {pii_found}", guardrail_type="pii_detector"
                    )

        return result
