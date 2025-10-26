"""Guardrail exceptions."""


class GuardrailViolation(Exception):
    """Raised when a guardrail is violated."""

    def __init__(self, message: str, guardrail_type: str = "unknown"):
        """Initialize GuardrailViolation.

        Args:
            message: Description of the violation
            guardrail_type: Type of guardrail that was violated
        """
        self.message = message
        self.guardrail_type = guardrail_type
        super().__init__(f"[{guardrail_type}] {message}")
