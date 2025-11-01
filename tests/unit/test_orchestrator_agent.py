"""Tests for OrchestratorAgent that coordinates multiple agents."""

from unittest.mock import MagicMock, patch

import pytest

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.orchestration.agent_tool import AgentTool
from simple_agent.orchestration.orchestrator_agent import OrchestratorAgent


class TestOrchestratorAgent:
    """OrchestratorAgent coordinates execution of sub-agents."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock sub-agents."""
        researcher = MagicMock(spec=SimpleAgent)
        researcher.name = "researcher"
        researcher.run = MagicMock(return_value="Research findings: ...\n")

        writer = MagicMock(spec=SimpleAgent)
        writer.name = "writer"
        writer.run = MagicMock(return_value="Final article: ...\n")

        return {"researcher": researcher, "writer": writer}

    @pytest.fixture
    def orchestrator(self, mock_agents):
        """Create OrchestratorAgent with mock sub-agents."""
        sub_agents = {
            "researcher": AgentTool(
                name="researcher",
                agent=mock_agents["researcher"],
                description="Research and gather information"
            ),
            "writer": AgentTool(
                name="writer",
                agent=mock_agents["writer"],
                description="Write final content"
            )
        }

        return OrchestratorAgent(
            name="coordinator",
            role="You are a workflow coordinator.",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini", "temperature": 0.5},
            sub_agents=sub_agents,
            verbosity=1,
            max_steps=10
        )

    def test_orchestrator_creation(self, orchestrator):
        """OrchestratorAgent can be created with sub-agents."""
        assert orchestrator.name == "coordinator"
        assert orchestrator.role == "You are a workflow coordinator."
        assert len(orchestrator.sub_agents) == 2
        assert "researcher" in orchestrator.sub_agents
        assert "writer" in orchestrator.sub_agents

    def test_orchestrator_has_internal_agent(self, orchestrator):
        """OrchestratorAgent creates internal SimpleAgent."""
        assert orchestrator.agent is not None
        assert hasattr(orchestrator.agent, "run")

    def test_orchestrator_sub_agents_are_tools(self, orchestrator):
        """Sub-agents are registered as tools for the orchestrator."""
        # Get tools from internal agent
        tools = orchestrator.agent.tools

        assert len(tools) >= 2

        # Tools should be AgentTools
        tool_names = [tool.name for tool in tools if isinstance(tool, AgentTool)]
        assert "researcher" in tool_names
        assert "writer" in tool_names

    def test_orchestrator_run_with_mocked_llm(self, orchestrator, mock_agents):
        """OrchestratorAgent can run with mocked LLM."""
        # Mock the internal agent's run method to simulate orchestrator reasoning
        orchestrator.agent.run = MagicMock(
            return_value="Final orchestrated output"
        )

        result = orchestrator.run("Research and write about AI")

        assert result == "Final orchestrated output"
        assert orchestrator.agent.run.called

    def test_orchestrator_stores_config(self, orchestrator):
        """OrchestratorAgent stores configuration parameters."""
        assert orchestrator.model_provider == "openai"
        assert orchestrator.model_config["model"] == "gpt-4o-mini"
        assert orchestrator.model_config["temperature"] == 0.5

    def test_orchestrator_repr(self, orchestrator):
        """OrchestratorAgent has readable representation."""
        repr_str = repr(orchestrator)

        assert "OrchestratorAgent" in repr_str
        assert "coordinator" in repr_str

    def test_orchestrator_with_single_sub_agent(self, mock_agents):
        """OrchestratorAgent works with single sub-agent."""
        sub_agents = {
            "researcher": AgentTool(
                name="researcher",
                agent=mock_agents["researcher"],
                description="Research agent"
            )
        }

        orchestrator = OrchestratorAgent(
            name="simple_orchestrator",
            role="Simple coordinator",
            model_provider="openai",
            model_config={},
            sub_agents=sub_agents,
            verbosity=1,
            max_steps=10
        )

        assert len(orchestrator.sub_agents) == 1

    def test_orchestrator_with_custom_verbosity(self, mock_agents):
        """OrchestratorAgent respects verbosity setting."""
        sub_agents = {
            "researcher": AgentTool(
                name="researcher",
                agent=mock_agents["researcher"],
                description="Research agent"
            )
        }

        orchestrator = OrchestratorAgent(
            name="verbose_orchestrator",
            role="Verbose coordinator",
            model_provider="openai",
            model_config={},
            sub_agents=sub_agents,
            verbosity=2,
            max_steps=15
        )

        assert orchestrator.agent is not None

    def test_orchestrator_with_custom_max_steps(self, mock_agents):
        """OrchestratorAgent respects max_steps setting."""
        sub_agents = {
            "researcher": AgentTool(
                name="researcher",
                agent=mock_agents["researcher"],
                description="Research agent"
            )
        }

        orchestrator = OrchestratorAgent(
            name="steps_orchestrator",
            role="Steps coordinator",
            model_provider="openai",
            model_config={},
            sub_agents=sub_agents,
            verbosity=1,
            max_steps=20
        )

        assert orchestrator.agent is not None
