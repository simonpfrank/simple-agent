"""
Integration tests for Phase 1.1 with REAL LLM (definitive tests).

Tests the full flow of inspection and chat features with actual LLM.
Requires OPENAI_API_KEY environment variable.
"""

import os
from pathlib import Path

import pytest

from simple_agent.core.config_manager import ConfigManager
from simple_agent.core.agent_manager import AgentManager


# Skip all tests if no API key available
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping live LLM tests",
)


class TestPhase1_1InspectionLive:
    """Test inspection features with REAL LLM."""

    @pytest.fixture
    def test_config(self) -> dict:
        """Load test configuration and override with real API key from environment."""
        # Load .env file first to populate environment variables
        ConfigManager.load_env()

        config_path = Path(__file__).parent.parent / "data" / "test_config.yaml"
        config = ConfigManager.load(str(config_path))

        # Override fake API key with real one from environment
        if "llm" in config and "openai" in config["llm"]:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                config["llm"]["openai"]["api_key"] = api_key

        return config

    def test_prompt_response_tracking_with_real_llm(self, test_config: dict) -> None:
        """
        Test full lifecycle with REAL LLM: create agent - run - track prompt/response.

        This is the definitive test - no mocks.
        """
        # Initialize AgentManager
        agent_manager = AgentManager(test_config)

        # Verify tracking starts as None
        assert agent_manager.last_prompt is None
        assert agent_manager.last_response is None
        assert agent_manager.last_agent is None

        # Create and run agent with REAL LLM
        agent_manager.create_agent("test_agent")
        prompt = "What is 2+2? Answer with just the number."
        response = agent_manager.run_agent("test_agent", prompt)

        # Verify tracking captured the interaction
        assert agent_manager.last_prompt == prompt
        assert agent_manager.last_response is not None
        assert len(agent_manager.last_response) > 0
        assert agent_manager.last_agent == "test_agent"

        # Verify response is reasonable (should contain "4")
        # AgentResult supports string conversion for backward compatibility
        assert "4" in str(response) or "four" in str(response).lower()

    def test_tracking_updates_with_real_llm(self, test_config: dict) -> None:
        """
        Test that tracking updates correctly on subsequent runs with REAL LLM.

        This is the definitive test - no mocks.
        """
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("math_agent")

        # First run
        prompt1 = "What is 1+1? Just the number."
        response1 = agent_manager.run_agent("math_agent", prompt1)
        assert agent_manager.last_prompt == prompt1
        assert agent_manager.last_response == str(
            response1
        )  # AgentResult string conversion
        assert agent_manager.last_agent == "math_agent"
        assert "2" in str(response1) or "two" in str(response1).lower()

        # Second run - tracking should update
        prompt2 = "What is 3+3? Just the number."
        response2 = agent_manager.run_agent("math_agent", prompt2)
        assert agent_manager.last_prompt == prompt2
        assert agent_manager.last_response == str(
            response2
        )  # AgentResult string conversion
        assert agent_manager.last_agent == "math_agent"
        assert "6" in str(response2) or "six" in str(response2).lower()

        # Verify they're different
        assert str(response1) != str(response2)
        assert prompt1 != prompt2

    def test_tracking_across_multiple_agents_with_real_llm(
        self, test_config: dict
    ) -> None:
        """
        Test tracking when switching between agents with REAL LLM.

        This is the definitive test - no mocks.
        """
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("agent1")
        agent_manager.create_agent("agent2")

        # Run with agent1
        prompt1 = "Say 'Hello from agent 1'"
        response1 = agent_manager.run_agent("agent1", prompt1)
        assert agent_manager.last_agent == "agent1"
        assert agent_manager.last_prompt == prompt1
        assert agent_manager.last_response == str(
            response1
        )  # AgentResult string conversion

        # Run with agent2 - tracking should switch
        prompt2 = "Say 'Hello from agent 2'"
        response2 = agent_manager.run_agent("agent2", prompt2)
        assert agent_manager.last_agent == "agent2"
        assert agent_manager.last_prompt == prompt2
        assert agent_manager.last_response == str(
            response2
        )  # AgentResult string conversion

        # Verify responses are different
        assert str(response1) != str(response2)

    def test_auto_loaded_agent_tracking_with_real_llm(self, test_config: dict) -> None:
        """
        Test that tracking works with manually created agents and REAL LLM.

        This is the definitive test - no mocks.
        """
        # AgentManager needs agents to be manually created
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("default")

        # Verify 'default' was created
        assert "default" in agent_manager.list_agents()

        # Run with created agent
        prompt = "What is the capital of France? Just the city name."
        response = agent_manager.run_agent("default", prompt)

        # Verify tracking works
        assert agent_manager.last_agent == "default"
        assert agent_manager.last_prompt == prompt
        assert agent_manager.last_response == str(
            response
        )  # AgentResult string conversion
        assert len(str(response)) > 0

        # Verify response is reasonable
        assert "Paris" in str(response) or "paris" in str(response).lower()

    def test_response_always_string_with_real_llm(self, test_config: dict) -> None:
        """
        Test that responses convert to strings with REAL LLM.

        This is the definitive test - no mocks.
        """
        agent_manager = AgentManager(test_config)
        agent_manager.create_agent("test_agent")

        # Run agent
        response = agent_manager.run_agent(
            "test_agent", "What is your favorite color? One word answer."
        )

        # Verify response converts to string (AgentResult.__str__())
        assert isinstance(agent_manager.last_response, str)
        assert isinstance(str(response), str)  # AgentResult can convert to string
        assert len(str(response)) > 0
