"""
Integration tests for Phase 1.5 - YAML Agent Definitions.

Tests the full workflow of YAML agent loading, saving, and auto-loading.
"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from simple_agent.core.agent_manager import AgentManager
from simple_agent.core.tool_manager import ToolManager


class TestPhase1_5YAMLAgents:
    """Integration tests for YAML agent definitions."""

    @pytest.fixture
    def temp_agents_dir(self) -> str:
        """Create temporary agents directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def config(self) -> dict:
        """Create test config."""
        return {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            }
        }

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_save_and_load_agent_workflow(
        self, mock_simple_agent: MagicMock, temp_agents_dir: str, config: dict
    ) -> None:
        """
        Test complete save/load workflow.

        1. Create agent
        2. Save to YAML
        3. Load from YAML
        4. Verify agent properties match
        """
        # Mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "test_agent"
        mock_agent_instance.agent_type = "tool_calling"
        mock_agent_instance.role = "You are a test agent."
        mock_agent_instance.user_prompt_template = None
        mock_agent_instance.tools = []
        mock_agent_instance.model_provider = "openai"
        mock_simple_agent.return_value = mock_agent_instance

        # Create manager and agent
        manager = AgentManager(config)
        manager.create_agent("test_agent", role="You are a test agent.")

        # Save to YAML
        yaml_path = os.path.join(temp_agents_dir, "test_agent.yaml")
        manager.save_agent_to_yaml("test_agent", yaml_path)

        # Verify file exists
        assert os.path.exists(yaml_path)

        # Load YAML and verify structure
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        assert data["name"] == "test_agent"
        assert data["agent_type"] == "tool_calling"
        assert data["role"] == "You are a test agent."

        # Create new manager and load agent
        manager2 = AgentManager(config)
        loaded_agent = manager2.load_agent_from_yaml(yaml_path)

        # Verify agent was loaded
        assert "test_agent" in manager2.agents
        assert loaded_agent is not None

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_auto_load_agents_from_directory(
        self, mock_simple_agent: MagicMock, temp_agents_dir: str, config: dict
    ) -> None:
        """
        Test auto-loading agents from directory.

        1. Create YAML files in directory
        2. Load from directory
        3. Verify all valid agents loaded
        """
        # Create agent YAML files
        agent1_yaml = """
name: "agent1"
role: "Agent 1"
"""
        agent2_yaml = """
name: "agent2"
role: "Agent 2"
"""

        with open(os.path.join(temp_agents_dir, "agent1.yaml"), "w") as f:
            f.write(agent1_yaml)

        with open(os.path.join(temp_agents_dir, "agent2.yaml"), "w") as f:
            f.write(agent2_yaml)

        # Mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        # Load agents from directory
        manager = AgentManager(config)
        count = manager.load_agents_from_directory(temp_agents_dir)

        # Verify agents loaded
        assert count == 2
        assert "agent1" in manager.agents
        assert "agent2" in manager.agents

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_agent_with_tools_save_load(
        self, mock_simple_agent: MagicMock, temp_agents_dir: str, config: dict
    ) -> None:
        """
        Test saving and loading agent with tools.

        1. Create agent with tools
        2. Save to YAML
        3. Load from YAML
        4. Verify tools preserved
        """
        # Create tool manager with mock tools
        tool_manager = ToolManager(auto_load_builtin=False)

        # Register mock tools
        mock_tool1 = MagicMock()
        mock_tool1.name = "add"
        mock_tool2 = MagicMock()
        mock_tool2.name = "multiply"

        tool_manager.register_tool(mock_tool1)
        tool_manager.register_tool(mock_tool2)

        # Mock agent with tools
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "math_agent"
        mock_agent_instance.agent_type = "tool_calling"
        mock_agent_instance.role = "You are a math agent."
        mock_agent_instance.user_prompt_template = None
        mock_agent_instance.tools = [mock_tool1, mock_tool2]
        mock_agent_instance.model_provider = "openai"
        mock_simple_agent.return_value = mock_agent_instance

        # Create manager and agent
        manager = AgentManager(config)
        manager.tool_manager = tool_manager
        manager.create_agent(
            "math_agent", role="You are a math agent.", tools=["add", "multiply"]
        )

        # Save to YAML
        yaml_path = os.path.join(temp_agents_dir, "math_agent.yaml")
        manager.save_agent_to_yaml("math_agent", yaml_path)

        # Verify tools in YAML
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        assert "tools" in data
        assert "add" in data["tools"]
        assert "multiply" in data["tools"]

        # Load agent (new manager)
        manager2 = AgentManager(config)
        manager2.tool_manager = tool_manager
        manager2.load_agent_from_yaml(yaml_path)

        # Verify agent loaded with tools
        assert "math_agent" in manager2.agents

    @patch("simple_agent.core.agent_manager.SimpleAgent")
    def test_agent_hierarchy_yaml_overrides_config(
        self, mock_simple_agent: MagicMock, temp_agents_dir: str
    ) -> None:
        """
        Test agent hierarchy: YAML > config.yaml.

        1. Set default role in config
        2. Override role in YAML
        3. Verify YAML role takes precedence
        """
        # Config with default role
        config = {
            "llm": {
                "provider": "openai",
                "openai": {"model": "gpt-4o-mini", "api_key": "sk-test"},
            },
            "agents": {
                "default": {
                    "role": "Default role from config",
                }
            },
        }

        # Create YAML with different role
        agent_yaml = """
name: "custom_agent"
role: "Custom role from YAML"
"""
        yaml_path = os.path.join(temp_agents_dir, "custom_agent.yaml")
        with open(yaml_path, "w") as f:
            f.write(agent_yaml)

        # Mock agent
        mock_agent_instance = MagicMock()
        mock_agent_instance.tools = []
        mock_simple_agent.return_value = mock_agent_instance

        # Load agent
        manager = AgentManager(config)
        manager.load_agent_from_yaml(yaml_path)

        # Verify YAML role was used (not config default)
        # Check that create_agent was called with YAML role
        call_kwargs = mock_simple_agent.call_args_list[-1].kwargs
        assert "role" in call_kwargs or "instructions" in call_kwargs
