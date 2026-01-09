"""Agent execution result with token tracking and cost information."""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from decimal import Decimal

from simple_agent.tools.helpers.token_tracker import TokenStats


@dataclass
class AgentResult:
    """Result of an agent execution with token and cost information.

    Provides backward compatibility by supporting both string and dict access.
    Includes error tracking to indicate if execution was halted by an error.
    """

    response: Any  # The actual response from the agent
    input_tokens: int = 0  # Tokens in the input prompt
    output_tokens: int = 0  # Tokens in the LLM response
    total_tokens: int = 0  # Total tokens (input + output)
    cost: Decimal = Decimal("0")  # Cost in USD
    model: str = "unknown"  # Model name used
    error: Optional[str] = None  # Error message if execution failed
    error_type: Optional[str] = None  # Error class name (e.g., "ValueError")

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
            Dict with response, token stats, and error info if applicable
        """
        result = {
            "response": str(self.response),
            "tokens": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
                "cost": float(self.cost),
                "model": self.model,
            },
        }

        # Add error information if an error occurred
        if self.error is not None or self.error_type is not None:
            result["error"] = {
                "error_type": self.error_type,
                "error_message": self.error,
                "execution_halted": True,
            }

        return result

    @classmethod
    def from_response(
        cls,
        response: Any,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: Decimal = Decimal("0"),
        model: str = "unknown",
        error: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> "AgentResult":
        """Create AgentResult from response and token info.

        Args:
            response: The actual response
            input_tokens: Tokens in input
            output_tokens: Tokens in output
            cost: Cost in USD
            model: Model name
            error: Error message if execution failed
            error_type: Error class name (e.g., "ValueError")

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
            error=error,
            error_type=error_type,
        )

    @classmethod
    def from_token_stats(
        cls,
        response: Any,
        stats: TokenStats,
        error: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> "AgentResult":
        """Create AgentResult from TokenStats.

        Args:
            response: The actual response
            stats: TokenStats object
            error: Error message if execution failed
            error_type: Error class name (e.g., "ValueError")

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
            error=error,
            error_type=error_type,
        )
