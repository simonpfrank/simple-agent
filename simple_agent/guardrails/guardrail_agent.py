"""GuardrailAgent wrapper for applying guardrails to SimpleAgent."""

from typing import Any, List


class GuardrailAgent:
    """Wrapper around SimpleAgent that applies input guardrails before execution.

    Guardrails are applied in order: each guardrail processes the output of the previous one.
    """

    def __init__(self, agent: Any, input_guardrails: List = None):
        """Initialize GuardrailAgent.

        Args:
            agent: SimpleAgent instance to wrap
            input_guardrails: List of guardrails to apply to input (order matters)
        """
        self.agent = agent
        self.input_guardrails = input_guardrails or []

    def run(self, prompt: str) -> str:
        """Run agent with guardrails applied to input.

        Args:
            prompt: User input prompt

        Returns:
            Agent response

        Raises:
            GuardrailViolation: If input guardrails reject the input
        """
        # Apply input guardrails in order
        processed_prompt = prompt
        for guardrail in self.input_guardrails:
            processed_prompt = guardrail.process(processed_prompt)

        # Run wrapped agent with processed prompt
        response = self.agent.run(processed_prompt)
        return response
