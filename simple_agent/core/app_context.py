"""AppContext dataclass for application context management.

Replaces the service locator anti-pattern (ctx.obj as dict) with a strongly-typed
dataclass providing IDE autocomplete, type safety, and clear dependencies.

Issue 10-B resolution: Improves testability and dependency injection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from rich.console import Console


@dataclass
class AppContext:
    """Strongly-typed application context for dependency injection.

    Replaces ctx.obj dict-based service locator with type-safe dataclass.
    All dependencies are explicit and type-hinted, improving IDE support
    and testability.

    Attributes:
        console: Rich console for output rendering
        config: Application configuration dict (loaded from YAML)
        config_file: Path to config file
        debug_level: Debug level ("off", "info", or "debug")
        tool_manager: ToolManager instance for managing agents' tools
        agent_manager: AgentManager instance for managing agents
        collection_manager: CollectionManager instance for RAG collections
        flow_manager: FlowManager instance for multi-agent orchestration
    """

    console: Console
    config: Dict[str, Any] = field(default_factory=dict)
    config_file: str = ""
    debug_level: str = "info"
    tool_manager: Optional[Any] = None  # Avoid circular import
    agent_manager: Optional[Any] = None  # Avoid circular import
    collection_manager: Optional[Any] = None  # Avoid circular import
    flow_manager: Optional[Any] = None  # Avoid circular import

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dict for backward compatibility with Click.

        Returns:
            Dict representation of context (suitable for ctx.obj)
        """
        return {
            "console": self.console,
            "config": self.config,
            "config_file": self.config_file,
            "debug_level": self.debug_level,
            "tool_manager": self.tool_manager,
            "agent_manager": self.agent_manager,
            "collection_manager": self.collection_manager,
            "flow_manager": self.flow_manager,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppContext":
        """Create AppContext from dict (for backward compatibility).

        Args:
            data: Dict with context values (from ctx.obj)

        Returns:
            AppContext instance with values from dict
        """
        return cls(
            console=data.get("console") or Console(),
            config=data.get("config", {}),
            config_file=data.get("config_file", ""),
            debug_level=data.get("debug_level", "info"),
            tool_manager=data.get("tool_manager"),
            agent_manager=data.get("agent_manager"),
            collection_manager=data.get("collection_manager"),
            flow_manager=data.get("flow_manager"),
        )
