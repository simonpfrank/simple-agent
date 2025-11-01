"""FlowManager manages orchestrator workflows."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from simple_agent.orchestration.flow_validator import FlowValidator
from simple_agent.orchestration.orchestrator_agent import OrchestratorAgent
from simple_agent.orchestration.agent_tool import AgentTool


class FlowManager:
    """Manages orchestrator flows.

    Loads flow definitions from YAML, validates them, and creates
    orchestrator agents from flow specifications.
    """

    def __init__(self, agent_manager: Any, flows_dir: str = "config/flows") -> None:
        """Initialize FlowManager.

        Args:
            agent_manager: AgentManager instance for resolving agents
            flows_dir: Directory containing flow YAML files
        """
        self.agent_manager = agent_manager
        self.flows_dir = flows_dir
        self.flows: Dict[str, Dict[str, Any]] = {}
        self.validator = FlowValidator()

    def load_flow(self, flow_name: str) -> Dict[str, Any]:
        """Load flow definition from YAML.

        Args:
            flow_name: Name of flow (without .yaml extension)

        Returns:
            Flow definition dict

        Raises:
            FileNotFoundError: If flow file not found
        """
        # Return cached flow if available
        if flow_name in self.flows:
            return self.flows[flow_name]

        # Load from file
        flow_path = Path(self.flows_dir) / f"{flow_name}.yaml"
        if not flow_path.exists():
            raise FileNotFoundError(f"Flow file not found: {flow_path}")

        with open(flow_path, "r") as f:
            flow_def = yaml.safe_load(f)

        # Cache the flow
        self.flows[flow_name] = flow_def

        return flow_def

    def validate_flow(self, flow_def: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate flow definition.

        Args:
            flow_def: Flow definition to validate

        Returns:
            Tuple of (is_valid: bool, errors: list[str])
        """
        return self.validator.validate(flow_def)

    def list_flows(self) -> List[str]:
        """List available flows.

        Returns:
            List of flow names (without .yaml extension)
        """
        flows_path = Path(self.flows_dir)
        if not flows_path.exists():
            return []

        flow_files = flows_path.glob("*.yaml")
        return [f.stem for f in flow_files]

    def create_orchestrator(self, flow_def: Dict[str, Any]) -> OrchestratorAgent:
        """Create orchestrator agent from flow definition.

        Args:
            flow_def: Flow definition dict

        Returns:
            OrchestratorAgent instance

        Raises:
            ValueError: If flow validation fails
        """
        # Validate flow first
        is_valid, errors = self.validate_flow(flow_def)
        if not is_valid:
            raise ValueError(f"Invalid flow: {', '.join(errors)}")

        # Get orchestrator config
        orch_config = flow_def["orchestrator"]

        # Create sub-agents as AgentTools
        sub_agents: Dict[str, AgentTool] = {}
        for sub_agent_def in flow_def.get("sub_agents", []):
            agent_name = sub_agent_def["name"]

            # Load the agent from config
            agent = self.agent_manager.load_agent_from_yaml(sub_agent_def["config"])

            # Wrap as AgentTool
            agent_tool = AgentTool(
                name=agent_name,
                agent=agent,
                description=sub_agent_def["description"]
            )
            sub_agents[agent_name] = agent_tool

        # Get model config from orchestrator
        model_config = orch_config.get("model", {})
        if isinstance(model_config, dict) and not model_config:
            # Empty model config, use defaults
            model_config = {"model": "gpt-4o-mini", "temperature": 0.7}

        # Create orchestrator agent
        orchestrator = OrchestratorAgent(
            name=orch_config.get("name", "orchestrator"),
            role=orch_config.get("role", "Orchestrate workflow"),
            model_provider=model_config.get("provider", "openai"),
            model_config=model_config,
            sub_agents=sub_agents,
            verbosity=orch_config.get("settings", {}).get("verbosity", 1),
            max_steps=orch_config.get("settings", {}).get("max_steps", 15)
        )

        return orchestrator
