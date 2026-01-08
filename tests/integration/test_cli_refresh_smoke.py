"""
Smoke tests for CLI implementation (cli_repl_kit integration).

These tests verify that the REPL can initialize with cli_repl_kit
without crashing. Visual testing of colors and spacing must be done manually.
"""

import pytest
from pathlib import Path


def test_app_imports_successfully():
    """Test that app.py imports without errors."""
    try:
        from simple_agent.app import main
        assert main is not None
    except Exception as e:
        pytest.fail(f"Failed to import app.py: {e}")


def test_cli_repl_kit_imports_successfully():
    """Test that cli_repl_kit imports correctly from submodule."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simple_agent" / "lib" / "cli_repl_kit"))

    try:
        from cli_repl_kit import REPL, CommandPlugin
        assert REPL is not None
        assert CommandPlugin is not None
    except Exception as e:
        pytest.fail(f"Failed to import cli_repl_kit: {e}")


def test_core_commands_plugin_imports():
    """Test that CoreCommandsPlugin can be imported."""
    try:
        from simple_agent.plugins.core_commands import CoreCommandsPlugin
        assert CoreCommandsPlugin is not None
    except Exception as e:
        pytest.fail(f"Failed to import CoreCommandsPlugin: {e}")


def test_context_factory_imports():
    """Test that context factory can be imported."""
    try:
        from simple_agent.core.repl_context import create_context_factory
        assert create_context_factory is not None
    except Exception as e:
        pytest.fail(f"Failed to import create_context_factory: {e}")


def test_history_directory_creation():
    """Test that history directory path is valid."""
    from pathlib import Path

    history_file = Path.home() / ".simple-agent" / "history"
    # Directory should be created by app startup, but we just verify the path is valid
    assert history_file.parent.name == ".simple-agent"
    assert history_file.name == "history"


def test_config_has_ui_prompt_setting():
    """Test that config.yaml has the ui.prompt setting."""
    import yaml
    from pathlib import Path

    config_path = Path("config.yaml")
    if not config_path.exists():
        pytest.skip("config.yaml not found")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Verify ui.prompt setting exists
    assert 'ui' in config, "ui section missing from config.yaml"
    assert 'prompt' in config['ui'], "ui.prompt setting missing from config.yaml"
    assert isinstance(config['ui']['prompt'], str), "ui.prompt should be a string"


def test_repl_config_exists():
    """Test that repl_config.yaml exists for cli_repl_kit."""
    config_path = Path(__file__).parent.parent.parent / "simple_agent" / "repl_config.yaml"
    assert config_path.exists(), "repl_config.yaml not found"


def test_common_has_app_theme():
    """Test that APP_THEME is available in commands/common.py."""
    try:
        from simple_agent.commands.common import APP_THEME, SYMBOLS
        assert APP_THEME is not None
        assert SYMBOLS is not None
    except Exception as e:
        pytest.fail(f"Failed to import APP_THEME from common.py: {e}")


# Note: Visual tests (menu colors, spacing, grey lines) must be done manually
# Run the REPL and verify:
# - Purple background (#6B4FBB) on selected menu items
# - White text on unselected items
# - Grey horizontal line below input area
# - Ctrl+J inserts newline
