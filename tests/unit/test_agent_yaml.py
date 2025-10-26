"""
Unit tests for YAML agent loading and saving (Phase 1.5).

Tests AgentManager YAML methods for loading/saving agent definitions.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from simple_agent.core.agent_manager import AgentManager


class TestLoadAgentFromYAML:
    """Test loading single agent from YAML file."""

    @pytest.fixture
    def temp_yaml_file(self) -> str:
        """Create temporary YAML file with agent definition."""
        content = """
name: "test_agent"
agent_type: "tool_calling"
role: "You are a test agent."

tools:
  - add
  - multiply

model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.5

settings:
  verbosity: 2
  max_steps: 20

metadata:
  description: "Test agent"
  author: "test"
  version: "1.0.0"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            return f.name

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agent_from_yaml_success(
        self, mock_simple_agent: MagicMock, temp_yaml_file: str
    ) -> None:
        """Test loading agent from valid YAML file."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Mock agent instance
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.tool_manager = MagicMock()

        # Load agent from YAML
        agent = manager.load_agent_from_yaml(temp_yaml_file)

        # Verify agent was created with correct settings
        assert agent is not None
        assert "test_agent" in manager.agents
        assert manager.agents["test_agent"] == agent

        # Cleanup
        os.unlink(temp_yaml_file)

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agent_from_yaml_with_defaults(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test loading agent with minimal YAML (uses defaults)."""
        content = """
name: "minimal_agent"
role: "You are a minimal agent."
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = f.name

        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        agent = manager.load_agent_from_yaml(yaml_file)

        # Verify agent was created with defaults
        assert agent is not None
        assert "minimal_agent" in manager.agents

        # Cleanup
        os.unlink(yaml_file)

    def test_load_agent_from_yaml_file_not_found(self) -> None:
        """Test loading from non-existent file raises error."""
        config = {}
        manager = AgentManager(config)

        with pytest.raises(FileNotFoundError):
            manager.load_agent_from_yaml("/nonexistent/path.yaml")

    def test_load_agent_from_yaml_invalid_yaml(self) -> None:
        """Test loading invalid YAML raises error."""
        content = "invalid: yaml: content: ["
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = f.name

        config = {}
        manager = AgentManager(config)

        with pytest.raises(yaml.YAMLError):
            manager.load_agent_from_yaml(yaml_file)

        # Cleanup
        os.unlink(yaml_file)

    def test_load_agent_from_yaml_missing_name(self) -> None:
        """Test loading YAML without 'name' field raises error."""
        content = """
