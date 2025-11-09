"""
AgentManager - Manages agent lifecycle.

Handles creating, storing, retrieving, and running agents.
Provides separation between business logic and CLI/REPL interface.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import yaml

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

    def create_agent(
        self,
        name: str,
        provider: Optional[str] = None,
        role: Optional[str] = None,
        tools: Optional[List[str]] = None,
        user_prompt_template: Optional[str] = None,
        token_budget: Optional[int] = None,
        token_warning_threshold: Optional[int] = None,
    ) -> SimpleAgent:
        """
        Create and register a new agent.

        Args:
            name: Agent identifier
            provider: LLM provider (defaults to config)
            role: Agent role/persona (defaults to config)
            tools: List of tool names to attach to agent
            user_prompt_template: Optional template to wrap user input. Use {user_input} placeholder.
            token_budget: Hard limit on input prompt size
            token_warning_threshold: Soft warning threshold before token_budget

        Returns:
            Created SimpleAgent instance
        """
        logger.debug(
            f"Creating agent '{name}' - provider: {provider}, "
            f"role: {role}, tools: {tools}"
        )

        # Get defaults from config if not specified
        provider = provider or self.config.get("llm", {}).get("provider")

        # Get role from config default if not specified
        if not role:
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
            tools=tool_objects if tool_objects else None,
            verbosity=verbosity,
            max_steps=max_steps,
            agent_type=agent_type,
            executor_type=executor_type,
            debug_enabled=debug_enabled,
            user_prompt_template=user_prompt_template,
            token_budget=token_budget,
            token_warning_threshold=token_warning_threshold,
        )

        # Register
        self.agents[name] = agent
        logger.info(f"Agent '{name}' created and registered (provider={provider})")

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
            logger.error(f"Agent '{name}' not loaded. Available: {available}")
            raise KeyError(f"Agent '{name}' not loaded. Available: {available}")
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
        logger.debug(
            f"Running agent '{name}' with prompt: {prompt[:50]}... (reset={reset})"
        )

        # Store prompt for inspection
        self.last_prompt = prompt
        self.last_agent = name

        result = agent.run(prompt, reset=reset)

        # Store response for inspection (convert to string)
        self.last_response = str(result)

        logger.debug(f"Agent '{name}' (provider={agent.model_provider}) completed - result length: {len(str(result))}")
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
                provider = agent_config.get("provider")
                tools = agent_config.get("tools")
                token_budget = agent_config.get("token_budget")
                token_warning_threshold = agent_config.get("token_warning_threshold")

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
                        tools=tools,
                        token_budget=token_budget,
                        token_warning_threshold=token_warning_threshold,
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

        # Check for duplicates
        if tool_name in [t.name for t in agent.tools]:
            logger.warning(
                f"Tool '{tool_name}' already exists on agent '{agent_name}', skipping"
            )
            return

        # Add to agent's tools list
        agent.tools.append(tool)

        # Update underlying SmolAgents agent tools
        # IMPORTANT: Add to dict instead of replacing to preserve built-in tools like final_answer
        agent.agent.tools[tool.name] = tool

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
        # IMPORTANT: Delete from dict instead of replacing to preserve built-in tools like final_answer
        if tool_name in agent.agent.tools:
            del agent.agent.tools[tool_name]

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

    def load_agent_from_yaml(self, yaml_path: str) -> SimpleAgent:
        """
        Load agent from YAML file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Created SimpleAgent instance

        Raises:
            FileNotFoundError: If YAML file not found
            yaml.YAMLError: If YAML is invalid
            ValueError: If required fields missing
        """
        logger.debug(f"Loading agent from YAML: {yaml_path}")

        # Check file exists
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Agent YAML file not found: {yaml_path}")

        # Load YAML
        with open(yaml_path, "r") as f:
            agent_data = yaml.safe_load(f)

        # Validate required field: name
        if not agent_data or "name" not in agent_data:
            raise ValueError("Agent YAML must contain 'name' field")

        name = agent_data["name"]

        # Extract fields with defaults
        role = agent_data.get("role")
        tools = agent_data.get("tools", [])
        user_prompt_template = agent_data.get("user_prompt_template")

        # Extract model settings (optional, will use config defaults)
        model_section = agent_data.get("model", {})
        provider = model_section.get("provider")

        # Extract agent settings (optional, will use config defaults)
        settings_section = agent_data.get("settings", {})

        # If model settings provided, merge with config
        if model_section and provider:
            # Get base config for provider
            provider_config = self.config.get("llm", {}).get(provider, {})

            # Override with YAML values
            for key in ["model", "temperature", "max_tokens"]:
                if key in model_section:
                    provider_config[key] = model_section[key]

            # Temporarily update config
            if "llm" not in self.config:
                self.config["llm"] = {}
            if provider not in self.config["llm"]:
                self.config["llm"][provider] = {}
            self.config["llm"][provider].update(provider_config)

        # If settings provided, merge with config agent defaults
        if settings_section:
            if "agents" not in self.config:
                self.config["agents"] = {}
            if "default" not in self.config["agents"]:
                self.config["agents"]["default"] = {}
            # Override defaults with YAML agent settings
            for key in ["verbosity", "max_steps", "agent_type"]:
                if key in settings_section:
                    self.config["agents"]["default"][key] = settings_section[key]

        # Create agent using existing create_agent logic
        agent = self.create_agent(
            name=name,
            provider=provider,
            role=role,
            tools=tools if tools else None,
            user_prompt_template=user_prompt_template,
        )

        logger.info(f"Loaded agent '{name}' from YAML: {yaml_path}")
        return agent

    def save_agent_to_yaml(self, agent_name: str, yaml_path: str) -> None:
        """
        Save agent to YAML file.

        Args:
            agent_name: Name of agent to save
            yaml_path: Path to save YAML file

        Raises:
            KeyError: If agent not found
        """
        logger.debug(f"Saving agent '{agent_name}' to YAML: {yaml_path}")

        # Get agent
        agent = self.get_agent(agent_name)

        # Build YAML structure
        agent_data = {
            "name": agent.name,
            "agent_type": agent.agent_type,
        }

        # Add role if present
        if agent.role:
            agent_data["role"] = agent.role

        # Add user_prompt_template if present
        if agent.user_prompt_template:
            agent_data["user_prompt_template"] = agent.user_prompt_template

        # Add tools if any
        if agent.tools:
            agent_data["tools"] = [tool.name for tool in agent.tools]

        # Add model settings
        agent_data["model"] = {
            "provider": agent.model_provider,
        }

        # Add metadata
        agent_data["metadata"] = {
            "description": f"Agent '{agent.name}'",
            "version": "1.0.0",
        }

        # Create directory if needed
        os.makedirs(
            os.path.dirname(yaml_path) if os.path.dirname(yaml_path) else ".",
            exist_ok=True,
        )

        # Write YAML
        with open(yaml_path, "w") as f:
            yaml.dump(agent_data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved agent '{agent_name}' to YAML: {yaml_path}")

    def load_agents_from_directory(self, directory: str) -> int:
        """
        Load all agents from YAML files in directory.

        Args:
            directory: Directory path to scan

        Returns:
            Number of agents loaded
        """
        logger.debug(f"Loading agents from directory: {directory}")

        # Check directory exists
        if not os.path.exists(directory):
            logger.warning(f"Agent directory not found: {directory}")
            return 0

        if not os.path.isdir(directory):
            logger.warning(f"Path is not a directory: {directory}")
            return 0

        # Scan for YAML files
        loaded_count = 0
        for filename in os.listdir(directory):
            if not filename.endswith(".yaml") and not filename.endswith(".yml"):
                continue

            yaml_path = os.path.join(directory, filename)

            try:
                self.load_agent_from_yaml(yaml_path)
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to load agent from {filename}: {str(e)}")
                continue

        logger.info(f"Loaded {loaded_count} agents from directory: {directory}")
        return loaded_count
