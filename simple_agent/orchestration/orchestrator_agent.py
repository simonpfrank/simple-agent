"""OrchestratorAgent that coordinates multiple sub-agents."""

from typing import Any, Dict

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.orchestration.agent_tool import AgentTool
from simple_agent.core.agent_result import AgentResult


class OrchestratorAgent:
    """Meta-agent that reasons about agent orchestration.

    Coordinates execution of sub-agents using ReAct iteration at the orchestrator
    level. Each sub-agent also iterates internally (ReAct at sub-agent level).

    Attributes:
        name: Orchestrator agent name
        role: System prompt describing the orchestrator's role
        model_provider: LLM provider (e.g., "openai")
        model_config: Model configuration (model name, temperature, etc.)
        sub_agents: Dict of sub-agents as AgentTools
        agent: Internal SimpleAgent that orchestrates sub-agents
    """

    def __init__(
        self,
        name: str,
        role: str,
        model_provider: str,
        model_config: Dict[str, Any],
        sub_agents: Dict[str, AgentTool],
        verbosity: int = 1,
        max_steps: int = 15
    ) -> None:
        """Initialize OrchestratorAgent.

        Args:
            name: Name of the orchestrator agent
            role: System prompt for the orchestrator
            model_provider: LLM provider (e.g., "openai")
            model_config: Model configuration dict
            sub_agents: Dict mapping agent names to AgentTools
            verbosity: Verbosity level for reasoning (0-2)
            max_steps: Maximum ReAct iterations for orchestrator
        """
        self.name = name
        self.role = role
        self.model_provider = model_provider
        self.model_config = model_config
        self.sub_agents = sub_agents
        self.verbosity = verbosity
        self.max_steps = max_steps

        # Create internal SimpleAgent with sub-agents as tools
        self.agent = SimpleAgent(
            name=name,
            role=role,
            model_provider=model_provider,
            model_config=model_config,
            tools=list(sub_agents.values()),
            verbosity=verbosity,
            max_steps=max_steps
        )

    def run(self, prompt: str) -> AgentResult:
        """Run orchestrator - it reasons about which agents to call.

        The orchestrator uses ReAct iteration to:
        1. Analyze the request
        2. Decide which sub-agents to call
        3. Evaluate outputs
        4. Route to next agent or refine based on results
        5. Synthesize final output

        Args:
            prompt: User's request for orchestrator to handle

        Returns:
            Final response from orchestrator after coordinating sub-agents.
        """
        return self.agent.run(prompt)

    def __repr__(self) -> str:
        """Return readable representation."""
        return f"OrchestratorAgent(name='{self.name}', sub_agents={len(self.sub_agents)})"