role: "You are an agent without a name."
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = f.name

        config = {}
        manager = AgentManager(config)

        with pytest.raises(ValueError, match="name"):
            manager.load_agent_from_yaml(yaml_file)

        # Cleanup
        os.unlink(yaml_file)

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agent_from_yaml_with_user_prompt_template(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test loading agent from YAML with user_prompt_template field."""
        content = """
name: "template_agent"
role: "You are a test assistant"
user_prompt_template: "{user_input}\\n\\nPlease answer concisely."
model:
  provider: "openai"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = f.name

        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.load_agent_from_yaml(yaml_file)

        # Verify user_prompt_template was passed to create_agent -> SimpleAgent
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs["user_prompt_template"] == "{user_input}\n\nPlease answer concisely."

        # Cleanup
        os.unlink(yaml_file)

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agent_from_yaml_without_user_prompt_template(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test loading agent from YAML without user_prompt_template (should be None)."""
        content = """
name: "no_template_agent"
role: "You are a test assistant"
model:
  provider: "openai"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = f.name

        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.load_agent_from_yaml(yaml_file)

        # Verify user_prompt_template was None (not specified in YAML)
        call_kwargs = mock_simple_agent.call_args.kwargs
        assert call_kwargs.get("user_prompt_template") is None

        # Cleanup
        os.unlink(yaml_file)


class TestSaveAgentToYAML:
    """Test saving agent to YAML file."""

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_save_agent_to_yaml_success(self, mock_simple_agent: MagicMock) -> None:
        """Test saving agent to YAML file."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Create mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "test_agent"
        mock_agent_instance.agent_type = "tool_calling"
        mock_agent_instance.role = "You are a test agent."
        mock_agent_instance.user_prompt_template = None
        mock_agent_instance.tools = []
        mock_agent_instance.model_provider = "openai"
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("test_agent", role="You are a test agent.")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_file = f.name

        manager.save_agent_to_yaml("test_agent", yaml_file)

        # Verify file was created and contains agent data
        assert os.path.exists(yaml_file)

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        assert data["name"] == "test_agent"
        assert "role" in data

        # Cleanup
        os.unlink(yaml_file)

    def test_save_agent_to_yaml_nonexistent_agent(self) -> None:
        """Test saving non-existent agent raises error."""
        config = {}
        manager = AgentManager(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_file = f.name

        with pytest.raises(KeyError, match="not found"):
            manager.save_agent_to_yaml("nonexistent", yaml_file)

        # Cleanup
        os.unlink(yaml_file)

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_save_agent_to_yaml_with_user_prompt_template(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test saving agent with user_prompt_template to YAML file."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Create mock agent with user_prompt_template
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "template_agent"
        mock_agent_instance.agent_type = "tool_calling"
        mock_agent_instance.role = "You are a test agent."
        mock_agent_instance.user_prompt_template = "{user_input}\n\nBe concise."
        mock_agent_instance.tools = []
        mock_agent_instance.model_provider = "openai"
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("template_agent", role="You are a test agent.")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_file = f.name

        manager.save_agent_to_yaml("template_agent", yaml_file)

        # Verify file contains user_prompt_template
        assert os.path.exists(yaml_file)

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        assert data["name"] == "template_agent"
        assert data["user_prompt_template"] == "{user_input}\n\nBe concise."

        # Cleanup
        os.unlink(yaml_file)

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_save_agent_to_yaml_without_user_prompt_template(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test saving agent without user_prompt_template to YAML (field should not exist)."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        # Create mock agent without user_prompt_template
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "no_template_agent"
        mock_agent_instance.agent_type = "tool_calling"
        mock_agent_instance.role = "You are a test agent."
        mock_agent_instance.user_prompt_template = None
        mock_agent_instance.tools = []
        mock_agent_instance.model_provider = "openai"
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        manager.create_agent("no_template_agent", role="You are a test agent.")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_file = f.name

        manager.save_agent_to_yaml("no_template_agent", yaml_file)

        # Verify file does NOT contain user_prompt_template field
        assert os.path.exists(yaml_file)

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        assert data["name"] == "no_template_agent"
        assert "user_prompt_template" not in data

        # Cleanup
        os.unlink(yaml_file)


class TestLoadAgentsFromDirectory:
    """Test loading multiple agents from directory."""

    @pytest.fixture
    def temp_agents_dir(self) -> str:
        """Create temporary directory with agent YAML files."""
        temp_dir = tempfile.mkdtemp()

        # Create agent1.yaml
        agent1 = """
name: "agent1"
role: "Agent 1"
"""
        with open(os.path.join(temp_dir, "agent1.yaml"), "w") as f:
            f.write(agent1)

        # Create agent2.yaml
        agent2 = """
name: "agent2"
role: "Agent 2"
"""
        with open(os.path.join(temp_dir, "agent2.yaml"), "w") as f:
            f.write(agent2)

        # Create invalid.yaml (missing name)
        invalid = """
role: "Invalid agent"
"""
        with open(os.path.join(temp_dir, "invalid.yaml"), "w") as f:
            f.write(invalid)

        # Create non-yaml file (should be ignored)
        with open(os.path.join(temp_dir, "readme.txt"), "w") as f:
            f.write("Not a YAML file")

        return temp_dir

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agents_from_directory(
        self, mock_simple_agent: MagicMock, temp_agents_dir: str
    ) -> None:
        """Test loading multiple agents from directory."""
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        manager = AgentManager(config)
        count = manager.load_agents_from_directory(temp_agents_dir)

        # Should load 2 valid agents, skip invalid.yaml and readme.txt
        assert count == 2
        assert "agent1" in manager.agents
        assert "agent2" in manager.agents
        assert "invalid" not in manager.agents

        # Cleanup
        import shutil

        shutil.rmtree(temp_agents_dir)

    def test_load_agents_from_nonexistent_directory(self) -> None:
        """Test loading from non-existent directory."""
        config = {}
        manager = AgentManager(config)

        # Should not raise error, just return 0
        count = manager.load_agents_from_directory("/nonexistent/directory")
        assert count == 0

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_load_agents_from_empty_directory(
        self, mock_simple_agent: MagicMock
    ) -> None:
        """Test loading from empty directory."""
        temp_dir = tempfile.mkdtemp()

        config = {}
        manager = AgentManager(config)
        count = manager.load_agents_from_directory(temp_dir)

        assert count == 0

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir)
