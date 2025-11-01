"""
Tool management for Simple Agent.

Handles tool registration, retrieval, and metadata management.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Manages tool registration and retrieval.

    Provides a central registry for tools that can be used by agents.
    """

    def __init__(self, auto_load_builtin: bool = False):
        """
        Initialize ToolManager.

        Args:
            auto_load_builtin: If True, automatically load built-in tools
        """
        self.tools: Dict[str, Any] = {}
        logger.debug("ToolManager initialized")

        if auto_load_builtin:
            self._load_builtin_tools()

    def register_tool(self, tool: Any) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: Tool object with 'name' attribute

        Raises:
            ValueError: If tool with same name already registered
        """
        tool_name = tool.name

        if tool_name in self.tools:
            raise ValueError(f"Tool '{tool_name}' already registered")

        self.tools[tool_name] = tool
        logger.debug(f"Registered tool: {tool_name}")

    def get_tool(self, name: str) -> Any:
        """
        Retrieve a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool object

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found")

        return self.tools[name]

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool exists in registry.

        Args:
            name: Tool name

        Returns:
            True if tool exists, False otherwise
        """
        return name in self.tools

    def list_tools(self) -> List[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool name strings
        """
        return list(self.tools.keys())

    def get_tool_info(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a tool.

        Args:
            name: Tool name

        Returns:
            Dictionary with tool metadata (name, description, inputs, output_type)

        Raises:
            KeyError: If tool not found
        """
        tool = self.get_tool(name)

        return {
            "name": tool.name,
            "description": getattr(tool, "description", "No description"),
            "inputs": getattr(tool, "inputs", {}),
            "output_type": getattr(tool, "output_type", "unknown"),
        }

    def unregister_tool(self, name: str) -> None:
        """
        Remove a tool from registry.

        Args:
            name: Tool name to remove
        """
        if name in self.tools:
            del self.tools[name]
            logger.debug(f"Unregistered tool: {name}")

    def _load_builtin_tools(self) -> None:
        """
        Load built-in tools from tools/builtin/ directory.

        This dynamically imports and registers all tools decorated with @tool.
        """
        try:
            from simple_agent.tools.builtin import calculator
            from simple_agent.tools.builtin.tavily_search import tavily_web_search
            from simple_agent.tools.builtin.page_fetch import fetch_webpage_markdown

            # Register calculator tools
            tools_to_register = [
                calculator.add,
                calculator.subtract,
                calculator.multiply,
                calculator.divide,
                tavily_web_search,
                fetch_webpage_markdown,
            ]

            for tool in tools_to_register:
                self.register_tool(tool)

            logger.info(f"Loaded {len(tools_to_register)} built-in tools")

        except ImportError as e:
            logger.warning(f"Failed to load built-in tools: {e}")
