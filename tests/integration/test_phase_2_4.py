"""Integration tests for Phase 2.4: Multi-Agent Orchestration."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.orchestration.agent_tool import AgentTool
from simple_agent.orchestration.orchestrator_agent import OrchestratorAgent
from simple_agent.orchestration.flow_manager import FlowManager
from simple_agent.commands.flow_commands import FlowCommands


class TestMultiAgentOrchestration:
    """End-to-end multi-agent orchestration workflows."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock sub-agents."""
        researcher = MagicMock(spec=SimpleAgent)
        researcher.name = "researcher"
        researcher.run = MagicMock(return_value="Research findings on quantum computing")

        writer = MagicMock(spec=SimpleAgent)
        writer.name = "writer"
        writer.run = MagicMock(return_value="A comprehensive article on quantum computing")

        return {"researcher": researcher, "writer": writer}

    @pytest.fixture
    def temp_flows_dir(self):
        """Create temporary flows directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            flows_dir = Path(tmpdir)

            flow_content = {
                "name": "test_workflow",
                "description": "Test multi-agent workflow",
                "sub_agents": [
                    {
                        "name": "researcher",
                        "description": "Research agent",
                        "config": "config/agents/researcher.yaml"
                    },
                    {
                        "name": "writer",
                        "description": "Writing agent",
                        "config": "config/agents/writer.yaml"
                    }
                ],
                "orchestrator": {
                    "name": "coordinator",
                    "role": "Coordinate research and writing",
                    "model": {"provider": "openai"}
                }
            }

            flow_file = flows_dir / "test_workflow.yaml"
            with open(flow_file, "w") as f:
                yaml.dump(flow_content, f)

            yield flows_dir

    def test_agent_tool_wraps_agent(self, mock_agents):
        """AgentTool successfully wraps an agent."""
        researcher = mock_agents["researcher"]

        tool = AgentTool(
            name="researcher",
            agent=researcher,
            description="Conducts research"
        )

        # Execute the tool
        output = tool.forward("Research quantum computing")

        # Verify agent was called
        assert researcher.run.called
        assert output == "Research findings on quantum computing"

        # Verify execution was tracked
        assert len(tool.call_history) == 1

    def test_orchestrator_with_agent_tools(self, mock_agents):
        """OrchestratorAgent successfully uses agent tools."""
        # Create agent tools
        sub_agents = {
            "researcher": AgentTool(
                name="researcher",
                agent=mock_agents["researcher"],
                description="Conducts research"
            ),
            "writer": AgentTool(
                name="writer",
                agent=mock_agents["writer"],
                description="Writes content"
            )
        }

        # Create orchestrator
        orchestrator = OrchestratorAgent(
            name="coordinator",
            role="Coordinate research and writing",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            sub_agents=sub_agents,
            verbosity=1,
            max_steps=10
        )

        # Verify sub-agents are tools
        assert len(orchestrator.agent.tools) >= 2

    def test_flow_manager_loads_flow(self, temp_flows_dir):
        """FlowManager successfully loads flow from YAML."""
        mock_agent_manager = MagicMock()
        mock_agent = MagicMock()
        mock_agent.name = "researcher"
        mock_agent_manager.load_agent_from_yaml = MagicMock(return_value=mock_agent)

        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        # Load flow
        flow = manager.load_flow("test_workflow")

        assert flow["name"] == "test_workflow"
        assert "orchestrator" in flow
        assert len(flow["sub_agents"]) == 2

    def test_flow_manager_validates_flow(self, temp_flows_dir):
        """FlowManager validates flow definitions."""
        mock_agent_manager = MagicMock()
        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        flow = manager.load_flow("test_workflow")
        is_valid, errors = manager.validate_flow(flow)

        assert is_valid is True
        assert len(errors) == 0

    def test_flow_manager_creates_orchestrator(self, temp_flows_dir):
        """FlowManager creates orchestrator from flow."""
        mock_agent_manager = MagicMock()
        mock_agent = MagicMock()
        mock_agent.name = "researcher"
        mock_agent_manager.load_agent_from_yaml = MagicMock(return_value=mock_agent)

        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        flow = manager.load_flow("test_workflow")
        orchestrator = manager.create_orchestrator(flow)

        assert orchestrator.name == "coordinator"
        assert len(orchestrator.sub_agents) == 2

    def test_flow_commands_list_flows(self, temp_flows_dir):
        """FlowCommands can list available flows."""
        mock_agent_manager = MagicMock()
        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        commands = FlowCommands(flow_manager=manager)
        output = commands.list_flows()

        assert output is not None
        assert "test_workflow" in output

    def test_flow_commands_show_flow(self, temp_flows_dir):
        """FlowCommands can display flow definition."""
        mock_agent_manager = MagicMock()
        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        commands = FlowCommands(flow_manager=manager)
        output = commands.show_flow("test_workflow")

        assert output is not None
        assert "test_workflow" in output
        assert "orchestrator" in output

    def test_orchestrator_handles_agent_failure(self):
        """Orchestrator handles agent failures gracefully."""
        # Create a failing agent
        failing_agent = MagicMock()
        failing_agent.name = "failing_agent"
        failing_agent.run = MagicMock(side_effect=RuntimeError("Agent error"))

        # Wrap as tool
        tool = AgentTool(
            name="failing",
            agent=failing_agent,
            description="Failing agent"
        )

        # Tool should handle failure
        output = tool.forward("Test")

        assert "Error" in output
        assert len(tool.call_history) == 1
        assert tool.call_history[0]["status"] == "failure"

    def test_integration_full_workflow(self, temp_flows_dir, mock_agents):
        """Full workflow from flow YAML to orchestrator execution."""
        # Create mock agent manager that returns our mock agents
        mock_agent_manager = MagicMock()

        def load_agent_side_effect(config_path):
            if "researcher" in config_path:
                return mock_agents["researcher"]
            elif "writer" in config_path:
                return mock_agents["writer"]
            raise ValueError(f"Unknown agent config: {config_path}")

        mock_agent_manager.load_agent_from_yaml = MagicMock(
            side_effect=load_agent_side_effect
        )

        # Create flow manager
        manager = FlowManager(
            agent_manager=mock_agent_manager,
            flows_dir=str(temp_flows_dir)
        )

        # Load and validate flow
        flow = manager.load_flow("test_workflow")
        is_valid, errors = manager.validate_flow(flow)
        assert is_valid is True

        # Create orchestrator from flow
        orchestrator = manager.create_orchestrator(flow)
        assert orchestrator is not None

        # Verify sub-agents are properly wrapped
        assert len(orchestrator.sub_agents) == 2
        assert "researcher" in orchestrator.sub_agents
        assert "writer" in orchestrator.sub_agents
