"""
Integration tests for Phase 1.7: Jinja2 Template Support.

Tests the full Jinja2 template rendering workflow including role and user_prompt_template.
"""

from unittest.mock import Mock, patch

from simple_agent.core.agent_manager import AgentManager


class TestPhase1_7Jinja2Integration:
    """Integration tests for Jinja2 template rendering in YAML workflows."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_full_workflow(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test complete workflow: create agent with Jinja2 templates, run prompt, verify rendering."""
        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "4"
        mock_tool_calling_agent.return_value = mock_agent_instance

        # Configuration with Jinja2 templates and verbosity setting
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "default": {
                    "verbosity": 2,  # Set verbosity in config
                    "max_steps": 10,
                }
            },
        }

        agent_manager = AgentManager(config)

        # Create agent with Jinja2 role and user_prompt_template
        agent = agent_manager.create_agent(
            name="jinja_bot",
            provider="openai",
            role="You are {{ agent_name }} powered by {{ model_provider }}.",
            user_prompt_template="""{{ user_input }}

{% if verbosity >= 2 %}
Please show your work step by step.
{% endif %}""",
        )

        # Verify role was rendered
        assert agent.role == "You are jinja_bot powered by openai."

        # Run prompt
        response = agent_manager.run_agent("jinja_bot", "What is 2+2?")

        # Verify response (AgentResult supports string conversion)
        assert str(response) == "4"

        # Verify user_prompt_template was applied with conditional
        expected_prompt = """What is 2+2?

Please show your work step by step."""
        mock_agent_instance.run.assert_called_once_with(expected_prompt, reset=True)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_jinja2_with_yaml_style_templates(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test Jinja2 with YAML-style multi-line templates (using | syntax in YAML)."""
        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Paris"
        mock_tool_calling_agent.return_value = mock_agent_instance

        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "default": {
                    "verbosity": 1,  # Set verbosity in config
                    "max_steps": 10,
                }
            },
        }

        agent_manager = AgentManager(config)

        # Multi-line template as would appear in YAML with | syntax
        multiline_template = """You are {{ agent_name }}, a knowledge assistant.
Created on: {{ current_date.strftime('%Y-%m-%d') }}

{% if verbosity == 0 %}
Be extremely concise.
{% elif verbosity == 1 %}
Provide clear answers.
{% else %}
Provide detailed explanations.
{% endif %}"""

        agent = agent_manager.create_agent(
            name="knowledge_bot",
            provider="openai",
            role=multiline_template,
        )

        # Verify role rendered with current date
        assert "You are knowledge_bot, a knowledge assistant." in agent.role
        assert "Created on:" in agent.role
        assert "Provide clear answers." in agent.role
        # Should not have other verbosity options
        assert "Be extremely concise." not in agent.role
        assert "Provide detailed explanations." not in agent.role

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    def test_backward_compatibility_with_format_strings(
        self, mock_tool_calling_agent: Mock, mock_litellm: Mock
    ) -> None:
        """Test that old-style format strings still work alongside Jinja2."""
        # Mock the underlying agent
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = "Done"
        mock_tool_calling_agent.return_value = mock_agent_instance

        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        agent_manager = AgentManager(config)

        # Old-style format string (no {{ }})
        agent = agent_manager.create_agent(
            name="compat_bot",
            provider="openai",
            role="You are a helpful assistant.",
            user_prompt_template="{user_input}\\n\\nBe concise.",
        )

        agent_manager.run_agent("compat_bot", "Hello")

        # Verify old format string was applied
        mock_agent_instance.run.assert_called_once_with("Hello\\n\\nBe concise.", reset=True)
