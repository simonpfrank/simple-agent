"""Tests for REPL flow commands."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from simple_agent.commands.flow_commands import FlowCommands
from simple_agent.orchestration.flow_manager import FlowManager


class TestFlowCommands:
    """FlowCommands provides REPL interface for flow management."""

    @pytest.fixture
    def temp_flows_dir(self):
        """Create temporary flows directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flows_dir = Path(tmpdir)

            # Create example flow
            flow_content = {
                "name": "example",
                "description": "Example workflow",
                "sub_agents": [
                    {
                        "name": "researcher",
                        "description": "Research agent",
                        "config": "config/agents/researcher.yaml"
                    }
                ],
                "orchestrator": {
                    "name": "coordinator",
                    "role": "Coordinate workflow",
                    "model": {"provider": "openai"}
                }
            }

            flow_file = flows_dir / "example.yaml"
            with open(flow_file, "w") as f:
                yaml.dump(flow_content, f)

            yield flows_dir

    @pytest.fixture
    def mock_agent_manager(self):
        """Create mock AgentManager."""
        manager = MagicMock()
        agent = MagicMock()
        agent.name = "researcher"
        manager.load_agent_from_yaml = MagicMock(return_value=agent)
        return manager

    @pytest.fixture
    def flow_commands(self, mock_agent_manager, temp_flows_dir):
        """Create FlowCommands instance."""
        flow_manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )
        return FlowCommands(flow_manager=flow_manager)

    def test_flow_commands_creation(self, flow_commands):
        """FlowCommands can be created."""
        assert flow_commands.flow_manager is not None

    def test_list_flows_command(self, flow_commands):
        """list_flows command returns available flows."""
        result = flow_commands.list_flows()

        # Should return a list or table output
        assert result is not None

    def test_show_flow_command(self, flow_commands):
        """show_flow command displays flow details."""
        result = flow_commands.show_flow("example")

        # Should return formatted output about the flow
        assert result is not None

    def test_show_nonexistent_flow_raises(self, flow_commands):
        """show_flow raises for nonexistent flow."""
        with pytest.raises(FileNotFoundError):
            flow_commands.show_flow("nonexistent")

    def test_run_flow_command_with_mocked_agent(self, flow_commands):
        """run_flow command can execute orchestrator."""
        # Mock orchestrator run without patching imports
        orchestrator = MagicMock()
        orchestrator.run = MagicMock(return_value="Final output")
        flow_commands.flow_manager.create_orchestrator = MagicMock(return_value=orchestrator)

        result = flow_commands.run_flow("example", "test input")

        # Verify orchestrator was executed
        assert orchestrator.run.called
        assert "Final output" in result or "Result" in result

    def test_delete_flow_command_validation(self, flow_commands):
        """delete_flow validates flow exists before deleting."""
        # Test that we handle nonexistent flows gracefully
        with pytest.raises(FileNotFoundError):
            flow_commands.delete_flow("nonexistent")

    def test_help_text_available(self, flow_commands):
        """FlowCommands has help text."""
        # Verify commands have docstrings
        assert flow_commands.list_flows.__doc__ is not None
        assert flow_commands.show_flow.__doc__ is not None
        assert flow_commands.run_flow.__doc__ is not None
