"""Tests for FlowValidator that validates YAML flow definitions."""

import pytest

from simple_agent.orchestration.flow_validator import FlowValidator


class TestFlowValidator:
    """FlowValidator checks flow definitions for correctness."""

    def test_validate_valid_minimal_flow(self):
        """Validator accepts valid minimal flow."""
        flow = {
            "name": "test_flow",
            "description": "Test workflow",
            "sub_agents": [
                {"name": "agent1", "description": "First agent", "config": "path/to/config.yaml"}
            ],
            "orchestrator": {
                "name": "orchestrator",
                "role": "Coordinator",
                "model": {"provider": "openai"}
            }
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_name(self):
        """Validator rejects flow without name."""
        flow = {
            "description": "Test workflow",
            "sub_agents": [],
            "orchestrator": {}
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is False
        assert any("name" in error for error in errors)

    def test_validate_missing_orchestrator(self):
        """Validator rejects flow without orchestrator."""
        flow = {
            "name": "test_flow",
            "description": "Test workflow",
            "sub_agents": []
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is False
        assert any("orchestrator" in error for error in errors)

    def test_validate_invalid_sub_agent(self):
        """Validator rejects sub-agent without required fields."""
        flow = {
            "name": "test_flow",
            "description": "Test workflow",
            "sub_agents": [
                {"name": "agent1"}  # Missing description and config
            ],
            "orchestrator": {"name": "orch", "role": "Coordinator"}
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is False
        # Should have errors about missing sub-agent fields

    def test_validate_multiple_sub_agents(self):
        """Validator accepts flow with multiple sub-agents."""
        flow = {
            "name": "complex_flow",
            "description": "Complex workflow",
            "sub_agents": [
                {"name": "researcher", "description": "Research agent", "config": "config/researcher.yaml"},
                {"name": "writer", "description": "Writing agent", "config": "config/writer.yaml"},
                {"name": "reviewer", "description": "Review agent", "config": "config/reviewer.yaml"}
            ],
            "orchestrator": {
                "name": "coordinator",
                "role": "Orchestrate workflow",
                "model": {"provider": "openai"}
            }
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_orchestrator_missing_name(self):
        """Validator rejects orchestrator without name."""
        flow = {
            "name": "test_flow",
            "sub_agents": [],
            "orchestrator": {
                "role": "Coordinator",
                "model": {"provider": "openai"}
            }
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is False
        # Check that there's an error about orchestrator name
        assert any("name" in error.lower() for error in errors)

    def test_validate_empty_sub_agents_list_ok(self):
        """Validator accepts flow with empty sub_agents list."""
        flow = {
            "name": "simple_flow",
            "sub_agents": [],
            "orchestrator": {
                "name": "orch",
                "role": "Simple coordinator"
            }
        }

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is True

    def test_validate_error_messages_are_strings(self):
        """Validator error messages are readable strings."""
        flow = {"sub_agents": [{"name": "agent"}]}  # Missing multiple required fields

        validator = FlowValidator()
        is_valid, errors = validator.validate(flow)

        assert is_valid is False
        assert all(isinstance(err, str) for err in errors)
        assert all(len(err) > 0 for err in errors)
