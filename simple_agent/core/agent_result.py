"""Agent execution result with token tracking and cost information."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
from decimal import Decimal

from simple_agent.tools.helpers.token_tracker import TokenStats


@dataclass
class AgentResult:
    """Result of an agent execution with token and cost information.

    Provides backward compatibility by supporting both string and dict access.
    """

    response: Any  # The actual response from the agent
    input_tokens: int = 0  # Tokens in the input prompt
    output_tokens: int = 0  # Tokens in the LLM response
    total_tokens: int = 0  # Total tokens (input + output)
    cost: Decimal = Decimal("0")  # Cost in USD
    model: str = "unknown"  # Model name used

    def __str__(self) -> str:
        """Return response as string for backward compatibility."""
        return str(self.response)

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"AgentResult(response={self.response[:50]}..., "
            f"tokens={self.total_tokens}, cost=${float(self.cost):.6f})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict with response and token stats
        """
        return {
            "response": str(self.response),
            "tokens": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
                "cost": float(self.cost),
                "model": self.model,
            },
        }

    @classmethod
    def from_response(
        cls,
        response: Any,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: Decimal = Decimal("0"),
        model: str = "unknown",
    ) -> "AgentResult":
        """Create AgentResult from response and token info.

        Args:
            response: The actual response
            input_tokens: Tokens in input
            output_tokens: Tokens in output
            cost: Cost in USD
            model: Model name

        Returns:
            AgentResult instance
        """
        total_tokens = input_tokens + output_tokens
        return cls(
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            model=model,
        )

    @classmethod
    def from_token_stats(
        cls, response: Any, stats: TokenStats
    ) -> "AgentResult":
        """Create AgentResult from TokenStats.

        Args:
            response: The actual response
            stats: TokenStats object

        Returns:
            AgentResult instance
        """
        return cls(
            response=response,
            input_tokens=stats.input_tokens,
            output_tokens=stats.output_tokens,
            total_tokens=stats.total_tokens,
            cost=stats.cost,
            model=stats.model,
        )
