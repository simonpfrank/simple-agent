"""
Unit tests for SimpleAgent.

Tests the thin wrapper around SmolAgents with support for multiple agent types.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


from simple_agent.agents.simple_agent import SimpleAgent


class TestSimpleAgentInitialization:
    """Test SimpleAgent initialization."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

        # AgentResult should work as string (backward compatibility)
        assert str(result) == "This is the agent response"
        mock_agent_instance.run.assert_called_once_with("What is 2+2?", reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

        # Result should be AgentResult, which contains the dict response
        from simple_agent.core.agent_result import AgentResult
        assert isinstance(result, AgentResult)
        # Response should be dict that was converted to string
        assert "response" in str(result) or "data" in str(result)


class TestSimpleAgentRepr:
    """Test SimpleAgent string representation."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_repr_format(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
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


class TestSimpleAgentUserPromptTemplate:
    """Test user_prompt_template functionality."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_user_prompt_template_formats_input(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that user_prompt_template formats user input correctly."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent BEFORE creating SimpleAgent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Create agent with user_prompt_template
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template="{user_input}\n\nPlease answer concisely.",
        )

        # Run with user input
        agent.run("What is 2+2?")

        # Verify the template was applied
        mock_agent_instance.run.assert_called_once_with(
            "What is 2+2?\n\nPlease answer concisely.", reset=True
        )

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_user_prompt_template_none_uses_direct_input(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that no template means direct pass-through of user input."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent BEFORE creating SimpleAgent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Create agent WITHOUT user_prompt_template
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
        )

        # Run with user input
        agent.run("What is 2+2?")

        # Verify the input was passed directly (no formatting)
        mock_agent_instance.run.assert_called_once_with("What is 2+2?", reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_user_prompt_template_multiline(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that multi-line templates work correctly."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        template = """
{user_input}

Let's think through this step by step:
1. First, understand the question
2. Then, provide a clear answer
"""

        # Mock the underlying agent BEFORE creating SimpleAgent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a logical assistant.",
            user_prompt_template=template,
        )

        # Run with user input
        agent.run("Explain quantum computing")

        # Verify the multi-line template was applied
        expected = """
Explain quantum computing

Let's think through this step by step:
1. First, understand the question
2. Then, provide a clear answer
"""
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_user_prompt_template_with_chat_mode(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that template persists across chat turns (reset=False)."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent BEFORE creating SimpleAgent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template="{user_input} (Be brief)",
        )

        # Multiple turns with reset=False (chat mode)
        agent.run("First question", reset=False)
        agent.run("Second question", reset=False)

        # Verify template was applied to both
        assert mock_agent_instance.run.call_count == 2
        mock_agent_instance.run.assert_any_call("First question (Be brief)", reset=False)
        mock_agent_instance.run.assert_any_call("Second question (Be brief)", reset=False)


class TestSimpleAgentJinja2:
    """Test Jinja2 template rendering in SimpleAgent."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_role_with_variables(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 template rendering in role field with agent_name variable."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Role with Jinja2 template
        role_template = "You are {{ agent_name }}, a helpful assistant."

        agent = SimpleAgent(
            name="TestBot",
            model_provider="openai",
            model_config=model_config,
            role=role_template,
        )

        # Verify role was rendered with agent_name
        assert agent.role == "You are TestBot, a helpful assistant."

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_user_prompt_template_with_conditionals(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 conditionals in user_prompt_template."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template with conditional based on verbosity
        template = """{{ user_input }}

{% if verbosity >= 2 %}
Please provide detailed step-by-step reasoning.
{% else %}
Please be concise.
{% endif %}"""

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template=template,
            verbosity=2,  # High verbosity
        )

        agent.run("What is 2+2?")

        # Verify conditional rendered correctly (verbosity >= 2)
        expected = """What is 2+2?

Please provide detailed step-by-step reasoning."""
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_with_loops(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 loops over tools list."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock tools
        mock_tool1 = Mock()
        mock_tool1.name = "calculator"
        mock_tool2 = Mock()
        mock_tool2.name = "web_search"

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template with loop
        template = """{{ user_input }}

{% if tools %}
Available tools:
{% for tool in tools %}
- {{ tool }}
{% endfor %}
{% endif %}"""

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template=template,
            tools=[mock_tool1, mock_tool2],
        )

        agent.run("Help me")

        # Verify loop rendered tool names
        expected = """Help me

Available tools:
- calculator
- web_search"""
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_with_filters(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 filters like upper, lower."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template with filter
        template = "Agent: {{ agent_name | upper }} - {{ user_input }}"

        agent = SimpleAgent(
            name="mybot",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template=template,
        )

        agent.run("Hello")

        # Verify filter applied (agent_name uppercased)
        expected = "Agent: MYBOT - Hello"
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_with_date_formatting(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 with current_time and current_date variables."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Role template with date formatting
        role_template = "You are {{ agent_name }}. Today is {{ current_date.strftime('%Y-%m-%d') }}."

        agent = SimpleAgent(
            name="TestBot",
            model_provider="openai",
            model_config=model_config,
            role=role_template,
        )

        # Verify role contains rendered date (format: YYYY-MM-DD)
        assert agent.role.startswith("You are TestBot. Today is ")
        assert len(agent.role.split("Today is ")[1]) == 11  # YYYY-MM-DD + period = 11 chars

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_backward_compatibility_format_string(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that old-style {user_input} format strings still work."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Old-style format string (no {{ }})
        template = "{user_input}\n\nPlease be concise."

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="You are a helpful assistant.",
            user_prompt_template=template,
        )

        agent.run("What is AI?")

        # Verify old format still works
        expected = "What is AI?\n\nPlease be concise."
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_error_handling(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test error handling for invalid Jinja2 syntax."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Invalid Jinja2 syntax (unclosed tag)
        role_template = "You are {{ agent_name"

        # Should raise ValueError with helpful message
        try:
            agent = SimpleAgent(
                name="TestBot",
                model_provider="openai",
                model_config=model_config,
                role=role_template,
            )
            assert False, "Should have raised ValueError for invalid Jinja2"
        except ValueError as e:
            assert "jinja2" in str(e).lower() or "template" in str(e).lower()

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_context_variables(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that all context variables are available in templates."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template using multiple context variables
        template = """Agent: {{ agent_name }}
Provider: {{ model_provider }}
Verbosity: {{ verbosity }}
Max Steps: {{ max_steps }}
{{ user_input }}"""

        agent = SimpleAgent(
            name="TestBot",
            model_provider="openai",
            model_config=model_config,
            role="Test",
            user_prompt_template=template,
            verbosity=2,
            max_steps=15,
        )

        agent.run("Help")

        # Verify all variables rendered
        expected = """Agent: TestBot
Provider: openai
Verbosity: 2
Max Steps: 15
Help"""
        mock_agent_instance.run.assert_called_once_with(expected, reset=True)


class TestSimpleAgentJinja2Security:
    """Test Jinja2 sandbox security in SimpleAgent."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_sandbox_blocks_subclasses_access(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that sandbox blocks access to __subclasses__ (dangerous method)."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        mock_agent_instance = Mock()
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template attempting to access __subclasses__ (used in RCE attacks)
        malicious_template = "{{ agent_name.__class__.__subclasses__() }}"

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
            user_prompt_template=malicious_template,
        )

        # Should raise an error due to sandbox restriction
        from jinja2.sandbox import SecurityError
        with pytest.raises((ValueError, SecurityError)):
            agent.run("test")

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_sandbox_blocks_mro_access(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that sandbox blocks __mro__ chain walking attacks."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        mock_agent_instance = Mock()
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Template attempting MRO chain walking
        malicious_template = "{{ agent_name.__class__.__mro__ }}"

        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
            user_prompt_template=malicious_template,
        )

        from jinja2.sandbox import SecurityError
        with pytest.raises((ValueError, SecurityError)):
            agent.run("test")

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_safe_templates_still_work(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that legitimate templates work with the sandbox."""
        model_config = {"model": "gpt-4o-mini", "api_key": "sk-test"}

        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Response"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Safe template using standard features (no slicing datetime)
        safe_template = """{{ user_input | upper }}
Agent: {{ agent_name }}
Provider: {{ model_provider }}"""

        agent = SimpleAgent(
            name="safe_agent",
            model_provider="openai",
            model_config=model_config,
            role="Test",
            user_prompt_template=safe_template,
        )

        # Should work without errors
        agent.run("hello")

        # Verify the template rendered (input was uppercased)
        call_args = mock_agent_instance.run.call_args[0][0]
        assert "HELLO" in call_args
        assert "safe_agent" in call_args
        assert "openai" in call_args
