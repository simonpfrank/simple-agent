"""
AgentManager - Manages agent lifecycle.

Handles creating, storing, retrieving, and running agents.
Provides separation between business logic and CLI/REPL interface.
"""

import logging
from typing import Any, Dict, List, Optional

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

        # Track last interaction for inspection commands
        self.last_prompt: Optional[str] = None
        self.last_response: Optional[str] = None
        self.last_agent: Optional[str] = None

        # Tool manager (set by app.py after initialization)
        self.tool_manager = None

        logger.info("AgentManager initialized")

        # Auto-load agents from config
        self._load_agents_from_config()

    def create_agent(
        self,
        name: str,
        provider: Optional[str] = None,
        role: Optional[str] = None,
        template: Optional[str] = None,
        tools: Optional[List[str]] = None,
    ) -> SimpleAgent:
        """
        Create and register a new agent.

        Args:
            name: Agent identifier
            provider: LLM provider (defaults to config)
            role: Agent role/persona (defaults to config)
            template: Template name to load from config/prompts/
            tools: List of tool names to attach to agent

        Returns:
            Created SimpleAgent instance
        """
        logger.debug(
            f"Creating agent '{name}' - provider: {provider}, "
            f"role: {role}, template: {template}, tools: {tools}"
        )

        # Get defaults from config if not specified
        provider = provider or self.config.get("llm", {}).get("provider")

        # Get role from config default if not specified and no template
        if not role and not template:
            role = self.config.get("agents", {}).get("default", {}).get("role")

        # Get model config for provider
        model_config = self.config.get("llm", {}).get(provider, {})

        # Get agent settings from config
        agent_defaults = self.config.get("agents", {}).get("default", {})
        verbosity = agent_defaults.get("verbosity", 1)
        max_steps = agent_defaults.get("max_steps", 10)
        agent_type = agent_defaults.get("agent_type", "tool_calling")
        executor_type = agent_defaults.get("executor_type", "docker")

        # Get debug mode from config
        debug_enabled = self.config.get("debug", {}).get("enabled", False)

        # Convert tool names to tool objects
        tool_objects = []
        if tools and self.tool_manager:
            for tool_name in tools:
                tool_obj = self.tool_manager.get_tool(tool_name)
                tool_objects.append(tool_obj)
            logger.debug(f"Loaded {len(tool_objects)} tools for agent '{name}'")

        # Create agent
        agent = SimpleAgent(
            name=name,
            model_provider=provider,
            model_config=model_config,
            role=role,
            template=template,
            tools=tool_objects if tool_objects else None,
            verbosity=verbosity,
            max_steps=max_steps,
            agent_type=agent_type,
            executor_type=executor_type,
            debug_enabled=debug_enabled,
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

    def run_agent(self, name: str, prompt: str, reset: bool = True) -> str:
        """
        Run prompt through specified agent.

        Args:
            name: Agent identifier
            prompt: User input
            reset: If True, reset memory before running. If False, preserve memory
                   for multi-turn conversations. Default True for backwards compatibility.

        Returns:
            Agent response string

        Raises:
            KeyError: If agent doesn't exist
        """
        agent = self.get_agent(name)
        logger.debug(f"Running agent '{name}' with prompt: {prompt[:50]}... (reset={reset})")

        # Store prompt for inspection
        self.last_prompt = prompt
        self.last_agent = name

        result = agent.run(prompt, reset=reset)

        # Store response for inspection (convert to string)
        self.last_response = str(result)

        logger.debug(f"Agent '{name}' completed - result length: {len(str(result))}")
        return result

    def _load_agents_from_config(self) -> None:
        """
        Load agents from config.yaml agents section.

        Creates agents for each entry under 'agents:' in config.
        Uses agent name from config key, and config values for settings.
        """
        agents_config = self.config.get("agents", {})
        logger.debug(f"Auto-loading agents from config: {list(agents_config.keys())}")

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

    def add_tool_to_agent(self, agent_name: str, tool_name: str) -> None:
        """
        Add a tool to an existing agent.

        Args:
            agent_name: Name of agent to modify
            tool_name: Name of tool to add

        Raises:
            KeyError: If agent or tool not found
        """
        agent = self.get_agent(agent_name)

        if not self.tool_manager:
            raise RuntimeError("Tool manager not initialized")

        tool = self.tool_manager.get_tool(tool_name)

        # Add to agent's tools list
        agent.tools.append(tool)

        # Update underlying SmolAgents agent tools
        # SmolAgents stores tools as dict, so we need to update it properly
        agent.agent.tools = agent.tools.copy()

        logger.info(f"Added tool '{tool_name}' to agent '{agent_name}'")

    def remove_tool_from_agent(self, agent_name: str, tool_name: str) -> None:
        """
        Remove a tool from an existing agent.

        Args:
            agent_name: Name of agent to modify
            tool_name: Name of tool to remove

        Raises:
            KeyError: If agent not found
        """
        agent = self.get_agent(agent_name)

        # Remove from agent's tools list (by name match)
        agent.tools = [t for t in agent.tools if t.name != tool_name]

        # Update underlying SmolAgents agent tools
        agent.agent.tools = agent.tools.copy()

        logger.info(f"Removed tool '{tool_name}' from agent '{agent_name}'")

    def get_agent_tools(self, agent_name: str) -> List[str]:
        """
        Get list of tool names for an agent.

        Args:
            agent_name: Name of agent

        Returns:
            List of tool name strings

        Raises:
            KeyError: If agent not found
        """
        agent = self.get_agent(agent_name)
        return [tool.name for tool in agent.tools]
