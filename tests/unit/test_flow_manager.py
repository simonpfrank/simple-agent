"""Tests for FlowManager that loads and manages orchestrator flows."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from simple_agent.orchestration.flow_manager import FlowManager


class TestFlowManager:
    """FlowManager loads flows from YAML and creates orchestrators."""

    @pytest.fixture
    def temp_flows_dir(self):
        """Create temporary flows directory with sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flows_dir = Path(tmpdir)

            # Create example_flow.yaml
            flow_content = {
                "name": "example_flow",
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
                    "role": "Coordinate research and writing",
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o-mini"
                    }
                }
            }

            flow_file = flows_dir / "example_flow.yaml"
            with open(flow_file, "w") as f:
                yaml.dump(flow_content, f)

            yield flows_dir

    @pytest.fixture
    def mock_agent_manager(self):
        """Create mock AgentManager."""
        manager = MagicMock()
        manager.create_agent = MagicMock(return_value=MagicMock())
        return manager

    def test_flow_manager_creation(self, mock_agent_manager):
        """FlowManager can be created."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir="config/flows")

        assert manager.agent_manager == mock_agent_manager
        assert manager.flows_dir == "config/flows"
        assert manager.flows == {}

    def test_load_flow_from_yaml(self, mock_agent_manager, temp_flows_dir):
        """FlowManager can load flow from YAML file."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))

        flow = manager.load_flow("example_flow")

        assert flow is not None
        assert flow["name"] == "example_flow"
        assert "orchestrator" in flow
        assert "sub_agents" in flow

    def test_load_flow_caches_result(self, mock_agent_manager, temp_flows_dir):
        """FlowManager caches loaded flows."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))

        flow1 = manager.load_flow("example_flow")
        flow2 = manager.load_flow("example_flow")

        # Should be same object (cached)
        assert flow1 is flow2

    def test_load_nonexistent_flow_raises(self, mock_agent_manager):
        """FlowManager raises for nonexistent flow."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir="/nonexistent")

        with pytest.raises(FileNotFoundError):
            manager.load_flow("nonexistent_flow")

    def test_validate_flow_valid(self, mock_agent_manager, temp_flows_dir):
        """FlowManager validates flow correctly."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))
        flow = manager.load_flow("example_flow")

        is_valid, errors = manager.validate_flow(flow)

        assert is_valid is True
        assert len(errors) == 0

    def test_list_flows(self, mock_agent_manager, temp_flows_dir):
        """FlowManager can list available flows."""
        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))

        flows = manager.list_flows()

        assert isinstance(flows, list)
        assert "example_flow" in flows

    def test_list_flows_empty_dir(self, mock_agent_manager):
        """FlowManager returns empty list for empty flows directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=tmpdir)

            flows = manager.list_flows()

            assert flows == []

    def test_create_orchestrator_from_flow(self, mock_agent_manager, temp_flows_dir):
        """FlowManager can create orchestrator from flow."""
        # Mock agent manager to return mock agents
        mock_agent = MagicMock()
        mock_agent.name = "researcher"
        mock_agent_manager.get_agent = MagicMock(return_value=mock_agent)

        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))
        flow = manager.load_flow("example_flow")

        orchestrator = manager.create_orchestrator(flow)

        assert orchestrator is not None
        assert orchestrator.name == "coordinator"

    def test_create_orchestrator_resolves_sub_agents(self, mock_agent_manager, temp_flows_dir):
        """FlowManager resolves sub-agents when creating orchestrator."""
        # Mock agent manager
        mock_agent = MagicMock()
        mock_agent.name = "researcher"
        mock_agent_manager.load_agent_from_yaml = MagicMock(return_value=mock_agent)

        manager = FlowManager(agent_manager=mock_agent_manager, flows_dir=str(temp_flows_dir))
        flow = manager.load_flow("example_flow")

        orchestrator = manager.create_orchestrator(flow)

        # Verify agent manager was called to load agents
        assert mock_agent_manager.load_agent_from_yaml.called
