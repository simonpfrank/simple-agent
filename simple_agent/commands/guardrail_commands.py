"""REPL commands for guardrail management."""

from typing import Any, List, Optional

from simple_agent.guardrails.custom_rule import CustomRuleGuardrail
from simple_agent.guardrails.exceptions import GuardrailViolation
from simple_agent.guardrails.input_validators import PIIDetector


class GuardrailCommands:
    """Commands for managing guardrails in REPL."""

    def __init__(self, agent_manager: Any):
        """Initialize GuardrailCommands.

        Args:
            agent_manager: AgentManager instance for agent operations
        """
        self.agent_manager = agent_manager

    def test_guardrail(self, guardrail: Any, text: str) -> str:
        """Test a guardrail on sample text.

        Args:
            guardrail: Guardrail instance to test (PIIDetector, CustomRuleGuardrail)
            text: Sample text to test

        Returns:
            Processed text if guardrail passes

        Raises:
            GuardrailViolation: If guardrail rejects the text
        """
        return guardrail.process(text)

    def list_guardrails(self, agent_name: str) -> Optional[List[str]]:
        """List guardrails for an agent.

        Args:
            agent_name: Name of agent

        Returns:
            List of guardrail descriptions or None if agent not found
        """
        agent = self.agent_manager.get_agent(agent_name)
        if not agent:
            return None

        guardrails = getattr(agent, "guardrails", [])
        result = []
        for i, guardrail in enumerate(guardrails):
            guardrail_type = type(guardrail).__name__
            if isinstance(guardrail, PIIDetector):
                desc = f"{i}: {guardrail_type} (types: {', '.join(guardrail.types)}, redact: {guardrail.redact})"
            elif isinstance(guardrail, CustomRuleGuardrail):
                desc = f"{i}: {guardrail_type} (function: {guardrail.name})"
            else:
                desc = f"{i}: {guardrail_type}"
            result.append(desc)

        return result

    def add_guardrail(
        self,
        agent_name: str,
        guardrail_type: str,
        redact: bool = True,
        pii_types: List[str] = None,
        function: str = None,
    ) -> bool:
        """Add guardrail to agent.

        Args:
            agent_name: Name of agent
            guardrail_type: Type of guardrail ("pii_detector" or "custom")
            redact: For PII detector, whether to redact (True) or reject (False)
            pii_types: For PII detector, types to detect (email, phone, ssn)
            function: For custom rule, module.function reference

        Returns:
            True if guardrail added successfully
        """
        agent = self.agent_manager.get_agent(agent_name)
        if not agent:
            return False

        if not hasattr(agent, "guardrails"):
            agent.guardrails = []

        guardrail = None
        if guardrail_type == "pii_detector":
            guardrail = PIIDetector(types=pii_types or ["email", "phone", "ssn"], redact=redact)
        elif guardrail_type == "custom":
            # Note: In real implementation, would need to import the function
            # For now, just create placeholder
            if function:
                guardrail = CustomRuleGuardrail(lambda text: text)  # Placeholder

        if guardrail:
            agent.guardrails.append(guardrail)
            return True

        return False

    def remove_guardrail(self, agent_name: str, index: int) -> bool:
        """Remove guardrail from agent.

        Args:
            agent_name: Name of agent
            index: Index of guardrail to remove

        Returns:
            True if guardrail removed successfully
        """
        agent = self.agent_manager.get_agent(agent_name)
        if not agent:
            return False

        guardrails = getattr(agent, "guardrails", [])
        if 0 <= index < len(guardrails):
            guardrails.pop(index)
            return True

        return False
