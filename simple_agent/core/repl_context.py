"""Context factory for cli_repl_kit integration.

This module provides a context factory function that bridges simple_agent's
manager classes to cli_repl_kit's context pattern. Managers are lazily
initialized on first access and shared across all commands.
"""

import logging
import os
from typing import Any, Callable, Dict, Optional

from rich.console import Console

logger = logging.getLogger(__name__)


def create_context_factory(
    console: Console,
    config: Dict[str, Any],
    config_file: str,
    debug_level: str,
) -> Callable[[], Dict[str, Any]]:
    """Create a context factory function for cli_repl_kit.

    The factory returns a callable that initializes managers lazily on first
    call and returns the same instances on subsequent calls. This matches
    the ctx.obj pattern used by Click commands.

    Args:
        console: Rich console instance for output
        config: Configuration dictionary
        config_file: Path to the config file
        debug_level: Debug level string ("off", "info", "debug")

    Returns:
        A callable that returns a dict compatible with ctx.obj
    """
    # Cache for initialized managers
    _cache: Dict[str, Any] = {}
    _initialized = False

    def context_factory() -> Dict[str, Any]:
        """Create or return cached context dict with managers."""
        nonlocal _initialized

        if not _initialized:
            _initialize_managers()
            _initialized = True

        return {
            "console": console,
            "config": config,
            "config_file": config_file,
            "debug_level": debug_level,
            "agent_manager": _cache.get("agent_manager"),
            "tool_manager": _cache.get("tool_manager"),
            "flow_manager": _cache.get("flow_manager"),
            "collection_manager": _cache.get("collection_manager"),
            "collections_dir": _cache.get("collections_dir"),
        }

    def _initialize_managers() -> None:
        """Initialize all managers (called once on first context access)."""
        # Import here to avoid circular imports
        from simple_agent.core.agent_manager import AgentManager
        from simple_agent.core.config_manager import ConfigManager
        from simple_agent.core.tool_manager import ToolManager
        from simple_agent.orchestration.flow_manager import FlowManager

        logger.info("Initializing managers for REPL context")

        # Initialize ToolManager
        logger.debug("Loading tool manager")
        tool_manager = ToolManager(auto_load_builtin=True)
        _cache["tool_manager"] = tool_manager

        # Initialize AgentManager
        logger.debug("Loading agent manager")
        agent_manager = AgentManager(config)
        agent_manager.tool_manager = tool_manager
        _cache["agent_manager"] = agent_manager

        # Load agents from config
        logger.debug("Loading agents from config")
        agent_manager._load_agents_from_config()

        # Auto-load agents from directory if enabled
        auto_load_agents = ConfigManager.get(
            config, "agents.auto_load_from_directory", True
        )
        if auto_load_agents:
            agents_dir = "config/agents"
            if os.path.exists(agents_dir):
                count = agent_manager.load_agents_from_directory(agents_dir)
                if count > 0:
                    logger.info(f"Auto-loaded {count} agents from {agents_dir}")
            else:
                logger.debug(f"Agents directory not found: {agents_dir}")

        # Collection manager - lazy loaded (None initially)
        _cache["collection_manager"] = None
        _cache["collections_dir"] = ConfigManager.get(
            config, "rag.collections_dir", "./chroma_db"
        )

        # Initialize FlowManager
        logger.debug("Loading flow manager")
        flows_dir = ConfigManager.get(
            config, "orchestration.flows_dir", "config/flows"
        )
        flow_manager = FlowManager(
            agent_manager=agent_manager, flows_dir=flows_dir
        )
        _cache["flow_manager"] = flow_manager

        logger.info("Manager initialization complete")

    return context_factory


def get_collection_manager(context: Dict[str, Any]) -> Optional[Any]:
    """Lazily initialize and return CollectionManager.

    This function should be called by commands that need the CollectionManager.
    It initializes the manager on first call and caches it in the context.

    Args:
        context: Context dict from context_factory

    Returns:
        CollectionManager instance or None if initialization fails
    """
    if context.get("collection_manager") is not None:
        return context["collection_manager"]

    try:
        from simple_agent.rag.collection_manager import CollectionManager

        collections_dir = context.get("collections_dir", "./chroma_db")
        collection_manager = CollectionManager(persist_directory=collections_dir)
        context["collection_manager"] = collection_manager
        logger.info(f"Initialized CollectionManager with dir: {collections_dir}")
        return collection_manager
    except Exception as e:
        logger.error(f"Failed to initialize CollectionManager: {e}")
        return None
