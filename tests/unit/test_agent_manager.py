"""
Unit tests for AgentManager.

Tests agent lifecycle management (create, store, retrieve, run).
"""

from unittest.mock import Mock, patch, MagicMock

import pytest

from simple_agent.core.agent_manager import AgentManager


class TestAgentManagerInit:
    """Test AgentManager initialization."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_init_with_config(self, mock_simple_agent: Mock) -> None:
        """Test initialization with configuration dict."""
        config = {
            "llm": {"provider": "openai", "openai": {"model": "gpt-4o-mini"}},
            "agents": {"default": {"role": "Test role"}},
        }

        manager = AgentManager(config)

        assert manager.config == config
        # Agents are NOT auto-loaded in __init__ (tool_manager not set yet)
        # They must be loaded later via _load_agents_from_config()
        assert len(manager.agents) == 0

    def test_init_empty_agents_dict(self) -> None:
        """Test agents dictionary is initialized empty."""
        config = {}

        manager = AgentManager(config)

        assert len(manager.agents) == 0


class TestAgentManagerCreateAgent:
    """Test agent creation functionality."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_with_defaults(self, mock_simple_agent: Mock) -> None:
        """Test creating agent with default config values."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "default": {
                    "role": "You are a helpful assistant.",
                    "verbosity": 1,
                    "max_steps": 10,
                }
            },
        }

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        # Verify SimpleAgent was called once (only for test_agent, no auto-load in __init__)
        assert mock_simple_agent.call_count == 1

        # Check the call (test_agent creation)
        call_kwargs = mock_simple_agent.call_args_list[0].kwargs
        assert call_kwargs["name"] == "test_agent"
        assert call_kwargs["model_provider"] == "openai"
        assert call_kwargs["role"] == "You are a helpful assistant."
        assert call_kwargs["verbosity"] == 1
        assert call_kwargs["max_steps"] == 10

        # Verify agent was registered
        assert "test_agent" in manager.agents

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_with_custom_provider(self, mock_simple_agent: Mock) -> None:
        """Test creating agent with custom provider override."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
                "ollama": {
                    "model": "llama3.2:1b",
                    "base_url": "http://localhost:11434",
                },
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        manager.create_agent("ollama_agent", provider="ollama")

        # Verify provider override worked
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs["model_provider"] == "ollama"
        assert call_kwargs["model_config"]["model"] == "llama3.2:1b"

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_with_custom_role(self, mock_simple_agent: Mock) -> None:
        """Test creating agent with custom role override."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Default role"}},
        }

        manager = AgentManager(config)
        custom_role = "Custom role for this agent"
        manager.create_agent("custom_agent", role=custom_role)

        # Verify role override worked
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs["role"] == custom_role

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_returns_instance(self, mock_simple_agent: Mock) -> None:
        """Test create_agent returns the created agent instance."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        mock_agent_instance = MagicMock()
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        result = manager.create_agent("test")

        assert result == mock_agent_instance

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_with_user_prompt_template(
        self, mock_simple_agent: Mock
    ) -> None:
        """Test creating agent with user_prompt_template parameter."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        template = "{user_input}\n\nPlease answer concisely."
        manager.create_agent("test_agent", user_prompt_template=template)

        # Verify user_prompt_template was passed to SimpleAgent
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs["user_prompt_template"] == template

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_create_agent_without_user_prompt_template(
        self, mock_simple_agent: Mock
    ) -> None:
        """Test creating agent without user_prompt_template (should be None)."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        # Verify user_prompt_template was None (not specified)
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs.get("user_prompt_template") is None


class TestAgentManagerGetAgent:
    """Test agent retrieval functionality."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_get_existing_agent(self, mock_simple_agent: Mock) -> None:
        """Test retrieving an existing agent."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        created_agent = manager.create_agent("test_agent")
        retrieved_agent = manager.get_agent("test_agent")

        assert retrieved_agent == created_agent

    def test_get_nonexistent_agent_raises_error(self) -> None:
        """Test retrieving non-existent agent raises KeyError."""
        config = {}
        manager = AgentManager(config)

        with pytest.raises(KeyError, match="Agent 'nonexistent' not found"):
            manager.get_agent("nonexistent")

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_get_agent_error_message_shows_available(
        self, mock_simple_agent: Mock
    ) -> None:
        """Test error message includes list of available agents."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        manager.create_agent("agent1")
        manager.create_agent("agent2")

        with pytest.raises(KeyError) as exc_info:
            manager.get_agent("missing")

        error_message = str(exc_info.value)
        assert "agent1" in error_message or "agent2" in error_message


class TestAgentManagerListAgents:
    """Test listing registered agents."""

    def test_list_agents_empty(self) -> None:
        """Test listing agents when none are registered."""
        config = {}
        manager = AgentManager(config)

        agents = manager.list_agents()

        assert agents == []

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_list_agents_with_multiple(self, mock_simple_agent: Mock) -> None:
        """Test listing multiple registered agents."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        manager = AgentManager(config)
        manager.create_agent("agent1")
        manager.create_agent("agent2")
        manager.create_agent("agent3")

        agents = manager.list_agents()

        # Should have 3 agents: agent1, agent2, agent3 (no auto-load in __init__)
        assert len(agents) == 3
        assert "agent1" in agents
        assert "agent2" in agents
        assert "agent3" in agents


class TestAgentManagerRunAgent:
    """Test running prompts through agents."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_success(self, mock_simple_agent: Mock) -> None:
        """Test running a prompt through an existing agent."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        # Setup mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Agent response"
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test_agent")

        result = manager.run_agent("test_agent", "What is 2+2?")

        assert result == "Agent response"
        mock_agent_instance.run.assert_called_once_with("What is 2+2?", reset=True)

    def test_run_nonexistent_agent_raises_error(self) -> None:
        """Test running prompt through non-existent agent raises KeyError."""
        config = {}
        manager = AgentManager(config)

        with pytest.raises(KeyError, match="Agent 'missing' not found"):
            manager.run_agent("missing", "test prompt")

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_run_agent_returns_string(self, mock_simple_agent: Mock) -> None:
        """Test run_agent returns response as string."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Test"}},
        }

        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "String response"
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test")

        result = manager.run_agent("test", "prompt")

        assert isinstance(result, str)
        assert result == "String response"
