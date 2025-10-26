"""Custom rule guardrails for user-defined validation."""

from typing import Callable

from simple_agent.guardrails.exceptions import GuardrailViolation


class CustomRuleGuardrail:
    """Wrapper for user-defined validation rules."""

    def __init__(self, rule_func: Callable[[str], str]):
        """Initialize CustomRuleGuardrail.

        Args:
            rule_func: Function that takes text and returns modified text.
                      Can raise GuardrailViolation to reject.
        """
        self.rule_func = rule_func
        self.name = rule_func.__name__

    def process(self, text: str) -> str:
        """Process text through custom rule.

        Args:
            text: Input text to process

        Returns:
            Processed text

        Raises:
            GuardrailViolation: If rule rejects the input
        """
        return self.rule_func(text)
