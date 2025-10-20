"""
AgentManager - Manages agent lifecycle.

Handles creating, storing, retrieving, and running agents.
Provides separation between business logic and CLI/REPL interface.
"""

import logging
from typing import Any, Dict, Optional

from simple_agent.agents.simple_agent import SimpleAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages agent lifecycle (create, store, retrieve, run)."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize agent manager.

        Args:
            config: Application configuration dict
        """
        self.config = config
        self.agents: Dict[str, SimpleAgent] = {}
        logger.info("AgentManager initialized")

        # Auto-load agents from config
        self._load_agents_from_config()

    def create_agent(
        self,
        name: str,
        provider: Optional[str] = None,
        role: Optional[str] = None,
        template: Optional[str] = None,
    ) -> SimpleAgent:
        """
        Create and register a new agent.

        Args:
            name: Agent identifier
            provider: LLM provider (defaults to config)
            role: Agent role/persona (defaults to config)
            template: Template name to load from config/prompts/

        Returns:
            Created SimpleAgent instance
        """
        # Get defaults from config if not specified
        provider = provider or self.config.get("llm", {}).get("provider")

        # Get role from config default if not specified and no template
        if not role and not template:
            role = self.config.get("agents", {}).get("default", {}).get("role")

        # Get model config for provider
        model_config = self.config.get("llm", {}).get(provider, {})

        # Get verbosity and max_steps from config
        verbosity = self.config.get("agents", {}).get("default", {}).get("verbosity", 1)
        max_steps = (
            self.config.get("agents", {}).get("default", {}).get("max_steps", 10)
        )

        # Create agent
        agent = SimpleAgent(
            name=name,
            model_provider=provider,
            model_config=model_config,
            role=role,
            template=template,
            verbosity=verbosity,
            max_steps=max_steps,
        )

        # Register
        self.agents[name] = agent
        logger.info(f"Agent '{name}' created and registered")

        return agent

    def get_agent(self, name: str) -> SimpleAgent:
        """
        Retrieve agent by name.

        Args:
            name: Agent identifier

        Returns:
            SimpleAgent instance

        Raises:
            KeyError: If agent doesn't exist
        """
        if name not in self.agents:
            available = list(self.agents.keys())
            logger.error(f"Agent '{name}' not found. Available: {available}")
            raise KeyError(f"Agent '{name}' not found. Available: {available}")
        return self.agents[name]

    def list_agents(self) -> list[str]:
        """
        Return list of registered agent names.

        Returns:
            List of agent name strings
        """
        return list(self.agents.keys())

    def run_agent(self, name: str, prompt: str) -> str:
        """
        Run prompt through specified agent.

        Args:
            name: Agent identifier
            prompt: User input

        Returns:
            Agent response string

        Raises:
            KeyError: If agent doesn't exist
        """
        agent = self.get_agent(name)
        logger.debug(f"Running agent '{name}' with prompt: {prompt[:50]}...")
        result = agent.run(prompt)
        return result

    def _load_agents_from_config(self) -> None:
        """
        Load agents from config.yaml agents section.

        Creates agents for each entry under 'agents:' in config.
        Uses agent name from config key, and config values for settings.
        """
        agents_config = self.config.get("agents", {})

        for agent_name, agent_config in agents_config.items():
            if isinstance(agent_config, dict):
                # Extract settings from config
                role = agent_config.get("role")
                template = agent_config.get("template")
                provider = agent_config.get("provider")

                # Skip if agent_name already exists (don't overwrite)
                if agent_name in self.agents:
                    logger.debug(
                        f"Agent '{agent_name}' already exists, skipping config load"
                    )
                    continue

                try:
                    # Create agent using the config settings
                    self.create_agent(
                        name=agent_name,
                        provider=provider,
                        role=role,
                        template=template,
                    )
                    logger.info(f"Auto-loaded agent '{agent_name}' from config")
                except Exception as e:
                    logger.error(f"Failed to auto-load agent '{agent_name}': {str(e)}")
