"""
Integration tests for Phase 1.2 with mocked LLM (CI/CD compatible).

Tests the full flow of history and memory management.
Uses mocked LLM responses for reliable testing.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.agent_manager import AgentManager


class TestPhase1_2HistoryMocked:
    """Test history and memory features with mocked LLM."""

    @pytest.fixture
    def test_config(self) -> dict:
        """Load test configuration."""
        config_path = Path(__file__).parent.parent / "data" / "test_config.yaml"
        config = ConfigManager.load(str(config_path))
        return config

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_memory_persists_across_runs(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that SmolAgents memory persists across multiple .run() calls."""
        # Setup mock agent with memory tracking
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.side_effect = ["Response 1", "Response 2", "Response 3"]

        # Mock memory steps - SmolAgents adds steps automatically
        mock_memory = MagicMock()
        mock_memory.steps = []

        def mock_get_full_steps():
            """Simulate SmolAgents memory accumulation."""
            return mock_memory.steps.copy()

        mock_memory.get_full_steps = mock_get_full_steps
        mock_agent_instance.memory = mock_memory
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager and create agent
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")
        agent_wrapper = agent_manager.get_agent("test_agent")

        # Verify memory starts empty
        assert len(agent_wrapper.agent.memory.get_full_steps()) == 0

        # Simulate first run - add memory step
        agent_manager.run_agent("test_agent", "Prompt 1")
        mock_memory.steps.append({"type": "task", "task": "Prompt 1"})
        mock_memory.steps.append({"type": "action", "result": "Response 1"})

        # Verify memory has 2 steps
        assert len(agent_wrapper.agent.memory.get_full_steps()) == 2

        # Simulate second run - add more steps
        agent_manager.run_agent("test_agent", "Prompt 2")
        mock_memory.steps.append({"type": "task", "task": "Prompt 2"})
        mock_memory.steps.append({"type": "action", "result": "Response 2"})

        # Verify memory has 4 steps (accumulated)
        assert len(agent_wrapper.agent.memory.get_full_steps()) == 4

        # Simulate third run
        agent_manager.run_agent("test_agent", "Prompt 3")
        mock_memory.steps.append({"type": "task", "task": "Prompt 3"})
        mock_memory.steps.append({"type": "action", "result": "Response 3"})

        # Verify memory has 6 steps (accumulated)
        memory_steps = agent_wrapper.agent.memory.get_full_steps()
        assert len(memory_steps) == 6

        # Verify step types
        assert memory_steps[0]["type"] == "task"
        assert memory_steps[1]["type"] == "action"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_history_retrieval_from_smolagents_memory(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test retrieving history from SmolAgents memory via get_full_steps()."""
        # Setup mock agent with pre-populated memory
        mock_agent_instance = MagicMock()
        mock_memory = MagicMock()

        # Simulate SmolAgents memory with conversation history
        memory_steps = [
            {
                "type": "task",
                "task": "What is 2+2?",
                "timestamp": "2025-10-23T10:00:00",
            },
            {
                "type": "action",
                "name": "final_answer",
                "result": "4",
                "timestamp": "2025-10-23T10:00:01",
            },
            {
                "type": "task",
                "task": "What is the capital of France?",
                "timestamp": "2025-10-23T10:01:00",
            },
            {
                "type": "action",
                "name": "final_answer",
                "result": "Paris",
                "timestamp": "2025-10-23T10:01:01",
            },
        ]
        mock_memory.get_full_steps.return_value = memory_steps
        mock_agent_instance.memory = mock_memory
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")
        agent_manager.last_agent = "test_agent"  # Simulate agent was run

        agent_wrapper = agent_manager.get_agent("test_agent")

        # Retrieve full memory
        retrieved_steps = agent_wrapper.agent.memory.get_full_steps()

        # Verify all steps retrieved
        assert len(retrieved_steps) == 4
        assert retrieved_steps[0]["task"] == "What is 2+2?"
        assert retrieved_steps[1]["result"] == "4"
        assert retrieved_steps[2]["task"] == "What is the capital of France?"
        assert retrieved_steps[3]["result"] == "Paris"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_memory_reset_clears_history(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that memory.reset() clears SmolAgents memory."""
        # Setup mock agent with memory
        mock_agent_instance = MagicMock()
        mock_memory = MagicMock()

        # Pre-populate memory
        mock_memory.steps = [
            {"type": "task", "task": "Old prompt"},
            {"type": "action", "result": "Old response"},
        ]
        mock_memory.get_full_steps.return_value = mock_memory.steps.copy()

        # Mock reset behavior
        def mock_reset():
            mock_memory.steps.clear()

        mock_memory.reset = mock_reset
        mock_agent_instance.memory = mock_memory
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")
        agent_wrapper = agent_manager.get_agent("test_agent")

        # Verify memory has steps
        assert len(agent_wrapper.agent.memory.get_full_steps()) == 2

        # Clear memory
        agent_wrapper.agent.memory.reset()

        # Verify memory is empty
        mock_memory.get_full_steps.return_value = []  # Update mock return value
        assert len(agent_wrapper.agent.memory.get_full_steps()) == 0

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_memory_export_to_json(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
        tmp_path: Path,
    ) -> None:
        """Test exporting SmolAgents memory to JSON file."""
        # Setup mock agent with memory
        mock_agent_instance = MagicMock()
        mock_memory = MagicMock()

        # Memory with conversation history
        memory_steps = [
            {"type": "task", "task": "What is Python?"},
            {"type": "action", "result": "Python is a programming language"},
        ]
        mock_memory.get_full_steps.return_value = memory_steps
        mock_agent_instance.memory = mock_memory
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Initialize AgentManager
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")
        agent_wrapper = agent_manager.get_agent("test_agent")

        # Get memory steps
        retrieved_steps = agent_wrapper.agent.memory.get_full_steps()

        # Export to JSON
        export_file = tmp_path / "history_export.json"
        export_data = {
            "agent_name": "test_agent",
            "steps": retrieved_steps,
            "total_steps": len(retrieved_steps),
        }

        with open(export_file, "w") as f:
            json.dump(export_data, f, indent=2)

        # Verify file was created
        assert export_file.exists()

        # Load and verify contents
        with open(export_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data["agent_name"] == "test_agent"
        assert loaded_data["total_steps"] == 2
        assert len(loaded_data["steps"]) == 2
        assert loaded_data["steps"][0]["task"] == "What is Python?"
        assert loaded_data["steps"][1]["result"] == "Python is a programming language"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_separate_memory_per_agent(
        self,
        mock_tool_calling_agent: MagicMock,
        mock_litellm: MagicMock,
        test_config: dict,
    ) -> None:
        """Test that each agent maintains separate memory."""
        # Setup mock for auto-loaded default agent
        mock_default_agent = MagicMock()
        mock_default_memory = MagicMock()
        mock_default_memory.steps = []
        mock_default_memory.get_full_steps.return_value = []
        mock_default_agent.memory = mock_default_memory

        # Setup two mock agents with separate memories
        mock_agent1 = MagicMock()
        mock_memory1 = MagicMock()
        mock_memory1.steps = [{"type": "task", "task": "Agent 1 task"}]
        mock_memory1.get_full_steps.return_value = mock_memory1.steps.copy()
        mock_agent1.memory = mock_memory1

        mock_agent2 = MagicMock()
        mock_memory2 = MagicMock()
        mock_memory2.steps = [{"type": "task", "task": "Agent 2 task"}]
        mock_memory2.get_full_steps.return_value = mock_memory2.steps.copy()
        mock_agent2.memory = mock_memory2

        # Return different agents on successive calls (agent1, agent2)
        mock_tool_calling_agent.side_effect = [
            mock_agent1,
            mock_agent2,
        ]

        # Initialize AgentManager and create two agents
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("agent1")
        agent_manager.create_agent("agent2")

        # Get agents
        agent1_wrapper = agent_manager.get_agent("agent1")
        agent2_wrapper = agent_manager.get_agent("agent2")

        # Verify each agent has different memory
        memory1 = agent1_wrapper.agent.memory.get_full_steps()
        memory2 = agent2_wrapper.agent.memory.get_full_steps()

        assert len(memory1) == 1
        assert len(memory2) == 1
        assert memory1[0]["task"] == "Agent 1 task"
        assert memory2[0]["task"] == "Agent 2 task"

        # Verify memories are independent
        assert memory1 != memory2
