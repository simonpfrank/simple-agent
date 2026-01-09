"""Agent mode handler for cli_repl_kit integration.

This module provides the agent callback function that routes free text
input (without /) to the active agent in simple_agent.
"""

import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


def create_agent_callback(
    context_factory: Callable[[], Dict[str, Any]]
) -> Callable[[str], str]:
    """Create an agent callback function for cli_repl_kit.

    The callback routes free text input to the active agent and returns
    the response.

    Args:
        context_factory: Function that returns the context dict with managers

    Returns:
        Callback function that takes user text and returns agent response
    """

    def agent_callback(text: str) -> str:
        """Route user text to the active agent.

        Args:
            text: User's free text input (without / prefix)

        Returns:
            Agent's response as a string
        """
        context = context_factory()
        agent_manager = context.get("agent_manager")

        if not agent_manager:
            return "Error: Agent manager not initialized"

        # Get active agent
        active_agent = agent_manager.get_active_agent()
        if not active_agent:
            return (
                "No active agent. Use /agent load <name> to load an agent first.\n"
                "Available agents: " + ", ".join(agent_manager.list_agents())
            )

        # Log the interaction
        agent_name = getattr(active_agent, "name", "unknown")
        logger.info(f"[AGENT_MODE] Sending to agent '{agent_name}': {text[:50]}...")

        try:
            # Run the agent with the user's text
            response = active_agent.run(text)

            # Store last prompt/response for inspection commands
            agent_manager.last_prompt = text
            agent_manager.last_response = response

            # Convert AgentResult to string for display
            return str(response)

        except Exception as e:
            logger.error(f"[AGENT_MODE] Error from agent: {e}", exc_info=True)
            return f"Agent error: {e}"

    return agent_callback
