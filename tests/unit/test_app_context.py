"""Unit tests for AppContext dataclass."""

from rich.console import Console

from simple_agent.core.app_context import AppContext


class TestAppContextInitialization:
    """Test AppContext initialization."""

    def test_app_context_with_console_only(self):
        """Test creating AppContext with just console."""
        console = Console()
        ctx = AppContext(console=console)

        assert ctx.console is console
        assert ctx.config == {}
        assert ctx.config_file == ""
        assert ctx.debug_level == "info"
        assert ctx.tool_manager is None
        assert ctx.agent_manager is None
        assert ctx.collection_manager is None
        assert ctx.flow_manager is None

    def test_app_context_with_all_fields(self):
        """Test creating AppContext with all fields."""
        console = Console()
        config = {"llm": {"provider": "openai"}}
        tool_manager = "mock_tool_manager"
        agent_manager = "mock_agent_manager"

        ctx = AppContext(
            console=console,
            config=config,
            config_file="config.yaml",
            debug_level="debug",
            tool_manager=tool_manager,
            agent_manager=agent_manager,
        )

        assert ctx.console is console
        assert ctx.config == config
        assert ctx.config_file == "config.yaml"
        assert ctx.debug_level == "debug"
        assert ctx.tool_manager == tool_manager
        assert ctx.agent_manager == agent_manager

    def test_app_context_defaults(self):
        """Test AppContext default values."""
        console = Console()
        ctx = AppContext(console=console)

        assert ctx.config == {}
        assert ctx.config_file == ""
        assert ctx.debug_level == "info"
        assert ctx.tool_manager is None
        assert ctx.agent_manager is None
        assert ctx.collection_manager is None
        assert ctx.flow_manager is None


class TestAppContextToDictConversion:
    """Test conversion to dict for backward compatibility."""

    def test_to_dict_with_minimal_context(self):
        """Test to_dict with minimal context."""
        console = Console()
        ctx = AppContext(console=console)

        result = ctx.to_dict()

        assert isinstance(result, dict)
        assert result["console"] is console
        assert result["config"] == {}
        assert result["config_file"] == ""
        assert result["debug_level"] == "info"
        assert result["tool_manager"] is None

    def test_to_dict_with_full_context(self):
        """Test to_dict with full context."""
        console = Console()
        config = {"llm": {"provider": "openai"}}
        tool_manager = "mock_tool_manager"
        agent_manager = "mock_agent_manager"
        collection_manager = "mock_collection_manager"
        flow_manager = "mock_flow_manager"

        ctx = AppContext(
            console=console,
            config=config,
            config_file="config.yaml",
            debug_level="debug",
            tool_manager=tool_manager,
            agent_manager=agent_manager,
            collection_manager=collection_manager,
            flow_manager=flow_manager,
        )

        result = ctx.to_dict()

        assert result["console"] is console
        assert result["config"] == config
        assert result["config_file"] == "config.yaml"
        assert result["debug_level"] == "debug"
        assert result["tool_manager"] == tool_manager
        assert result["agent_manager"] == agent_manager
        assert result["collection_manager"] == collection_manager
        assert result["flow_manager"] == flow_manager


class TestAppContextFromDictConversion:
    """Test creation from dict."""

    def test_from_dict_minimal(self):
        """Test from_dict with minimal dict."""
        console = Console()
        data = {"console": console}

        ctx = AppContext.from_dict(data)

        assert ctx.console is console
        assert ctx.config == {}
        assert ctx.config_file == ""

    def test_from_dict_with_all_fields(self):
        """Test from_dict with all fields."""
        console = Console()
        config = {"llm": {"provider": "openai"}}
        tool_manager = "mock_tool_manager"
        agent_manager = "mock_agent_manager"

        data = {
            "console": console,
            "config": config,
            "config_file": "config.yaml",
            "debug_level": "debug",
            "tool_manager": tool_manager,
            "agent_manager": agent_manager,
        }

        ctx = AppContext.from_dict(data)

        assert ctx.console is console
        assert ctx.config == config
        assert ctx.config_file == "config.yaml"
        assert ctx.debug_level == "debug"
        assert ctx.tool_manager == tool_manager
        assert ctx.agent_manager == agent_manager

    def test_from_dict_missing_fields(self):
        """Test from_dict with missing optional fields."""
        console = Console()
        data = {"console": console}  # Only console, missing other fields

        ctx = AppContext.from_dict(data)

        # Should not raise, use defaults
        assert ctx.console is console
        assert ctx.config == {}
        assert ctx.debug_level == "info"
        assert ctx.tool_manager is None


class TestAppContextRoundTrip:
    """Test round-trip conversion (dataclass -> dict -> dataclass)."""

    def test_round_trip_conversion(self):
        """Test that context survives round-trip conversion."""
        console = Console()
        config = {"llm": {"provider": "openai"}, "debug": {"level": "debug"}}
        tool_manager = "mock_tool_manager"
        agent_manager = "mock_agent_manager"

        # Create original context
        original = AppContext(
            console=console,
            config=config,
            config_file="config.yaml",
            debug_level="debug",
            tool_manager=tool_manager,
            agent_manager=agent_manager,
        )

        # Convert to dict and back
        as_dict = original.to_dict()
        restored = AppContext.from_dict(as_dict)

        # Verify all fields match
        assert restored.console is original.console
        assert restored.config == original.config
        assert restored.config_file == original.config_file
        assert restored.debug_level == original.debug_level
        assert restored.tool_manager == original.tool_manager
        assert restored.agent_manager == original.agent_manager
