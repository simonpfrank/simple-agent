"""
Integration tests for commands.
These tests demonstrate testing commands programmatically without UI interaction.
"""

from click.testing import CliRunner

from repl_cli_template.app import cli


class TestConfigCommands:
    """Tests for config commands."""

    def test_config_show(self):
        """Test config show command."""
        runner = CliRunner()

        # Run config show command
        result = runner.invoke(cli, ["config", "show"])

        # Should succeed
        assert result.exit_code == 0
        assert "Configuration" in result.output

    def test_config_save_and_load(self, tmp_path):
        """Test config save and load commands."""
        runner = CliRunner()
        config_file = tmp_path / "test_config.yaml"

        # Save config
        result = runner.invoke(cli, ["config", "save", "--file", str(config_file)])
        assert result.exit_code == 0
        assert config_file.exists()

        # Load config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "show"])
        assert result.exit_code == 0


class TestProcessCommand:
    """Tests for process command."""

    def test_process_command_success(self, tmp_path):
        """Test process command with valid input."""
        runner = CliRunner()

        # Create test input file
        input_file = tmp_path / "input.txt"
        input_file.write_text("test data\n")

        # Run process command
        result = runner.invoke(cli, ["process", "--input", str(input_file)])

        # Should succeed
        assert result.exit_code == 0
        assert "Success" in result.output or "success" in result.output.lower()

    def test_process_command_file_not_found(self):
        """Test process command with non-existent file."""
        runner = CliRunner()

        # Run with non-existent file
        result = runner.invoke(cli, ["process", "--input", "nonexistent.txt"])

        # Should fail
        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output.lower()


class TestSystemCommands:
    """Tests for system commands."""

    def test_help_command(self):
        """Test help command."""
        runner = CliRunner()

        # Test --help flag
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "REPL/CLI Template" in result.output

        # Test help command (in CLI mode with a dummy subcommand context)
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0


class TestCLIMode:
    """Tests for CLI mode behavior."""

    def test_cli_with_config_file(self, tmp_path):
        """Test running CLI with custom config file."""
        runner = CliRunner()

        # Create custom config
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
app:
  name: "Test App"
logging:
  level: "DEBUG"
        """)

        # Run with custom config
        result = runner.invoke(cli, ["--config", str(config_file), "config", "show"])

        assert result.exit_code == 0
        assert "Test App" in result.output

    def test_cli_without_config_file(self):
        """Test running CLI without config file (uses defaults)."""
        runner = CliRunner()

        # Run with non-existent config (should use defaults)
        result = runner.invoke(cli, ["--config", "nonexistent.yaml", "config", "show"])

        # Should still work with defaults
        assert result.exit_code == 0
