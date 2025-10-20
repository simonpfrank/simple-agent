"""
Unit tests for SimpleAgent.

Tests the thin wrapper around SmolAgents CodeAgent.
"""

from unittest.mock import Mock, patch, MagicMock

import pytest

from simple_agent.agents.simple_agent import SimpleAgent


class TestSimpleAgentInitialization:
    """Test SimpleAgent initialization."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_init_with_explicit_role(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with explicit role parameter."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        role = "You are a helpful assistant."

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role=role,
        )

        assert agent.name == "test_agent"
        assert agent.model_provider == "openai"
        assert agent.role == role
        mock_litellm.assert_called_once()
        mock_code_agent.assert_called_once()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    @patch("simple_agent.agents.simple_agent.ConfigManager")
    def test_init_with_template(
        self, mock_config_manager: Mock, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with template parameter."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        mock_config_manager.load_prompt_template.return_value = {
            "name": "researcher",
            "system": "You are a research assistant.",
        }

        agent = SimpleAgent(
            name="researcher_agent",
            model_provider="openai",
            model_config=model_config,
            template="researcher",
        )

        assert agent.name == "researcher_agent"
        assert agent.role == "You are a research assistant."
        mock_config_manager.load_prompt_template.assert_called_once_with("researcher")

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_init_role_overrides_template(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that explicit role overrides template."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        explicit_role = "Explicit role"

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role=explicit_role,
            template="researcher",  # Should be ignored
        )

        assert agent.role == explicit_role

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_init_with_custom_verbosity_and_max_steps(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with custom verbosity and max_steps."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test role",
            verbosity=2,
            max_steps=20,
        )

        # Verify CodeAgent was called with correct parameters
        call_kwargs = mock_code_agent.call_args.kwargs
        assert call_kwargs["verbosity_level"] == 2
        assert call_kwargs["max_steps"] == 20
        assert call_kwargs["instructions"] == "Test role"


class TestSimpleAgentModelCreation:
    """Test LiteLLM model creation for different providers."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_create_model_openai(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test creating OpenAI model."""
        model_config = {
            "model": "gpt-4o-mini",
            "api_key": "sk-test",
            "temperature": 0.7,
        }

        agent = SimpleAgent(
            name="openai_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        # Verify LiteLLM was called with OpenAI config
        mock_litellm.assert_called_once()
        call_args = mock_litellm.call_args
        assert "gpt-4o-mini" in str(call_args)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_create_model_ollama(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test creating Ollama model."""
        model_config = {
            "model": "llama3.2:1b",
            "base_url": "http://localhost:11434",
        }

        agent = SimpleAgent(
            name="ollama_agent",
            model_provider="ollama",
            model_config=model_config,
            role="Test",
        )

        # Verify LiteLLM was called
        mock_litellm.assert_called_once()


class TestSimpleAgentRun:
    """Test agent run method."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_run_returns_string_response(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test run method returns agent response as string."""
        # Setup mock agent response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "This is the agent response"
        mock_code_agent.return_value = mock_agent_instance

        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        result = agent.run("What is 2+2?")

        assert result == "This is the agent response"
        mock_agent_instance.run.assert_called_once_with("What is 2+2?")

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_run_converts_non_string_to_string(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test run method converts non-string responses to string."""
        # Setup mock agent that returns a dict
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = {"response": "data"}
        mock_code_agent.return_value = mock_agent_instance

        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        result = agent.run("Test prompt")

        assert isinstance(result, str)
        assert "response" in result or "data" in result


class TestSimpleAgentRepr:
    """Test SimpleAgent string representation."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_repr_format(self, mock_code_agent: Mock, mock_litellm: Mock) -> None:
        """Test __repr__ returns formatted string."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        repr_str = repr(agent)

        assert "SimpleAgent" in repr_str
        assert "test_agent" in repr_str
        assert "openai" in repr_str
