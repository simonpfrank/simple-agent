"""AgentTool wrapper that exposes a SimpleAgent as a callable tool for orchestrators."""

import logging
import time
from typing import Any, Dict

from smolagents import Tool

logger = logging.getLogger(__name__)


class AgentTool(Tool):
    """Wrapper that exposes an agent as a callable tool.

    Makes a SimpleAgent callable from within another agent's tool set,
    enabling multi-level agent orchestration with ReAct iteration at both levels.

    Inherits from SmolAgents Tool to be compatible with ToolCallingAgent.

    Attributes:
        agent: The SimpleAgent instance being wrapped
        description: Tool description for the orchestrator's understanding
        call_history: List of all calls made to this tool
    """

    def __init__(
        self,
        name: str,
        agent: Any,
        description: str,
        expected_output_format: str = "text"
    ) -> None:
        """Initialize AgentTool wrapper.

        Args:
            name: Tool name (used by orchestrator)
            agent: SimpleAgent instance to wrap
            description: Tool description for orchestrator's understanding
            expected_output_format: Expected output format ("text" or "structured")
        """
        # Set SmolAgents Tool required attributes before parent init
        self.name = name
        self.description = description
        self.inputs = {"prompt": {"type": "string", "description": "Input prompt for the agent"}}
        self.output_type = "string"

        # Initialize parent Tool class
        super().__init__()

        self.agent = agent
        self.expected_output_format = expected_output_format
        self.call_history: list[Dict[str, Any]] = []

    def forward(self, prompt: str) -> str:
        """Execute agent and return result as string.

        This is the required SmolAgents Tool method.

        Args:
            prompt: Input prompt for the agent

        Returns:
            Agent's response as a string
        """
        start_time = time.time()
        logger.debug(f"[TOOL] AgentTool.forward() - agent={self.agent.name}, prompt_len={len(prompt)}")

        try:
            # Execute wrapped agent
            output = self.agent.run(prompt)
            execution_time = time.time() - start_time
            output_str = str(output) if output else ""
            output_len = len(output_str)

            # Build result dict for history
            result = {
                "status": "success",
                "output": output,
                "metadata": {
                    "agent_name": self.agent.name,
                    "execution_time": execution_time,
                    "tool_name": self.name,
                }
            }

            # Track in history
            self.call_history.append(result)

            logger.info(f"[TOOL] AgentTool.forward() completed - agent={self.agent.name}, output_len={output_len}, time={execution_time:.2f}s")
            # Return as string for SmolAgents
            return output

        except Exception as e:
            # Handle failure gracefully
            execution_time = time.time() - start_time

            error_msg = f"Error from {self.agent.name}: {str(e)}"

            result = {
                "status": "failure",
                "output": error_msg,
                "metadata": {
                    "agent_name": self.agent.name,
                    "execution_time": execution_time,
                    "tool_name": self.name,
                },
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                }
            }

            # Track in history
            self.call_history.append(result)

            logger.error(f"[TOOL] AgentTool.forward() failed - agent={self.agent.name}, {type(e).__name__}: {str(e)}, time={execution_time:.2f}s")
            # Return error as string for SmolAgents
            return error_msg

    def __repr__(self) -> str:
        """Return readable representation."""
        return f"AgentTool(name='{self.name}', agent='{self.agent.name}')"
