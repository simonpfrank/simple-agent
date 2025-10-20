"""
SimpleAgent - Thin wrapper around SmolAgents CodeAgent.

Provides a simplified interface for creating and running agents with LiteLLM support.
"""

import logging
from typing import Any, Dict, Optional

from smolagents import CodeAgent, LiteLLMModel

from simple_agent.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class SimpleAgent:
    """Thin wrapper around SmolAgents CodeAgent."""

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
            verbosity: 0=quiet, 1=normal, 2=verbose
            max_steps: Max tool call iterations
        """
        self.name = name
        self.model_provider = model_provider

        # Load template if specified and no explicit role
        if template and not role:
            template_data = ConfigManager.load_prompt_template(template)
            role = template_data.get("system", "")

        self.role = role

        # Create LiteLLM model instance
        self.model = self._create_model(model_provider, model_config)

        # Create SmolAgents CodeAgent
        self.agent = CodeAgent(
            tools=tools or [],
            model=self.model,
            max_steps=max_steps,
            verbosity_level=verbosity,
            instructions=role,
        )

        logger.info(f"Created agent: {self.name} ({model_provider})")

    def _create_model(self, provider: str, config: Dict[str, Any]) -> LiteLLMModel:
        """
        Create LiteLLM model instance based on provider.

        Args:
            provider: LLM provider name
            config: Model configuration dict

        Returns:
            LiteLLMModel instance
        """
        model_id = config.get("model")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)

        # Handle provider-specific configuration
        if provider == "ollama" or provider == "lmstudio":
            # Local models need custom_llm_provider
            base_url = config.get("base_url", "http://localhost:11434")
            return LiteLLMModel(
                model_id=f"ollama/{model_id}",
                api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "openai":
            # OpenAI models
            api_key = config.get("api_key")
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "anthropic":
            # Anthropic models
            api_key = config.get("api_key")
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            # Generic provider - let LiteLLM figure it out
            logger.warning(f"Unknown provider: {provider}, using generic configuration")
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
