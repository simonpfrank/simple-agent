"""
Unit tests for SimpleAgent.

Tests the thin wrapper around SmolAgents with support for multiple agent types.
"""

from unittest.mock import Mock, patch, MagicMock


from simple_agent.agents.simple_agent import SimpleAgent


class TestSimpleAgentInitialization:
    """Test SimpleAgent initialization."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_init_with_explicit_role(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
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
        mock_tool_calling_agent.assert_called_once()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    @patch("simple_agent.agents.simple_agent.ConfigManager")
    def test_init_with_template(
        self, mock_config_manager: Mock, mock_tool_calling_agent: Mock, mock_litellm: Mock
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
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_init_role_overrides_template(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
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
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_init_with_custom_verbosity_and_max_steps(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with custom max_steps (verbosity not used for ToolCallingAgent)."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test role",
            verbosity=2,
            max_steps=20,
        )

        # Verify ToolCallingAgent was called with correct parameters
        call_kwargs = mock_tool_calling_agent.call_args.kwargs
        # Note: ToolCallingAgent doesn't have verbosity_level parameter
        assert call_kwargs["max_steps"] == 20
        assert call_kwargs["instructions"] == "Test role"


class TestSimpleAgentModelCreation:
    """Test LiteLLM model creation for different providers."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_create_model_openai(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test creating OpenAI model."""
        model_config = {
            "model": "gpt-4o-mini",
            "api_key": "sk-test",
            "temperature": 0.7,
        }

        SimpleAgent(
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
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_create_model_ollama(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test creating Ollama model."""
        model_config = {
            "model": "llama3.2:1b",
            "base_url": "http://localhost:11434",
        }

        SimpleAgent(
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
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_run_returns_string_response(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test run method returns agent response as string."""
        # Setup mock agent response
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "This is the agent response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        result = agent.run("What is 2+2?")

        assert result == "This is the agent response"
        mock_agent_instance.run.assert_called_once_with("What is 2+2?", reset=True)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_run_converts_non_string_to_string(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test run method converts non-string responses to string."""
        # Setup mock agent that returns a dict
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = {"response": "data"}
        mock_tool_calling_agent.return_value = mock_agent_instance

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
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_repr_format(self, mock_tool_calling_agent: Mock, mock_litellm: Mock) -> None:
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


class TestSimpleAgentTypes:
    """Test SimpleAgent with different agent types."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_init_with_tool_calling_agent_type(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with agent_type='tool_calling'."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        role = "You are a helpful assistant."

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role=role,
            agent_type="tool_calling",
        )

        assert agent.name == "test_agent"
        assert agent.agent_type == "tool_calling"
        mock_tool_calling_agent.assert_called_once()
        mock_litellm.assert_called_once()

        # Verify ToolCallingAgent was called with correct parameters
        call_kwargs = mock_tool_calling_agent.call_args.kwargs
        assert call_kwargs["instructions"] == role
        assert call_kwargs["max_steps"] == 10

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_init_with_code_agent_type_docker(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test initialization with agent_type='code' and docker executor."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}
        role = "You are a helpful assistant."

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role=role,
            agent_type="code",
            executor_type="docker",
        )

        assert agent.name == "test_agent"
        assert agent.agent_type == "code"
        mock_code_agent.assert_called_once()

        # Verify CodeAgent was called with docker executor
        call_kwargs = mock_code_agent.call_args.kwargs
        assert call_kwargs["executor_type"] == "docker"
        assert call_kwargs["instructions"] == role

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_init_defaults_to_tool_calling_agent(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that default agent_type is 'tool_calling' for security."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
        )

        # Default should be ToolCallingAgent for security
        assert agent.agent_type == "tool_calling"
        mock_tool_calling_agent.assert_called_once()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.CodeAgent")
    def test_code_agent_rejects_local_executor(
        self, mock_code_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that attempting to use 'local' executor raises error."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Should raise ValueError when trying to use local executor
        try:
            SimpleAgent(
                name="test_agent",
                model_provider="openai",
                model_config=model_config,
                role="Test",
                agent_type="code",
                executor_type="local",
            )
            # If we get here, test should fail
            assert False, "Should have raised ValueError for local executor"
        except ValueError as e:
            assert "local" in str(e).lower()
            assert "security" in str(e).lower() or "unsafe" in str(e).lower()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_invalid_agent_type_raises_error(self, mock_litellm: Mock) -> None:
        """Test that invalid agent_type raises ValueError."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        try:
            SimpleAgent(
                name="test_agent",
                model_provider="openai",
                model_config=model_config,
                role="Test",
                agent_type="invalid_type",
            )
            assert False, "Should have raised ValueError for invalid agent_type"
        except ValueError as e:
            assert "agent_type" in str(e).lower()
            assert "invalid_type" in str(e)
