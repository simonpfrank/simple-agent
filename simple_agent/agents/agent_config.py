"""Configuration dataclass for SimpleAgent initialization.

Encapsulates all agent parameters to reduce constructor complexity
and improve testability (Issue 1-A from code review).
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


@dataclass
class AgentConfig:
    """Configuration for SimpleAgent initialization.

    Replaces 12+ constructor parameters with a single structured object,
    improving testability, documentation, and maintainability.

    Attributes:
        name: Agent identifier
        model_provider: LLM provider ("openai", "ollama", etc.)
        model_config: Dict with model settings (model, temperature, api_key, etc.)
        role: Optional system prompt/persona for the agent
        tools: Optional list of tool instances to attach to agent
        verbosity: Log verbosity (0=quiet, 1=normal, 2=verbose) - DEPRECATED
        max_steps: Maximum ReAct iterations for agent
        agent_type: Agent type - "tool_calling" (safe) or "code" (requires Docker)
        executor_type: Executor for code agents - "docker", "e2b", "modal", "wasm"
        debug_enabled: Enable verbose debug output and logging (DEPRECATED, use debug_level)
        debug_level: Verbosity level for smolagents ("off", "info", "debug")
        user_prompt_template: Optional template to wrap user input (Jinja2 or format string)
        token_budget: Hard limit on input tokens (prevents rate limits)
        token_warning_threshold: Soft warning threshold before hitting budget
    """

    name: str
    model_provider: Optional[str]
    model_config: Dict[str, Any]
    role: Optional[str] = None
    tools: Optional[list] = None
    verbosity: int = 1
    max_steps: int = 10
    agent_type: Literal["tool_calling", "code"] = "tool_calling"
    executor_type: Literal["docker", "e2b", "modal", "wasm"] = "docker"
    debug_enabled: bool = False
    debug_level: Literal["off", "info", "debug"] = "off"
    user_prompt_template: Optional[str] = None
    token_budget: Optional[int] = None
    token_warning_threshold: Optional[int] = None

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If required parameters are invalid
            TypeError: If parameters have incorrect types
        """
        # Type validation
        if not isinstance(self.name, str):
            raise TypeError(f"name must be a string, got {type(self.name).__name__}")

        if self.model_provider is not None and not isinstance(self.model_provider, str):
            raise TypeError(f"model_provider must be a string or None, got {type(self.model_provider).__name__}")

        if not isinstance(self.model_config, dict):
            raise TypeError(f"model_config must be a dict, got {type(self.model_config).__name__}")

        # Value validation
        if not isinstance(self.max_steps, int) or self.max_steps <= 0:
            raise ValueError(f"max_steps must be a positive integer, got {self.max_steps}")

        if self.token_budget is not None and (not isinstance(self.token_budget, int) or self.token_budget < 0):
            raise ValueError(f"token_budget must be a non-negative integer or None, got {self.token_budget}")

        if self.token_warning_threshold is not None and (not isinstance(self.token_warning_threshold, int) or self.token_warning_threshold < 0):
            raise ValueError(f"token_warning_threshold must be a non-negative integer or None, got {self.token_warning_threshold}")

        # Agent type validation
        valid_agent_types = ["tool_calling", "code"]
        if self.agent_type not in valid_agent_types:
            raise ValueError(f"Invalid agent_type '{self.agent_type}'. Must be one of: {valid_agent_types}")

        # Security: Reject 'local' executor for CodeAgent
        if self.agent_type == "code" and self.executor_type == "local":
            raise ValueError(
                "Security error: 'local' executor is unsafe and not allowed. "
                "Use 'docker' (recommended), 'e2b', 'modal', or 'wasm' instead."
            )

    @classmethod
    def from_kwargs(cls, **kwargs) -> "AgentConfig":
        """Create AgentConfig from keyword arguments.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Validated AgentConfig instance

        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters have incorrect types
        """
        config = cls(**kwargs)
        config.validate()
        return config
