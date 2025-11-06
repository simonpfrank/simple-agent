"""
Integration tests for commands.
These tests demonstrate testing commands programmatically without UI interaction.
"""

from click.testing import CliRunner

from simple_agent.app import cli


class TestConfigCommands:
    """Tests for config commands."""

    def test_config_show(self, tmp_path):
        """Test config show command."""
        runner = CliRunner()
        
        # Create minimal valid config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
""")

        # Run config show command
        result = runner.invoke(cli, ["--config", str(config_file), "config", "show"])

        # Should succeed
        assert result.exit_code == 0, f"Failed with: {result.output}"
        assert "Configuration" in result.output or "provider" in result.output

    def test_config_save_and_load(self, tmp_path):
        """Test config save and load commands."""
        runner = CliRunner()
        
        # Create initial config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test App"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
""")
        
        save_file = tmp_path / "saved_config.yaml"

        # Save config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "save", "--file", str(save_file)])
        assert result.exit_code == 0, f"Save failed with: {result.output}"
        assert save_file.exists()

        # Load config
        result = runner.invoke(cli, ["--config", str(save_file), "config", "show"])
        assert result.exit_code == 0, f"Load failed with: {result.output}"


class TestSystemCommands:
    """Tests for system commands."""

    def test_help_command(self, tmp_path):
        """Test help command."""
        runner = CliRunner()

        # Test --help flag (doesn't require config)
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, f"Failed with: {result.output}"
        # Just verify it shows usage info
        assert "Usage:" in result.output or "Options:" in result.output

        # Test subcommand help (CLI loads config first, so need a valid one)
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  name: "Test"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "INFO"
  file: "test.log"
""")
        result = runner.invoke(cli, ["--config", str(config_file), "config", "--help"])
        assert result.exit_code == 0, f"Failed with: {result.output}"
        assert "Usage:" in result.output or "config" in result.output.lower()


class TestCLIMode:
    """Tests for CLI mode behavior."""

    def test_cli_with_config_file(self, tmp_path):
        """Test running CLI with custom config file."""
        runner = CliRunner()

        # Create custom config with all required fields
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
app:
  name: "Test App"
  version: "1.0"
paths:
  data_dir: "./data"
  logs_dir: "./logs"
  prompts: "./prompts"
  tools: "./tools"
llm:
  provider: "openai"
agents:
  default:
    role: "Test"
logging:
  level: "DEBUG"
  file: "test.log"
""")

        # Run with custom config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "show"])

        assert result.exit_code == 0, f"Failed with: {result.output}"

    def test_cli_without_config_file(self):
        """Test running CLI without config file (uses defaults)."""
        runner = CliRunner()

        # Run with non-existent config (should use defaults)
        result = runner.invoke(cli, ["--config", "nonexistent.yaml", "config", "show"])

        # Should still work with defaults
        assert result.exit_code == 0
