"""Token tracking and cost calculation for agents and flows."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from decimal import Decimal


@dataclass
class TokenStats:
    """Statistics for a single agent execution."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = field(init=False)
    cost: Decimal = Decimal("0")
    model: str = "unknown"
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        """Calculate total tokens after initialization."""
        self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class StepTokenStats:
    """Token statistics for a single step in a flow."""

    agent_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = field(init=False)
    cost: Decimal = Decimal("0")
    model: str = "unknown"

    def __post_init__(self) -> None:
        """Calculate total tokens after initialization."""
        self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class FlowTokenStats:
    """Aggregated token statistics for a complete flow."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = field(init=False)
    total_cost: Decimal = Decimal("0")
    steps: List[StepTokenStats] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Calculate totals after initialization."""
        self.total_tokens = self.total_input_tokens + self.total_output_tokens

    def add_step(self, step: StepTokenStats) -> None:
        """Add a step's statistics to the flow totals."""
        self.steps.append(step)
        self.total_input_tokens += step.input_tokens
        self.total_output_tokens += step.output_tokens
        self.total_tokens = self.total_input_tokens + self.total_output_tokens
        self.total_cost += step.cost

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost": float(self.total_cost),
            "steps": [
                {
                    "agent": step.agent_name,
                    "input_tokens": step.input_tokens,
                    "output_tokens": step.output_tokens,
                    "total_tokens": step.total_tokens,
                    "cost": float(step.cost),
                    "model": step.model,
                }
                for step in self.steps
            ],
        }


class TokenTracker:
    """Track token usage and calculate costs during execution."""

    def __init__(self) -> None:
        """Initialize token tracker."""
        self.stats: List[TokenStats] = []
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost: Decimal = Decimal("0")

    def add_execution(
        self,
        input_tokens: int,
        output_tokens: int = 0,
        cost: Decimal = Decimal("0"),
        model: str = "unknown",
    ) -> None:
        """Record a single execution's token usage.

        Args:
            input_tokens: Tokens in the input prompt
            output_tokens: Tokens in the LLM response
            cost: Calculated cost in USD
            model: Model name (e.g., "gpt-4o-mini")
        """
        stats = TokenStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            model=model,
        )
        self.stats.append(stats)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

    def get_stats(self) -> TokenStats:
        """Get aggregated statistics.

        Returns:
            TokenStats with totals across all executions
        """
        return TokenStats(
            input_tokens=self.total_input_tokens,
            output_tokens=self.total_output_tokens,
            cost=self.total_cost,
            model="mixed" if len(set(s.model for s in self.stats)) > 1 else (self.stats[0].model if self.stats else "unknown"),
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict with token counts and cost
        """
        stats = self.get_stats()
        return {
            "input_tokens": stats.input_tokens,
            "output_tokens": stats.output_tokens,
            "total_tokens": stats.total_tokens,
            "cost": float(stats.cost),
            "model": stats.model,
        }

    def reset(self) -> None:
        """Reset all statistics."""
        self.stats = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = Decimal("0")
