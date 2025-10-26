"""
Unit tests for ToolManager (Phase 1.4).

Tests the tool management system including registration, retrieval, and listing.
"""

from unittest.mock import MagicMock

import pytest

from simple_agent.core.tool_manager import ToolManager


class TestToolManagerInit:
    """Test ToolManager initialization."""

    def test_init_creates_empty_registry(self) -> None:
        """Test that ToolManager initializes with empty tool registry."""
        manager = ToolManager()

        assert manager.tools == {}
        assert manager.list_tools() == []

    def test_init_loads_builtin_tools(self) -> None:
        """Test that ToolManager can auto-load built-in tools."""
        manager = ToolManager(auto_load_builtin=True)

        # Should have loaded calculator tools
        tools = manager.list_tools()
        assert len(tools) > 0


class TestToolManagerRegister:
    """Test tool registration."""

    def test_register_tool(self) -> None:
        """Test registering a single tool."""
        manager = ToolManager()
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"

        manager.register_tool(mock_tool)

        assert "test_tool" in manager.tools
        assert manager.get_tool("test_tool") == mock_tool

    def test_register_multiple_tools(self) -> None:
        """Test registering multiple tools."""
        manager = ToolManager()

        tool1 = MagicMock()
        tool1.name = "tool1"
        tool2 = MagicMock()
        tool2.name = "tool2"

        manager.register_tool(tool1)
        manager.register_tool(tool2)

        assert len(manager.list_tools()) == 2
        assert "tool1" in manager.list_tools()
        assert "tool2" in manager.list_tools()

    def test_register_duplicate_tool_raises_error(self) -> None:
        """Test that registering a duplicate tool name raises error."""
        manager = ToolManager()

        tool1 = MagicMock()
        tool1.name = "duplicate"
        tool2 = MagicMock()
        tool2.name = "duplicate"

        manager.register_tool(tool1)

        with pytest.raises(ValueError, match="already registered"):
            manager.register_tool(tool2)


class TestToolManagerGet:
    """Test tool retrieval."""

    def test_get_tool_success(self) -> None:
        """Test retrieving an existing tool."""
        manager = ToolManager()
        mock_tool = MagicMock()
        mock_tool.name = "my_tool"

        manager.register_tool(mock_tool)
        retrieved = manager.get_tool("my_tool")

        assert retrieved == mock_tool

    def test_get_tool_not_found_raises_error(self) -> None:
        """Test retrieving non-existent tool raises error."""
        manager = ToolManager()

        with pytest.raises(KeyError, match="Tool 'missing' not found"):
            manager.get_tool("missing")

    def test_has_tool(self) -> None:
        """Test checking if tool exists."""
        manager = ToolManager()
        mock_tool = MagicMock()
        mock_tool.name = "exists"

        manager.register_tool(mock_tool)

        assert manager.has_tool("exists") is True
        assert manager.has_tool("missing") is False


class TestToolManagerList:
    """Test tool listing."""

    def test_list_tools_empty(self) -> None:
        """Test listing tools when registry is empty."""
        manager = ToolManager()

        assert manager.list_tools() == []

    def test_list_tools_returns_names(self) -> None:
        """Test list_tools returns tool names."""
        manager = ToolManager()

        tool1 = MagicMock()
        tool1.name = "tool_a"
        tool2 = MagicMock()
        tool2.name = "tool_b"

        manager.register_tool(tool1)
        manager.register_tool(tool2)

        tools = manager.list_tools()
        assert "tool_a" in tools
        assert "tool_b" in tools
        assert len(tools) == 2


class TestToolManagerInfo:
    """Test tool information retrieval."""

    def test_get_tool_info(self) -> None:
        """Test getting detailed info about a tool."""
        manager = ToolManager()

        mock_tool = MagicMock()
        mock_tool.name = "my_tool"
        mock_tool.description = "Does something useful"
        mock_tool.inputs = {"arg1": "str", "arg2": "int"}
        mock_tool.output_type = "str"

        manager.register_tool(mock_tool)
        info = manager.get_tool_info("my_tool")

        assert info["name"] == "my_tool"
        assert info["description"] == "Does something useful"
        assert "inputs" in info
        assert "output_type" in info

    def test_get_tool_info_not_found(self) -> None:
        """Test getting info for non-existent tool."""
        manager = ToolManager()

        with pytest.raises(KeyError, match="Tool 'missing' not found"):
            manager.get_tool_info("missing")


class TestToolManagerUnregister:
    """Test tool unregistration."""

    def test_unregister_tool(self) -> None:
        """Test removing a tool from registry."""
        manager = ToolManager()

        tool = MagicMock()
        tool.name = "removeme"

        manager.register_tool(tool)
        assert manager.has_tool("removeme")

        manager.unregister_tool("removeme")
        assert not manager.has_tool("removeme")

    def test_unregister_nonexistent_tool(self) -> None:
        """Test unregistering a tool that doesn't exist."""
        manager = ToolManager()

        # Should not raise error, just be a no-op
        manager.unregister_tool("doesnt_exist")
