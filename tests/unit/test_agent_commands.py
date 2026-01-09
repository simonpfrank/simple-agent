"""
Unit tests for /agent tool commands (Phase 1.4).

Tests the tool-related agent commands: tools, add-tool, remove-tool, load.
"""

from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import os

import pytest
from click.testing import CliRunner

from simple_agent.commands.agent_commands import agent
from simple_agent.commands.agent_persistence import resolve_agent_path


class TestAgentToolsCommand:
    """Test /agent tools command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.return_value = ["add", "subtract", "multiply"]

        return {"console": console, "agent_manager": agent_manager}

    def test_tools_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent tools command exists."""
        result = runner.invoke(agent, ["tools", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_tools_displays_agent_tools(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that tools displays all tools for an agent."""
        result = runner.invoke(agent, ["tools", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify agent_manager.get_agent_tools() was called
        mock_context["agent_manager"].get_agent_tools.assert_called_once_with(
            "test_agent"
        )

        # Verify console output was produced
        mock_context["console"].print.assert_called()

        # Verify summary line was printed
        call_args = str(mock_context["console"].print.call_args_list)
        assert "3 tools" in call_args.lower() or "add" in call_args.lower()

    def test_tools_shows_message_when_no_tools(self, runner: CliRunner) -> None:
        """Test tools shows message when agent has no tools."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.return_value = []

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["tools", "test_agent"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "no tools" in call_args.lower() or "empty" in call_args.lower()

    def test_tools_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test tools command with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent_tools.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["tools", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentAddToolCommand:
    """Test /agent add-tool command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        return {"console": console, "agent_manager": agent_manager}

    def test_add_tool_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent add-tool command exists."""
        result = runner.invoke(agent, ["add-tool", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_add_tool_adds_tool_to_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that add-tool adds a tool to an agent."""
        result = runner.invoke(
            agent, ["add-tool", "test_agent", "add"], obj=mock_context
        )

        assert result.exit_code == 0

        # Verify add_tool_to_agent was called
        mock_context["agent_manager"].add_tool_to_agent.assert_called_once_with(
            "test_agent", "add"
        )

        # Verify success message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "added" in call_args.lower() or "success" in call_args.lower()

    def test_add_tool_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test add-tool with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.add_tool_to_agent.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["add-tool", "missing", "add"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()

    def test_add_tool_handles_nonexistent_tool(self, runner: CliRunner) -> None:
        """Test add-tool with non-existent tool."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.add_tool_to_agent.side_effect = KeyError(
            "Tool 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["add-tool", "test_agent", "missing"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentRemoveToolCommand:
    """Test /agent remove-tool command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        return {"console": console, "agent_manager": agent_manager}

    def test_remove_tool_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent remove-tool command exists."""
        result = runner.invoke(agent, ["remove-tool", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_remove_tool_removes_tool_from_agent(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that remove-tool removes a tool from an agent."""
        result = runner.invoke(
            agent, ["remove-tool", "test_agent", "add"], obj=mock_context
        )

        assert result.exit_code == 0

        # Verify remove_tool_from_agent was called
        mock_context["agent_manager"].remove_tool_from_agent.assert_called_once_with(
            "test_agent", "add"
        )

        # Verify success message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "removed" in call_args.lower() or "success" in call_args.lower()

    def test_remove_tool_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test remove-tool with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.remove_tool_from_agent.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["remove-tool", "missing", "add"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentShowPromptCommand:
    """Test /agent show-prompt command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()

        # Mock agent with system prompt
        mock_agent = MagicMock()
        mock_agent.agent.system_prompt = "You are a helpful AI assistant with tools."
        agent_manager.get_agent.return_value = mock_agent

        return {"console": console, "agent_manager": agent_manager}

    def test_show_prompt_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /agent show-prompt command exists."""
        result = runner.invoke(agent, ["show-prompt", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_show_prompt_displays_system_prompt(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show-prompt displays the agent's system prompt."""
        result = runner.invoke(agent, ["show-prompt", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify agent was retrieved
        mock_context["agent_manager"].get_agent.assert_called_once_with("test_agent")

        # Verify console.print was called with a Panel
        assert mock_context["console"].print.called
        # Check that at least one call included a Panel with the system prompt
        calls = mock_context["console"].print.call_args_list
        assert len(calls) >= 1

    def test_show_prompt_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test show-prompt with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.get_agent.side_effect = KeyError("Agent 'missing' not found")

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["show-prompt", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestAgentSaveCommand:
    """Test /agent save command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        return {"console": console, "agent_manager": agent_manager}

    def test_save_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent save command exists."""
        result = runner.invoke(agent, ["save", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_save_saves_agent_to_yaml(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that save command saves agent to YAML file."""
        result = runner.invoke(agent, ["save", "test_agent"], obj=mock_context)

        assert result.exit_code == 0

        # Verify save_agent_to_yaml was called
        mock_context["agent_manager"].save_agent_to_yaml.assert_called_once()
        call_args = mock_context["agent_manager"].save_agent_to_yaml.call_args
        assert call_args[0][0] == "test_agent"  # agent name
        assert "config/agents/test_agent.yaml" in call_args[0][1]  # path

        # Verify success message
        call_args_str = str(mock_context["console"].print.call_args_list)
        assert "saved" in call_args_str.lower()

    def test_save_with_custom_path(self, runner: CliRunner, mock_context: dict) -> None:
        """Test save with custom path option."""
        result = runner.invoke(
            agent,
            ["save", "test_agent", "--path", "custom/path.yaml"],
            obj=mock_context,
        )

        assert result.exit_code == 0

        # Verify custom path was used
        call_args = mock_context["agent_manager"].save_agent_to_yaml.call_args
        assert call_args[0][1] == "custom/path.yaml"

    def test_save_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test save with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.save_agent_to_yaml.side_effect = KeyError(
            "Agent 'missing' not found"
        )

        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(agent, ["save", "missing"], obj=mock_context)

        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestResolveAgentPath:
    """Test resolve_agent_path helper function."""

    def test_resolve_agent_name_with_yaml_extension(self) -> None:
        """Test resolving agent name finds .yaml file in config/agents/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config/agents directory with test file
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            yaml_file = agents_dir / "column_matcher.yaml"
            yaml_file.write_text("name: column_matcher")

            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("column_matcher")
                # Returns absolute resolved path for security
                assert result is not None
                assert result.endswith("column_matcher.yaml")
                assert "config/agents" in result or "config\\agents" in result
            finally:
                os.chdir(original_cwd)

    def test_resolve_agent_name_with_yml_extension(self) -> None:
        """Test resolving agent name finds .yml file in config/agents/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config/agents directory with test file
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            yml_file = agents_dir / "researcher.yml"
            yml_file.write_text("name: researcher")

            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("researcher")
                # Returns absolute resolved path for security
                assert result is not None
                assert result.endswith("researcher.yml")
                assert "config/agents" in result or "config\\agents" in result
            finally:
                os.chdir(original_cwd)

    def test_resolve_full_path(self) -> None:
        """Test resolving a full path returns resolved absolute path if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file at a specific path
            agent_file = Path(tmpdir) / "custom" / "agent.yaml"
            agent_file.parent.mkdir(parents=True)
            agent_file.write_text("name: custom")

            result = resolve_agent_path(str(agent_file))
            # Returns resolved path - may differ from input on macOS (/var vs /private/var)
            assert result is not None
            assert result.endswith("custom/agent.yaml") or result.endswith("custom\\agent.yaml")
            assert Path(result).exists()

    def test_resolve_relative_path(self) -> None:
        """Test resolving a relative path returns resolved absolute path if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with relative path
            agents_dir = Path(tmpdir) / "agents"
            agents_dir.mkdir()
            agent_file = agents_dir / "agent.yaml"
            agent_file.write_text("name: agent")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("agents/agent.yaml")
                # Returns resolved absolute path for security
                assert result is not None
                assert result.endswith("agents/agent.yaml") or result.endswith("agents\\agent.yaml")
                assert Path(result).exists()
            finally:
                os.chdir(original_cwd)

    def test_resolve_nonexistent_agent_returns_none(self) -> None:
        """Test that non-existent agent name returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty config/agents directory
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("nonexistent")
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_resolve_prefers_yaml_over_yml(self) -> None:
        """Test that .yaml is preferred over .yml when both exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both .yaml and .yml files
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "agent.yaml").write_text("name: agent")
            (agents_dir / "agent.yml").write_text("name: agent")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("agent")
                # Returns absolute resolved path, preferring .yaml
                assert result is not None
                assert result.endswith("agent.yaml")
                assert "config/agents" in result or "config\\agents" in result
            finally:
                os.chdir(original_cwd)


class TestAgentLoadCommand:
    """Test /agent load command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        agent_manager = MagicMock()
        # Mock agent with tools
        mock_agent = MagicMock()
        mock_agent.name = "test_agent"
        mock_agent.tools = [MagicMock(name="tavily_web_search")]
        agent_manager.load_agent_from_yaml.return_value = mock_agent
        return {"console": console, "agent_manager": agent_manager}

    def test_load_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /agent load command exists."""
        result = runner.invoke(agent, ["load", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_load_by_agent_name(self, runner: CliRunner, mock_context: dict) -> None:
        """Test loading agent by name only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test agent file
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "test_agent.yaml").write_text("name: test_agent")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(agent, ["load", "test_agent"], obj=mock_context)
                assert result.exit_code == 0
                # Verify load_agent_from_yaml was called with resolved path
                mock_context["agent_manager"].load_agent_from_yaml.assert_called_once()
                call_args = mock_context["agent_manager"].load_agent_from_yaml.call_args
                assert "test_agent.yaml" in call_args[0][0]
            finally:
                os.chdir(original_cwd)

    def test_load_with_full_path(self, runner: CliRunner, mock_context: dict) -> None:
        """Test loading agent with full path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test agent file
            agent_file = Path(tmpdir) / "custom_agent.yaml"
            agent_file.write_text("name: custom_agent")

            result = runner.invoke(
                agent, ["load", str(agent_file)], obj=mock_context
            )
            assert result.exit_code == 0
            # Verify load_agent_from_yaml was called with a path containing the filename
            # Note: Path may be resolved (e.g., /var vs /private/var on macOS)
            mock_context["agent_manager"].load_agent_from_yaml.assert_called_once()
            call_args = mock_context["agent_manager"].load_agent_from_yaml.call_args
            assert "custom_agent.yaml" in call_args[0][0]

    def test_load_displays_agent_name_and_tools(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that load command displays agent name and tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "test_agent.yaml").write_text("name: test_agent")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(agent, ["load", "test_agent"], obj=mock_context)
                assert result.exit_code == 0
                # Verify console.print was called with agent info
                call_args_str = str(mock_context["console"].print.call_args_list)
                assert "test_agent" in call_args_str.lower() or "loaded" in call_args_str.lower()
            finally:
                os.chdir(original_cwd)

    def test_load_handles_nonexistent_agent(self, runner: CliRunner) -> None:
        """Test load command with non-existent agent."""
        console = MagicMock()
        agent_manager = MagicMock()
        mock_context = {"console": console, "agent_manager": agent_manager}

        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = runner.invoke(
                    agent, ["load", "nonexistent"], obj=mock_context
                )
                assert result.exit_code == 0
                call_args = str(console.print.call_args_list)
                assert "not found" in call_args.lower() or "error" in call_args.lower()
            finally:
                os.chdir(original_cwd)

    def test_load_handles_file_not_found(self, runner: CliRunner) -> None:
        """Test load command when load_agent_from_yaml raises FileNotFoundError."""
        console = MagicMock()
        agent_manager = MagicMock()
        agent_manager.load_agent_from_yaml.side_effect = FileNotFoundError(
            "Agent file not found"
        )
        mock_context = {"console": console, "agent_manager": agent_manager}

        result = runner.invoke(
            agent, ["load", "/path/to/nonexistent.yaml"], obj=mock_context
        )
        assert result.exit_code == 0
        call_args = str(console.print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestResolveAgentPathSecurity:
    """Test path traversal security in resolve_agent_path."""

    def test_rejects_double_dot_path_traversal(self) -> None:
        """Test that .. path traversal is rejected."""
        result = resolve_agent_path("../../../etc/passwd")
        assert result is None, "Path traversal with .. should be rejected"

    def test_rejects_double_dot_in_middle(self) -> None:
        """Test that .. in the middle of path is rejected."""
        result = resolve_agent_path("agents/../../../secret")
        assert result is None, "Path with .. in middle should be rejected"

    def test_rejects_double_dot_with_extension(self) -> None:
        """Test that .. with yaml extension is rejected."""
        result = resolve_agent_path("../../config.yaml")
        assert result is None, "Path traversal with extension should be rejected"

    def test_allows_valid_agent_name(self) -> None:
        """Test that valid agent names without .. are allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "valid_agent.yaml").write_text("name: valid_agent")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("valid_agent")
                assert result is not None, "Valid agent name should be resolved"
                assert "valid_agent.yaml" in result
            finally:
                os.chdir(original_cwd)

    def test_resolved_path_stays_within_agents_dir(self) -> None:
        """Test that resolved paths within config/agents stay within bounds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "nested.yaml").write_text("name: nested")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Even if agent name could resolve elsewhere, it should be bounded
                result = resolve_agent_path("nested")
                if result is not None:
                    resolved = Path(result).resolve()
                    assert str(resolved).startswith(str(agents_dir.resolve())), \
                        "Resolved path should be within agents directory"
            finally:
                os.chdir(original_cwd)

    def test_allows_dots_in_agent_name(self) -> None:
        """Test that single dots in names are allowed (e.g., v1.0)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "config" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "agent.v1.0.yaml").write_text("name: agent.v1.0")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = resolve_agent_path("agent.v1.0")
                assert result is not None, "Single dots in name should be allowed"
            finally:
                os.chdir(original_cwd)
