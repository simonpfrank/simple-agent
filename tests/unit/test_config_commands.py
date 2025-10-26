"""
Unit tests for /config commands (Phase 1.3).

Tests the configuration management commands including get, reset, and paths.
"""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from simple_agent.commands.config_commands import config


class TestConfigGetCommand:
    """Test /config get command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        config_dict = {
            "llm": {"provider": "openai", "temperature": 0.7},
            "agents": {"default": {"max_steps": 10}},
        }
        return {"console": console, "config": config_dict}

    def test_get_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /config get command exists."""
        result = runner.invoke(config, ["get", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_get_retrieves_simple_value(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test getting a simple config value."""
        result = runner.invoke(
            config, ["get", "--key", "llm.provider"], obj=mock_context
        )

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()

        # Verify the value was displayed
        call_args = str(mock_context["console"].print.call_args_list)
        assert "openai" in call_args.lower()

    def test_get_retrieves_nested_value(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test getting a nested config value."""
        result = runner.invoke(
            config, ["get", "--key", "agents.default.max_steps"], obj=mock_context
        )

        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "10" in call_args

    def test_get_handles_missing_key(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test getting a non-existent config key."""
        result = runner.invoke(
            config, ["get", "--key", "nonexistent.key"], obj=mock_context
        )

        # Should not crash, but should show error or "not found" message
        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestConfigResetCommand:
    """Test /config reset command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        # Config with overridden value
        config_dict = {
            "llm": {
                "provider": "openai",
                "temperature": 0.9,
            }  # Overridden from default 0.7
        }
        return {"console": console, "config": config_dict}

    def test_reset_command_exists(self, runner: CliRunner, mock_context: dict) -> None:
        """Test that /config reset command exists."""
        result = runner.invoke(config, ["reset", "--help"], obj=mock_context)
        assert result.exit_code == 0

    @patch("simple_agent.commands.config_commands.ConfigManager.get_defaults")
    def test_reset_restores_default_value(
        self,
        mock_get_defaults: MagicMock,
        runner: CliRunner,
        mock_context: dict,
    ) -> None:
        """Test that reset restores the default value."""
        # Setup mock defaults
        mock_get_defaults.return_value = {
            "llm": {"provider": "openai", "temperature": 0.7}
        }

        # Verify current value is overridden
        assert mock_context["config"]["llm"]["temperature"] == 0.9

        result = runner.invoke(
            config, ["reset", "--key", "llm.temperature"], obj=mock_context
        )

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()

        # Verify reset message was shown
        call_args = str(mock_context["console"].print.call_args_list)
        assert "reset" in call_args.lower() or "default" in call_args.lower()

    def test_reset_handles_missing_key(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test resetting a non-existent config key."""
        result = runner.invoke(
            config, ["reset", "--key", "nonexistent.key"], obj=mock_context
        )

        # Should show error
        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "not found" in call_args.lower() or "error" in call_args.lower()


class TestConfigSetPathCommand:
    """Test /config set-path command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        config_dict = {
            "paths": {
                "prompts": "config/prompts/",
                "tools": "tools/",
                "agents": "config/agents/",
                "logs": "logs/",
            }
        }
        return {"console": console, "config": config_dict}

    def test_set_path_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /config set-path command exists."""
        result = runner.invoke(config, ["set-path", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_set_path_updates_prompts_path(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test setting prompts path."""
        result = runner.invoke(
            config,
            ["set-path", "--type", "prompts", "--path", "custom/prompts/"],
            obj=mock_context,
        )

        assert result.exit_code == 0
        assert mock_context["config"]["paths"]["prompts"] == "custom/prompts/"

        # Verify success message
        call_args = str(mock_context["console"].print.call_args_list)
        assert "prompts" in call_args.lower()

    def test_set_path_updates_tools_path(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test setting tools path."""
        result = runner.invoke(
            config,
            ["set-path", "--type", "tools", "--path", "my_tools/"],
            obj=mock_context,
        )

        assert result.exit_code == 0
        assert mock_context["config"]["paths"]["tools"] == "my_tools/"

    def test_set_path_handles_invalid_type(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test setting path with invalid type."""
        result = runner.invoke(
            config,
            ["set-path", "--type", "invalid_type", "--path", "some/path/"],
            obj=mock_context,
        )

        # Should show error for invalid path type
        assert result.exit_code == 0
        call_args = str(mock_context["console"].print.call_args_list)
        assert "invalid" in call_args.lower() or "error" in call_args.lower()

    def test_set_path_initializes_paths_if_missing(self, runner: CliRunner) -> None:
        """Test that set-path creates paths section if it doesn't exist."""
        console = MagicMock()
        config_dict = {}  # No paths section
        mock_context = {"console": console, "config": config_dict}

        result = runner.invoke(
            config,
            ["set-path", "--type", "prompts", "--path", "new/prompts/"],
            obj=mock_context,
        )

        assert result.exit_code == 0
        assert "paths" in config_dict
        assert config_dict["paths"]["prompts"] == "new/prompts/"


class TestConfigShowPathsCommand:
    """Test /config show-paths command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self) -> dict:
        """Create mock context object."""
        console = MagicMock()
        config_dict = {
            "paths": {
                "prompts": "config/prompts/",
                "tools": "tools/",
                "agents": "config/agents/",
                "logs": "logs/",
            }
        }
        return {"console": console, "config": config_dict}

    def test_show_paths_command_exists(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that /config show-paths command exists."""
        result = runner.invoke(config, ["show-paths", "--help"], obj=mock_context)
        assert result.exit_code == 0

    def test_show_paths_displays_all_paths(
        self, runner: CliRunner, mock_context: dict
    ) -> None:
        """Test that show-paths displays all configured paths."""
        result = runner.invoke(config, ["show-paths"], obj=mock_context)

        assert result.exit_code == 0
        mock_context["console"].print.assert_called()

        # Verify all paths are shown
        call_args = str(mock_context["console"].print.call_args_list)
        assert "prompts" in call_args.lower()
        assert "tools" in call_args.lower()
        assert "agents" in call_args.lower()
        assert "logs" in call_args.lower()

    def test_show_paths_handles_missing_paths_section(self, runner: CliRunner) -> None:
        """Test show-paths when paths section doesn't exist."""
        console = MagicMock()
        config_dict = {}  # No paths section
        mock_context = {"console": console, "config": config_dict}

        result = runner.invoke(config, ["show-paths"], obj=mock_context)

        assert result.exit_code == 0
        # Should show message about no paths configured or show defaults
        mock_context["console"].print.assert_called()
