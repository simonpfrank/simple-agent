"""FlowValidator validates YAML flow definitions."""

from typing import Any, Dict, List, Tuple


class FlowValidator:
    """Validates orchestrator flow definitions.

    Checks that flow YAML files have required fields and proper structure
    before they are used to create orchestrators.
    """

    REQUIRED_FIELDS = {"name", "orchestrator"}

    def validate(self, flow: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a flow definition.

        Args:
            flow: Flow dictionary to validate

        Returns:
            Tuple of (is_valid: bool, errors: list[str])
        """
        errors: List[str] = []

        # Check required fields
        if "name" not in flow:
            errors.append("Flow must have 'name' field")
        if "orchestrator" not in flow:
            errors.append("Flow must have 'orchestrator' section")

        # Validate orchestrator section
        if "orchestrator" in flow:
            orch = flow["orchestrator"]
            if not isinstance(orch, dict):
                errors.append("'orchestrator' must be a dictionary")
            else:
                if "name" not in orch:
                    errors.append("Orchestrator must have 'name' field")
                if "role" not in orch:
                    errors.append("Orchestrator must have 'role' field")

        # Validate sub_agents section (optional, but if present must be valid)
        if "sub_agents" in flow:
            sub_agents = flow["sub_agents"]
            if not isinstance(sub_agents, list):
                errors.append("'sub_agents' must be a list")
            else:
                for idx, agent in enumerate(sub_agents):
                    if not isinstance(agent, dict):
                        errors.append(f"Sub-agent {idx} must be a dictionary")
                    else:
                        if "name" not in agent:
                            errors.append(f"Sub-agent {idx} must have 'name' field")
                        if "description" not in agent:
                            errors.append(f"Sub-agent {idx} must have 'description' field")
                        if "config" not in agent:
                            errors.append(f"Sub-agent {idx} must have 'config' field")

        return len(errors) == 0, errors
