"""
SimpleAgent - Thin wrapper around SmolAgents with support for multiple agent types.

Provides a simplified interface for creating and running agents with LiteLLM support.
Supports ToolCallingAgent (default, safe), CodeAgent (with Docker), and MultiStepAgent.
"""

import logging
from typing import Any, Dict, Literal, Optional

from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel
from smolagents.monitoring import LogLevel

from simple_agent.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class SimpleAgent:
    """Thin wrapper around SmolAgents with support for multiple agent types."""

    def __init__(
        self,
        name: str,
        model_provider: str,
        model_config: Dict[str, Any],
        role: Optional[str] = None,
        template: Optional[str] = None,
        tools: Optional[list] = None,
        verbosity: int = 1,
        max_steps: int = 10,
        agent_type: Literal["tool_calling", "code"] = "tool_calling",
        executor_type: Literal["docker", "e2b", "modal", "wasm"] = "docker",
        debug_enabled: bool = False,
    ):
        """
        Initialize agent.

        Args:
            name: Agent identifier
            model_provider: "openai", "ollama", etc.
            model_config: Dict with model settings
            role: Optional system prompt/persona (overrides template)
            template: Optional template name to load from config/prompts/
            tools: List of tool instances
            verbosity: 0=quiet, 1=normal, 2=verbose (DEPRECATED - use debug_enabled)
            max_steps: Max tool call iterations
            agent_type: Agent type - "tool_calling" (safe, default) or "code" (requires Docker)
            executor_type: Executor for code agent - "docker" (default), "e2b", "modal", "wasm"
            debug_enabled: Enable debug mode (verbose output and logging)

        Raises:
            ValueError: If invalid agent_type or attempting to use unsafe executor
        """
        # Validate agent_type
        valid_types = ["tool_calling", "code"]
        if agent_type not in valid_types:
            raise ValueError(
                f"Invalid agent_type '{agent_type}'. Must be one of: {valid_types}"
            )

        # Security: Reject 'local' executor for CodeAgent
        if agent_type == "code" and executor_type == "local":
            raise ValueError(
                "Security error: 'local' executor is unsafe and not allowed. "
                "Use 'docker' (recommended), 'e2b', 'modal', or 'wasm' instead."
            )

        self.name = name
        self.model_provider = model_provider
        self.agent_type = agent_type
        self.debug_enabled = debug_enabled

        # Load template if specified and no explicit role
        if template and not role:
            template_data = ConfigManager.load_prompt_template(template)
            role = template_data.get("system", "")

        self.role = role

        # Create LiteLLM model instance
        self.model = self._create_model(model_provider, model_config)

        # Map debug mode to SmolAgents LogLevel
        # LogLevel: OFF=-1, ERROR=0, INFO=1, DEBUG=2
        verbosity_level = LogLevel.DEBUG if debug_enabled else LogLevel.INFO
        logger.debug(
            f"Agent '{name}' verbosity set to {verbosity_level.name} "
            f"(debug_enabled={debug_enabled})"
        )

        # Create appropriate agent type
        if agent_type == "tool_calling":
            self.agent = ToolCallingAgent(
                tools=tools or [],
                model=self.model,
                max_steps=max_steps,
                instructions=role,
                verbosity_level=verbosity_level,
            )
            logger.info(f"Created ToolCallingAgent: {self.name} ({model_provider})")
        elif agent_type == "code":
            self.agent = CodeAgent(
                tools=tools or [],
                model=self.model,
                max_steps=max_steps,
                verbosity_level=verbosity_level,
                instructions=role,
                executor_type=executor_type,
            )
            logger.info(
                f"Created CodeAgent: {self.name} ({model_provider}) "
                f"with {executor_type} executor"
            )

    def _create_model(self, provider: str, config: Dict[str, Any]) -> LiteLLMModel:
        """
        Create LiteLLM model instance based on provider.

        Args:
            provider: LLM provider name
            config: Model configuration dict (may contain ${VAR} placeholders)

        Returns:
            LiteLLMModel instance
        """
        model_id = config.get("model")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)

        logger.debug(
            f"Creating LiteLLM model - provider: {provider}, "
            f"model: {model_id}, temp: {temperature}, max_tokens: {max_tokens}"
        )

        # Handle provider-specific configuration
        if provider == "ollama" or provider == "lmstudio":
            # Local models need custom_llm_provider
            base_url = config.get("base_url", "http://localhost:11434")
            # Resolve env vars at point-of-use (base_url might have tokens)
            base_url = ConfigManager.resolve_env_var(base_url)
            return LiteLLMModel(
                model_id=f"ollama/{model_id}",
                api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "openai":
            # OpenAI models - resolve API key from env var at point-of-use
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "anthropic":
            # Anthropic models - resolve API key from env var at point-of-use
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            # Generic provider - let LiteLLM figure it out
            logger.warning(f"Unknown provider: {provider}, using generic configuration")
            # Still resolve api_key if present
            api_key = config.get("api_key")
            if api_key:
                api_key = ConfigManager.resolve_env_var(api_key)
                return LiteLLMModel(
                    model_id=model_id,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                return LiteLLMModel(
                    model_id=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

    def run(self, prompt: str) -> str:
        """
        Execute prompt through agent.

        Args:
            prompt: User input

        Returns:
            Agent response string
        """
        logger.debug(f"Running prompt for agent '{self.name}': {prompt[:50]}...")
        result = self.agent.run(prompt)
        return str(result)

    def __repr__(self) -> str:
        """Return string representation of agent."""
        return f"SimpleAgent(name='{self.name}', provider='{self.model_provider}')"
