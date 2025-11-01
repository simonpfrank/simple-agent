"""Unit tests for token budget configuration in AgentManager."""
import pytest
from unittest.mock import patch, Mock

from simple_agent.core.agent_manager import AgentManager


class TestAgentManagerTokenConfig:
    """Test token budget configuration in AgentManager."""

    def test_create_agent_reads_token_budget_from_config(self) -> None:
        """AgentManager should read token_budget from agent config."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "researcher": {
                    "role": "Research agent",
                    "token_budget": 20000,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("researcher")

        # Agent should have token_budget from config
        assert agent.token_budget == 20000

    def test_create_agent_reads_token_warning_threshold_from_config(self) -> None:
        """AgentManager should read token_warning_threshold from agent config."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "researcher": {
                    "role": "Research agent",
                    "token_budget": 20000,
                    "token_warning_threshold": 18000,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("researcher")

        # Agent should have token_warning_threshold from config
        assert agent.token_warning_threshold == 18000

    def test_create_agent_without_token_config_defaults_to_none(self) -> None:
        """Agent should have None token values if not in config."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "default": {
                    "role": "Default agent",
                    # No token_budget or token_warning_threshold
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("default")

        # Should default to None
        assert agent.token_budget is None
        assert agent.token_warning_threshold is None

    def test_create_agent_with_create_agent_method(self) -> None:
        """create_agent method should accept token_budget parameter."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {"default": {"role": "Default"}},
        }

        manager = AgentManager(config)

        with patch("simple_agent.core.agent_manager.SimpleAgent") as mock_agent_class:
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            manager.create_agent("test", token_budget=15000, token_warning_threshold=13000)

            # Verify SimpleAgent was called with token parameters
            mock_agent_class.assert_called_once()
            call_kwargs = mock_agent_class.call_args.kwargs
            assert call_kwargs.get("token_budget") == 15000
            assert call_kwargs.get("token_warning_threshold") == 13000


class TestAgentManagerConfigIntegration:
    """Test full integration of token config from config.yaml to agent."""

    def test_agent_created_from_config_has_token_values(self) -> None:
        """Agent loaded from config should have token values."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "researcher": {
                    "role": "Research assistant",
                    "token_budget": 25000,
                    "token_warning_threshold": 22000,
                    "max_steps": 10,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("researcher")

        assert agent.token_budget == 25000
        assert agent.token_warning_threshold == 22000

    def test_multiple_agents_with_different_token_budgets(self) -> None:
        """Different agents can have different token budgets."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "planner": {
                    "role": "Planner",
                    "token_budget": 10000,
                },
                "researcher": {
                    "role": "Researcher",
                    "token_budget": 25000,
                },
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        planner = manager.get_agent("planner")
        researcher = manager.get_agent("researcher")

        assert planner.token_budget == 10000
        assert researcher.token_budget == 25000

    def test_default_agent_inherits_token_config(self) -> None:
        """Default agent should inherit token config if specified."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "default": {
                    "role": "Default assistant",
                    "token_budget": 20000,
                    "token_warning_threshold": 18000,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("default")

        assert agent.token_budget == 20000
        assert agent.token_warning_threshold == 18000

    def test_agent_config_does_not_interfere_with_tools(self) -> None:
        """Agent config should work independently of tools."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "researcher": {
                    "role": "Research assistant",
                    "token_budget": 20000,
                    "token_warning_threshold": 18000,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("researcher")

        # Token config should be preserved regardless of tools
        assert agent.token_budget == 20000
        assert agent.token_warning_threshold == 18000
        assert agent.tools == []  # No tools in this config


class TestTokenConfigEdgeCases:
    """Test edge cases in token configuration."""

    def test_zero_token_budget_is_valid(self) -> None:
        """Zero token budget should be stored (though not practical)."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "restricted": {
                    "role": "Test",
                    "token_budget": 0,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("restricted")
        assert agent.token_budget == 0

    def test_very_large_token_budget(self) -> None:
        """Very large token budget should be stored."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "unlimited": {
                    "role": "Test",
                    "token_budget": 1000000,
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("unlimited")
        assert agent.token_budget == 1000000

    def test_warning_threshold_greater_than_budget_is_allowed(self) -> None:
        """Config shouldn't validate relationships (business logic can)."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini"},
            },
            "agents": {
                "test": {
                    "role": "Test",
                    "token_budget": 1000,
                    "token_warning_threshold": 5000,  # Greater than budget
                }
            },
        }

        manager = AgentManager(config)
        manager._load_agents_from_config()

        agent = manager.get_agent("test")
        # Should store as-is without validation
        assert agent.token_budget == 1000
        assert agent.token_warning_threshold == 5000
